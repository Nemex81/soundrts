"""Tests for UI-MASTER-05 round.

Coverage matrix (mandatory minimum per round task):
  - T10-TOOLTIP-THROTTLE: empty-cell tooltip is debounced; identical
    cells re-fed within the window stay hidden, distinct cells reset
    the timer.
  - T10-CANCEL-SERVER: clicking an ACTIVITY row dispatches the proper
    server keyword via interface.send_order (training/research/build),
    falls back to client-only pop for unknown kinds, and removes the
    row from the per-frame mappings for immediate UI feedback.
  - T10-MOVE-INDICATOR: flash_move_target stores the click anchor and
    _draw_move_flash decays after the configured duration.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

import time

import pygame
import pytest

from soundrts.clientgamehud import HudPanel


# ---------------------------------------------------------------------------
# Shared fixtures.
# ---------------------------------------------------------------------------


def _make_interface(send_order=None):
    iface = MagicMock()
    iface.display_is_active = True
    iface.is_paused = False
    iface.resources = [100, 200]
    iface.used_food = 0
    iface.available_food = 10
    iface.last_virtual_time = 0
    iface.speed = 1.0
    iface._get_relative_speed = lambda: 1.0
    iface.group = []
    iface.dobjets = {}
    iface.player = SimpleNamespace(name="Tester", race=None, units=[])
    if send_order is None:
        send_order = MagicMock()
    iface.send_order = send_order
    return iface


def _make_hud(send_order=None):
    return HudPanel(_make_interface(send_order=send_order))


# ---------------------------------------------------------------------------
# T10-TOOLTIP-THROTTLE
# ---------------------------------------------------------------------------


def test_empty_cell_tooltip_debounced_first_sample_stays_hidden():
    hud = _make_hud()
    sq = SimpleNamespace(col=2, row=4)
    hud.set_map_hover(None, (50, 50), square=sq)
    # First sample: timer started, tooltip suppressed.
    assert hud._tooltip_text == ""
    assert hud._tooltip_pos is None
    assert hud._empty_cell_hover_square is sq


def test_empty_cell_tooltip_appears_after_debounce_window():
    hud = _make_hud()
    sq = SimpleNamespace(col=2, row=4)
    hud.set_map_hover(None, (50, 50), square=sq)
    # Rewind the start time so the next sample is past the window.
    hud._empty_cell_hover_start -= hud._empty_cell_tooltip_delay + 0.01
    same = SimpleNamespace(col=2, row=4)  # new object, same (col,row)
    hud.set_map_hover(None, (50, 50), square=same)
    assert hud._tooltip_text != ""
    assert "2" in hud._tooltip_text and "4" in hud._tooltip_text


def test_empty_cell_tooltip_resets_when_cell_changes():
    hud = _make_hud()
    sq1 = SimpleNamespace(col=2, row=4)
    sq2 = SimpleNamespace(col=3, row=4)
    hud.set_map_hover(None, (50, 50), square=sq1)
    t1 = hud._empty_cell_hover_start
    hud.set_map_hover(None, (60, 50), square=sq2)
    # Cell changed -> tooltip stays hidden and timer reset on new cell.
    assert hud._tooltip_text == ""
    assert hud._empty_cell_hover_square is sq2
    assert hud._empty_cell_hover_start >= t1


def test_empty_cell_state_cleared_on_full_clear():
    hud = _make_hud()
    sq = SimpleNamespace(col=2, row=4)
    hud.set_map_hover(None, (50, 50), square=sq)
    hud.set_map_hover(None, None)
    assert hud._empty_cell_hover_square is None
    assert hud._empty_cell_hover_start == 0.0


# ---------------------------------------------------------------------------
# T10-CANCEL-SERVER
# ---------------------------------------------------------------------------


def _make_unit(orders=None):
    return SimpleNamespace(orders=list(orders or [1, 2, 3]))


def test_cancel_training_dispatches_server_keyword():
    send_order = MagicMock()
    hud = _make_hud(send_order=send_order)
    unit = _make_unit()
    hud._cancel_unit_order(unit, "training")
    send_order.assert_called_once_with("cancel_training", None, [])
    # client-only flash reducer still pops the first order.
    assert unit.orders == [2, 3]


def test_cancel_research_dispatches_cancel_upgrading():
    send_order = MagicMock()
    hud = _make_hud(send_order=send_order)
    unit = _make_unit()
    hud._cancel_unit_order(unit, "research")
    send_order.assert_called_once_with("cancel_upgrading", None, [])


def test_cancel_build_dispatches_cancel_building():
    send_order = MagicMock()
    hud = _make_hud(send_order=send_order)
    unit = _make_unit()
    hud._cancel_unit_order(unit, "build")
    send_order.assert_called_once_with("cancel_building", None, [])


def test_cancel_unknown_kind_is_client_only():
    send_order = MagicMock()
    hud = _make_hud(send_order=send_order)
    unit = _make_unit()
    hud._cancel_unit_order(unit, "")
    send_order.assert_not_called()
    assert unit.orders == [2, 3]  # client-only flash still applied


def test_cancel_handler_removes_row_immediately_for_ui_feedback():
    hud = _make_hud()
    unit = _make_unit()
    # Pre-populate as if the activity panel had been rendered.
    hud._panel_rects["activity_row_0"] = pygame.Rect(0, 0, 100, 20)
    hud._activity_row_texts[0] = "[T] orc 40%"
    hud._activity_row_units[0] = unit
    hud._activity_row_kinds[0] = "training"
    hud.activity_visible = True
    event = SimpleNamespace(
        type=pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 10)
    )
    consumed = hud.handle_mouse_event(event)
    assert consumed is True
    # Immediate UI feedback: row erased from the per-frame mappings.
    assert 0 not in hud._activity_row_texts
    assert 0 not in hud._activity_row_units
    assert 0 not in hud._activity_row_kinds


def test_cancel_swallows_send_order_failure():
    send_order = MagicMock(side_effect=RuntimeError("boom"))
    hud = _make_hud(send_order=send_order)
    unit = _make_unit()
    # Must not raise: defensive contract.
    hud._cancel_unit_order(unit, "training")
    # client-only fallback still applied.
    assert unit.orders == [2, 3]


# ---------------------------------------------------------------------------
# T10-MOVE-INDICATOR
# ---------------------------------------------------------------------------


def test_flash_move_target_records_pos_and_timestamp():
    hud = _make_hud()
    sq = SimpleNamespace(col=5, row=8)
    before = time.monotonic()
    hud.flash_move_target(sq, (123, 456))
    assert hud._move_flash_square is sq
    assert hud._move_flash_pos == (123, 456)
    assert hud._move_flash_start >= before


def test_flash_move_target_ignores_none_inputs():
    hud = _make_hud()
    hud.flash_move_target(None, (1, 2))
    assert hud._move_flash_square is None
    assert hud._move_flash_pos is None
    sq = SimpleNamespace(col=1, row=1)
    hud.flash_move_target(sq, None)
    assert hud._move_flash_square is None


def test_move_flash_expires_after_duration():
    hud = _make_hud()
    sq = SimpleNamespace(col=5, row=8)
    hud.flash_move_target(sq, (50, 50))
    # Rewind so the next draw sees the flash as expired.
    hud._move_flash_start -= hud._move_flash_duration + 0.05
    surf = pygame.Surface((200, 200), pygame.SRCALPHA)
    hud._draw_move_flash(surf)
    assert hud._move_flash_square is None
    assert hud._move_flash_pos is None


def test_move_flash_draws_within_window_without_error():
    hud = _make_hud()
    sq = SimpleNamespace(col=5, row=8)
    hud.flash_move_target(sq, (60, 70))
    surf = pygame.Surface((200, 200), pygame.SRCALPHA)
    # Should not raise; should not clear the flash either.
    hud._draw_move_flash(surf)
    assert hud._move_flash_square is sq
    assert hud._move_flash_pos == (60, 70)


# ---------------------------------------------------------------------------
# L10N audit for new keys introduced this round
# ---------------------------------------------------------------------------


def test_no_new_l10n_keys_required_for_round():
    """UI-MASTER-05 introduces no new player-visible strings:
       - T10-TOOLTIP-THROTTLE reuses tooltip_map_empty_cell from
         UI-MASTER-04.
       - T10-CANCEL-SERVER reuses tooltip_activity_cancel_hint and
         tooltip_activity_row_full.
       - T10-MOVE-INDICATOR is a pure visual effect (LEGGE-4 N/A).
    Asserting that the two reused keys are still present in both
    EN and IT style files guards against accidental removal.
    """
    from pathlib import Path

    repo = Path(__file__).resolve().parents[3]
    en = (repo / "res" / "ui" / "style.txt").read_text(encoding="utf-8")
    it = (repo / "res" / "ui-it" / "style.txt").read_text(encoding="utf-8")
    for key in ("tooltip_map_empty_cell", "tooltip_activity_cancel_hint"):
        assert key in en, "missing in EN: " + key
        assert key in it, "missing in IT: " + key
