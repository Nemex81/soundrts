"""Tests for UI-MASTER-04 round.

Coverage:
  - T9-CANCEL: _collect_activity returns a 4-tuple, click on
    activity_row_N cancels the source unit's first order, row tooltip
    includes the cancel hint.
  - T9-TOOLTIP-GLOBAL: each new HUD widget exposes a rect and a
    non-empty tooltip.
  - T9-L10N-AUDIT: every _hud_text/_hud_format/_hud_named_format key
    used in clientgamehud.py is registered in res/ui/style.txt and
    res/ui-it/style.txt.
"""
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import locale
import pygame
import pytest

from soundrts.clientgamehud import (
    HudPanel,
    HudEvent,
    HudSnapshot,
    HudUnitSnapshot,
)


# ---------------------------------------------------------------------------
# Test fixtures (shared with prior rounds).
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
    return iface


def _make_hud():
    return HudPanel(_make_interface())


def _snapshot(units=None):
    if units is None:
        units = [
            HudUnitSnapshot(label="orc #1", hit_points=40, max_hit_points=50, status="idle"),
            HudUnitSnapshot(label="tower", hit_points=None, max_hit_points=None, status="building"),
        ]
    return HudSnapshot(
        resources=["Gold: 500", "Wood: 250"],
        food="Pop: 3/10",
        time="Time: 01:23",
        speed="Speed: x1.0",
        units=units,
        events=[HudEvent(severity="info", text="built tower")],
        player="Tester",
    )


def _draw(hud, snap, size=(800, 600), monkeypatch=None):
    surface = pygame.Surface(size)
    if monkeypatch is not None:
        from soundrts.lib import screen as screen_module

        monkeypatch.setattr(screen_module, "screen_render", lambda *a, **k: None)
        monkeypatch.setattr(screen_module, "screen_render_header", lambda *a, **k: None)
    hud._draw_snapshot(surface, snap)


@pytest.fixture(autouse=True)
def _mute_screen(monkeypatch):
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
    monkeypatch.setattr(locale, "getdefaultlocale", lambda: ("en_US", "UTF-8"))
    from soundrts.lib import screen as screen_module

    monkeypatch.setattr(screen_module, "screen_render", lambda *a, **k: None)
    monkeypatch.setattr(screen_module, "screen_render_header", lambda *a, **k: None)


# ---------------------------------------------------------------------------
# T9-CANCEL
# ---------------------------------------------------------------------------


def test_collect_activity_returns_4_tuple_with_unit():
    hud = _make_hud()
    order = SimpleNamespace(
        cls=SimpleNamespace(keyword="train"),
        type=SimpleNamespace(type_name="archer"),
        time=10, time_cost=20,
    )
    u = SimpleNamespace(orders=[order])
    hud.interface.player = SimpleNamespace(units=[u])
    out = hud._collect_activity()
    assert len(out) == 1
    item = out[0]
    assert len(item) == 4, f"expected 4-tuple, got {len(item)}"
    assert item[0] == "training"
    assert item[1] == "archer"
    assert item[2] == 50
    assert item[3] is u


def test_activity_row_click_cancels_unit_order():
    hud = _make_hud()
    hud.activity_visible = True
    # Inject a fake activity item with a mutable orders list.
    fake_unit = SimpleNamespace(orders=["first_order", "second_order"])
    with patch.object(
        type(hud), "_collect_activity",
        return_value=[("training", "archer", 25, fake_unit)],
    ):
        _draw(hud, _snapshot())
        row = hud.rect_for("activity_row_0")
        assert row is not None
        click = SimpleNamespace(
            type=pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=(row.centerx, row.centery),
        )
        consumed = hud.handle_mouse_event(click)
        assert consumed is True
        # The first order must be gone, the second still present.
        assert fake_unit.orders == ["second_order"]


