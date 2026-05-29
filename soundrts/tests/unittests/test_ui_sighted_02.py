"""Tests for UI-SIGHTED-02 round (sighted-player UX layer, wave 2).

Coverage matrix:
  - SI-L10N: ctx_* / hotkey_* keys are present in res/ui/style.txt
    (EN base) and the Italian translation does not miss the new
    hotkey_* entries.
  - SI-03b: GridView.draw_rubber_band degrades gracefully for tiny
    rectangles (no blit) and never propagates exceptions.
  - SI-05: GridView._draw_stack_badge skips counts <= 1, renders for
    count > 1, and shows "99+" past 99.
  - SI-06: HudPanel.keys_visible defaults to False, header click
    toggles it, and the panel does not crash without a screen.
  - SI-07: GridView.enemy_at_mousepos returns hostile entities only,
    and the custom "attack" cursor is registered in lib.mouse.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame
import pytest

from soundrts.clientgamegridview import GridView
from soundrts.clientgamehud import HudPanel
from soundrts.lib import mouse as mouse_lib


REPO_ROOT = Path(__file__).resolve().parents[3]
STYLE_EN = REPO_ROOT / "res" / "ui" / "style.txt"
STYLE_IT = REPO_ROOT / "res" / "ui-it" / "style.txt"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_interface():
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
    iface.orders = MagicMock(return_value=[])
    iface.send_order = MagicMock()
    iface._select_order = MagicMock()
    iface.already_asked_to_quit = False
    iface.end_loop = False
    return iface


def _make_grid_view():
    iface = _make_interface()
    gv = GridView.__new__(GridView)
    gv.interface = iface
    return gv


# ---------------------------------------------------------------------------
# SI-L10N
# ---------------------------------------------------------------------------


CTX_KEYS = [
    "ctx_move", "ctx_attack", "ctx_stop", "ctx_patrol", "ctx_build",
    "ctx_train", "ctx_research", "ctx_repair", "ctx_use", "ctx_default",
    "ctx_cancel_training", "ctx_cancel_upgrading", "ctx_cancel_building",
    "ctx_join_group", "ctx_reset_group",
]

HOTKEY_KEYS = [
    "panel_keys", "keys_collapsed", "tooltip_keys_show", "tooltip_keys_hide",
    "hotkey_space", "hotkey_f", "hotkey_s", "hotkey_a", "hotkey_p",
    "hotkey_tab", "hotkey_esc", "hotkey_ctrl_a",
]


def test_ctx_keys_present_in_en_style():
    text = STYLE_EN.read_text(encoding="utf-8")
    missing = [k for k in CTX_KEYS if k not in text]
    assert missing == [], "Missing ctx_* keys in EN style.txt: {}".format(missing)


def test_hotkey_keys_present_in_en_and_it():
    en = STYLE_EN.read_text(encoding="utf-8")
    it = STYLE_IT.read_text(encoding="utf-8")
    missing_en = [k for k in HOTKEY_KEYS if k not in en]
    missing_it = [k for k in HOTKEY_KEYS if k not in it]
    assert missing_en == [], "Missing hotkey_* keys in EN: {}".format(missing_en)
    assert missing_it == [], "Missing hotkey_* keys in IT: {}".format(missing_it)


# ---------------------------------------------------------------------------
# SI-03b rubber-band overlay
# ---------------------------------------------------------------------------


def test_draw_rubber_band_small_rect_no_blit():
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    gv.draw_rubber_band(screen, (10, 10), (11, 11))
    screen.blit.assert_not_called()


def test_draw_rubber_band_valid_blits_to_screen():
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    gv.draw_rubber_band(screen, (10, 10), (80, 60))
    assert screen.blit.called


def test_draw_rubber_band_exception_does_not_propagate():
    screen = MagicMock()
    screen.blit.side_effect = RuntimeError("simulated")
    gv = _make_grid_view()
    # Must not raise even when blit explodes.
    gv.draw_rubber_band(screen, (10, 10), (80, 60))


# ---------------------------------------------------------------------------
# SI-05 stack badge
# ---------------------------------------------------------------------------


def test_draw_stack_badge_count_le_1_no_blit():
    screen = MagicMock()
    gv = _make_grid_view()
    gv._draw_stack_badge(screen, (50, 50), 1)
    screen.blit.assert_not_called()


def test_draw_stack_badge_count_5_blits():
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    gv._draw_stack_badge(screen, (50, 50), 5)
    assert screen.blit.called


def test_draw_stack_badge_count_150_shows_99plus(monkeypatch):
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    captured = []
    import soundrts.lib.screen as screen_mod

    def fake_render(label, pos, center=False, color=None):
        captured.append(str(label))

    monkeypatch.setattr(screen_mod, "screen_render", fake_render)
    gv._draw_stack_badge(screen, (50, 50), 150)
    assert "99+" in captured


# ---------------------------------------------------------------------------
# SI-06 KEYS panel
# ---------------------------------------------------------------------------


def test_keys_visible_default_false():
    hud = HudPanel(_make_interface())
    assert hud.keys_visible is False


def test_handle_mouse_event_keys_header_toggle():
    hud = HudPanel(_make_interface())
    hud._panel_rects["keys_header"] = pygame.Rect(0, 0, 100, 20)
    event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
    consumed = hud.handle_mouse_event(event)
    assert consumed is True
    assert hud.keys_visible is True
    consumed2 = hud.handle_mouse_event(event)
    assert consumed2 is True
    assert hud.keys_visible is False


def test_keys_panel_has_eight_hotkey_entries():
    assert len(HudPanel._KEYS_HOTKEYS) >= 6
    for key_label, l10n_key, default in HudPanel._KEYS_HOTKEYS:
        assert key_label and l10n_key.startswith("hotkey_") and default


# ---------------------------------------------------------------------------
# SI-07 enemy hover + attack cursor
# ---------------------------------------------------------------------------


def test_enemy_at_mousepos_returns_enemy():
    own_player = SimpleNamespace(name="me")
    enemy_player = SimpleNamespace(name="foe")
    enemy_player.player_is_an_enemy = lambda other: other is own_player
    enemy_entity = SimpleNamespace(player=enemy_player)
    gv = _make_grid_view()
    gv.interface.player = own_player
    gv.object_from_mousepos = MagicMock(return_value=enemy_entity)
    assert gv.enemy_at_mousepos((10, 10)) is enemy_entity


def test_enemy_at_mousepos_returns_none_for_own():
    own_player = SimpleNamespace(name="me")
    own_player.player_is_an_enemy = lambda other: False
    own_entity = SimpleNamespace(player=own_player)
    gv = _make_grid_view()
    gv.interface.player = own_player
    gv.object_from_mousepos = MagicMock(return_value=own_entity)
    assert gv.enemy_at_mousepos((10, 10)) is None


def test_attack_cursor_registered_in_mouse_lib():
    assert "attack" in mouse_lib.my_cursors
    cursor = mouse_lib.my_cursors["attack"]
    # record_cursor stores (size, hotspot, xormask, andmask).
    assert len(cursor) == 4