def test_activity_row_click_with_none_unit_does_not_crash():
    hud = _make_hud()
    hud.activity_visible = True
    # 3-tuple legacy path => unit ref absent.
    with patch.object(
        type(hud), "_collect_activity",
        return_value=[("training", "ghost", 10)],
    ):
        _draw(hud, _snapshot())
        row = hud.rect_for("activity_row_0")
        assert row is not None
        click = SimpleNamespace(
            type=pygame.MOUSEBUTTONDOWN, button=1,
            pos=(row.centerx, row.centery),
        )
        # Should not raise. Returns True (consumed).
        assert hud.handle_mouse_event(click) is True


def test_activity_row_tooltip_includes_cancel_hint():
    hud = _make_hud()
    hud.activity_visible = True
    fake_unit = SimpleNamespace(orders=["x"])
    with patch.object(
        type(hud), "_collect_activity",
        return_value=[("training", "archer", 25, fake_unit)],
    ):
        _draw(hud, _snapshot())
    row = hud.rect_for("activity_row_0")
    assert row is not None
    hud._update_tooltip((row.centerx, row.centery))
    # Localized: EN "Click to cancel" or IT "Clicca per annullare".
    assert ("Click to cancel" in hud._tooltip_text
            or "Clicca per annullare" in hud._tooltip_text)


def test_cancel_unit_order_swallows_exceptions():
    hud = _make_hud()
    bad_unit = SimpleNamespace()  # no .orders attribute
    hud._cancel_unit_order(bad_unit)  # must not raise


# ---------------------------------------------------------------------------
# T9-TOOLTIP-GLOBAL
# ---------------------------------------------------------------------------


def test_res_cell_rects_registered_per_resource():
    hud = _make_hud()
    _draw(hud, _snapshot())
    assert hud.rect_for("res_cell_0") is not None
    assert hud.rect_for("res_cell_1") is not None
    assert hud.rect_for("food_cell") is not None


def test_bottom_bar_cell_rects_registered():
    hud = _make_hud()
    _draw(hud, _snapshot())
    assert hud.rect_for("bottom_time") is not None
    assert hud.rect_for("bottom_speed") is not None


def test_group_row_rect_registered_per_unit():
    hud = _make_hud()
    _draw(hud, _snapshot())
    # Two units in the snapshot.
    assert hud.rect_for("group_row_0") is not None
    assert hud.rect_for("group_row_1") is not None


def test_tooltip_on_res_cell_uses_snapshot_value():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("res_cell_0")
    hud._update_tooltip((r.centerx, r.centery))
    assert hud._tooltip_text != ""
    assert "Gold" in hud._tooltip_text
    assert "500" in hud._tooltip_text


def test_tooltip_on_food_cell_uses_snapshot_value():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("food_cell")
    hud._update_tooltip((r.centerx, r.centery))
    assert hud._tooltip_text != ""
    assert "Pop: 3/10" in hud._tooltip_text


def test_tooltip_on_bottom_time_uses_snapshot_value():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("bottom_time")
    hud._update_tooltip((r.centerx, r.centery))
    assert "Time: 01:23" in hud._tooltip_text


def test_tooltip_on_bottom_speed_uses_snapshot_value():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("bottom_speed")
    hud._update_tooltip((r.centerx, r.centery))
    assert "Speed" in hud._tooltip_text


def test_tooltip_on_player_panel_uses_snapshot_value():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("player")
    hud._update_tooltip((r.centerx, r.centery))
    assert "Tester" in hud._tooltip_text


def test_tooltip_on_group_row_with_hp():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("group_row_0")
    hud._update_tooltip((r.centerx, r.centery))
    assert "orc #1" in hud._tooltip_text
    assert "40" in hud._tooltip_text
    assert "50" in hud._tooltip_text


def test_tooltip_on_group_row_without_hp():
    hud = _make_hud()
    _draw(hud, _snapshot())
    r = hud.rect_for("group_row_1")
    hud._update_tooltip((r.centerx, r.centery))
    assert "tower" in hud._tooltip_text
    assert "building" in hud._tooltip_text


def test_map_empty_cell_tooltip_via_set_map_hover():
    """T10-TOOLTIP-THROTTLE: the empty-cell tooltip is now debounced so
    quick mouse drags over the grid don't flicker. After a single
    set_map_hover call the tooltip is still suppressed; it materialises
    only when the same cell stays under the cursor for at least
    ``_empty_cell_tooltip_delay`` seconds.
    """
    hud = _make_hud()
    square = SimpleNamespace(col=3, row=7)
    # First sample: starts the debounce timer, tooltip stays empty.
    hud.set_map_hover(None, (100, 100), square=square)
    assert hud._tooltip_text == ""
    # Simulate elapsed time past the debounce window without changing
    # the hovered cell, then re-feed the same (col,row): tooltip must
    # now appear with the cell coordinates.
    hud._empty_cell_hover_start -= hud._empty_cell_tooltip_delay + 0.05
    same_cell = SimpleNamespace(col=3, row=7)
    hud.set_map_hover(None, (100, 100), square=same_cell)
    assert hud._tooltip_text != ""
    assert "3" in hud._tooltip_text and "7" in hud._tooltip_text


def test_set_map_hover_full_clear_when_no_entity_no_square():
    hud = _make_hud()
    hud._tooltip_text = "stale"
    hud._tooltip_pos = (1, 1)
    hud.set_map_hover(None, None)
    assert hud._tooltip_text == ""
    assert hud._tooltip_pos is None


def test_last_snapshot_recorded_by_draw_snapshot():
    hud = _make_hud()
    snap = _snapshot()
    _draw(hud, snap)
    assert hud._last_snapshot is snap


# ---------------------------------------------------------------------------
# T9-L10N-AUDIT
# ---------------------------------------------------------------------------


_HUD_TEXT_CALL = re.compile(
    r"""self\._hud_(?:text|format|named_format)\(\s*['"]([a-zA-Z0-9_]+)['"]""",
    re.DOTALL,
)


def _extract_hud_keys() -> set:
    src = Path("soundrts/clientgamehud.py").read_text(encoding="utf-8")
    return set(_HUD_TEXT_CALL.findall(src))


def _section_keys(path: Path, section: str) -> set:
    keys: set = set()
    current = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("def "):
            current = line.split(None, 1)[1].strip()
            continue
        if current != section:
            continue
        first = line.split(None, 1)[0]
        if first:
            keys.add(first)
    return keys


def test_all_hud_text_keys_present_in_en_and_it():
    used = _extract_hud_keys()
    assert used, "no _hud_text/_hud_format keys extracted; regex broken"
    en_keys = _section_keys(Path("res/ui/style.txt"), "hud")
    it_keys = _section_keys(Path("res/ui-it/style.txt"), "hud")
    missing_en = sorted(used - en_keys)
    missing_it = sorted(used - it_keys)
    assert missing_en == [], f"missing EN keys: {missing_en}"
    assert missing_it == [], f"missing IT keys: {missing_it}"


def test_t9_new_keys_present_en_it():
    expected = {
        "tooltip_activity_cancel_hint",
        "tooltip_activity_row_full",
        "tooltip_res_cell",
        "tooltip_food_cell",
        "tooltip_player_panel",
        "tooltip_unit_row",
        "tooltip_unit_row_nohp",
        "tooltip_bottom_time",
        "tooltip_bottom_speed",
        "tooltip_map_empty_cell",
    }
    en_keys = _section_keys(Path("res/ui/style.txt"), "hud")
    it_keys = _section_keys(Path("res/ui-it/style.txt"), "hud")
    assert expected.issubset(en_keys), f"missing in EN: {expected - en_keys}"
    assert expected.issubset(it_keys), f"missing in IT: {expected - it_keys}"


def test_t9_new_keys_present_fr_ptbr():
    expected = {
        "tooltip_activity_cancel_hint",
        "tooltip_player_panel",
        "tooltip_bottom_time",
        "tooltip_bottom_speed",
        "tooltip_map_empty_cell",
    }
    for rel in ("res/ui-fr/style.txt", "res/ui-pt-BR/style.txt"):
        # FR/PT-BR placeholders may be plain-text appended rather than in
        # a parsed def section; substring match is sufficient for audit.
        text = Path(rel).read_text(encoding="utf-8", errors="replace")
        missing = [k for k in expected if k not in text]
        assert missing == [], f"{rel} missing {missing}"
