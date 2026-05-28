"""Unit tests for Round UI-MASTER-02b.

Coverage:
- BUG-T4 fix: GROUP panel leaves room for ACTIVITY when activity_visible=True.
- T7-EVENTI: event row rects + full-text tooltip on hover.
- T7-MAPPA: set_map_hover delay logic and localized _build_map_tooltip.
"""
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

if len(sys.argv) > 1:
    sys.argv = [sys.argv[0]]


def _make_hud():
    from soundrts.clientgamehud import HudPanel

    interface = MagicMock()
    interface.player = None
    return HudPanel(interface)


def _snapshot(events=None, units=None):
    from soundrts.clientgamehud import HudSnapshot

    return HudSnapshot(
        resources=[],
        food="Pop: 0/0",
        time="Time: 00:00",
        speed="Speed: x1.0",
        units=list(units or []),
        events=list(events or []),
        player="Player",
    )


# ---------------------------------------------------------------------------
# BUG-T4
# ---------------------------------------------------------------------------

def test_activity_panel_drawn_when_activity_flag_true():
    import pygame
    from soundrts.clientgamehud import HudPanel

    hud = _make_hud()
    hud.activity_visible = True
    snap = _snapshot()
    screen = pygame.Surface((800, 600))
    called = {"n": 0}

    def fake(self, screen, left, top, width, bottom):
        called["n"] += 1
        called["top"] = top

    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header"), \
         patch.object(HudPanel, "_draw_activity_panel", fake):
        hud._draw_snapshot(screen, snap)

    assert called["n"] == 1
    assert called["top"] < 600 - hud.margin - hud.panel_header_height


def test_group_leaves_room_for_activity_with_many_units_and_events_open():
    import pygame
    from soundrts.clientgamehud import HudPanel, HudUnitSnapshot, HudEvent

    hud = _make_hud()
    hud.activity_visible = True
    hud.events_visible = True
    units = [HudUnitSnapshot("u{}".format(i), 10, 10, "") for i in range(8)]
    events = [HudEvent("info", "evt {}".format(i)) for i in range(8)]
    snap = _snapshot(events=events, units=units)
    screen = pygame.Surface((800, 600))
    activity_top_holder = {}

    def fake(self, screen, left, top, width, bottom):
        activity_top_holder["top"] = top

    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header"), \
         patch.object(HudPanel, "_draw_activity_panel", fake):
        hud._draw_snapshot(screen, snap)

    assert "top" in activity_top_holder, "ACTIVITY panel was not drawn"
    group_rect = hud._panel_rects["group"]
    assert group_rect.bottom + hud.margin <= activity_top_holder["top"] + 4


def test_group_unchanged_when_activity_hidden():
    import pygame
    from soundrts.clientgamehud import HudUnitSnapshot

    hud = _make_hud()
    hud.activity_visible = False
    units = [HudUnitSnapshot("u{}".format(i), 10, 10, "") for i in range(8)]
    snap = _snapshot(units=units)
    screen = pygame.Surface((800, 600))
    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header"):
        hud._draw_snapshot(screen, snap)
    group_rect = hud._panel_rects["group"]
    # 8 units cap → header + 8 * line_height
    assert group_rect.height == hud.panel_header_height + 8 * hud.line_height


# ---------------------------------------------------------------------------
# T7-EVENTI
# ---------------------------------------------------------------------------

def test_event_row_rects_populated_when_events_visible():
    import pygame
    from soundrts.clientgamehud import HudEvent

    hud = _make_hud()
    hud.events_visible = True
    events = [HudEvent("info", "evt {}".format(i)) for i in range(3)]
    snap = _snapshot(events=events)
    screen = pygame.Surface((800, 600))
    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header"):
        hud._draw_snapshot(screen, snap)
    for i in range(3):
        assert "event_row_{}".format(i) in hud._panel_rects


def test_event_row_texts_keep_full_string():
    import pygame
    from soundrts.clientgamehud import HudEvent

    hud = _make_hud()
    hud.events_visible = True
    long_text = "this is a very long event description well past the 23 char limit"
    events = [HudEvent("info", long_text)]
    snap = _snapshot(events=events)
    screen = pygame.Surface((800, 600))
    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header"):
        hud._draw_snapshot(screen, snap)
    full = hud._event_row_texts[0]
    assert long_text in full
    assert len(full) > hud.event_text_max_length


def test_tooltip_shows_full_event_on_hover():
    import pygame

    hud = _make_hud()
    hud.events_visible = True
    full = "completed: very_long_unit_name at base_north"
    hud._panel_rects["event_row_0"] = pygame.Rect(0, 0, 200, 26)
    hud._event_row_texts[0] = full
    hud._update_tooltip((10, 10))
    assert hud._tooltip_text == full


def test_no_event_tooltip_when_panel_collapsed():
    import pygame

    hud = _make_hud()
    hud.events_visible = False
    hud._panel_rects["event_row_0"] = pygame.Rect(0, 0, 200, 26)
    hud._event_row_texts[0] = "should not show"
    hud._update_tooltip((10, 10))
    assert hud._tooltip_text == ""


# ---------------------------------------------------------------------------
# T7-MAPPA
# ---------------------------------------------------------------------------

def test_set_map_hover_none_clears_state():
    hud = _make_hud()
    hud._map_hover_entity = object()
    hud._tooltip_text = "x"
    hud._tooltip_pos = (1, 2)
    hud.set_map_hover(None, None)
    assert hud._map_hover_entity is None
    assert hud._tooltip_text == ""
    assert hud._tooltip_pos is None


def test_set_map_hover_delays_tooltip():
    hud = _make_hud()
    entity = SimpleNamespace(type_name="archer", hp=10, hp_max=10, player=None, orders=[])
    with patch("soundrts.clientgamehud.time.monotonic", return_value=100.0):
        hud.set_map_hover(entity, (50, 50))
    assert hud._tooltip_text == ""
    assert hud._map_hover_entity is entity


def test_set_map_hover_shows_tooltip_after_delay():
    hud = _make_hud()
    entity = SimpleNamespace(type_name="archer", hp=10, hp_max=10, player=None, orders=[])
    with patch("soundrts.clientgamehud.time.monotonic", return_value=100.0):
        hud.set_map_hover(entity, (50, 50))
    with patch("soundrts.clientgamehud.time.monotonic", return_value=100.5):
        hud.set_map_hover(entity, (50, 50))
    assert hud._tooltip_text != ""
    assert "archer" in hud._tooltip_text


def test_build_map_tooltip_handles_missing_attributes():
    hud = _make_hud()
    # Entity exposes only type_name; hp/owner/orders raise via getattr default.
    entity = SimpleNamespace(type_name="tree")
    text = hud._build_map_tooltip(entity, (0, 0))
    assert "tree" in text
    # No spurious "None" tokens from missing attributes.
    assert "None" not in text


def test_build_map_tooltip_includes_localized_hp():
    hud = _make_hud()
    entity = SimpleNamespace(
        type_name="orc",
        hp=42,
        hp_max=80,
        player=SimpleNamespace(name="red"),
        orders=[SimpleNamespace(keyword="attack")],
    )
    text = hud._build_map_tooltip(entity, (0, 0))
    # The localized template "HP: {hp}/{hp_max}" must produce the values.
    assert "42" in text and "80" in text
    assert "red" in text
    assert "attack" in text


def test_is_pos_over_hud_detects_panel_overlap():
    import pygame

    hud = _make_hud()
    hud._panel_rects["res"] = pygame.Rect(0, 0, 800, 40)
    assert hud.is_pos_over_hud((10, 10)) is True
    assert hud.is_pos_over_hud((10, 500)) is False


def test_is_pos_over_hud_ignores_internal_rects():
    """event_row_* and activity_tab_* rects live inside parent panels;
    they should not trigger HUD overlap detection on their own."""
    import pygame

    hud = _make_hud()
    hud._panel_rects["event_row_0"] = pygame.Rect(0, 0, 200, 26)
    hud._panel_rects["activity_tab_all"] = pygame.Rect(0, 100, 50, 24)
    assert hud.is_pos_over_hud((10, 10)) is False
    assert hud.is_pos_over_hud((10, 110)) is False


# ---------------------------------------------------------------------------
# Localization presence
# ---------------------------------------------------------------------------

def test_en_it_style_have_ui_master_02b_keys():
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    expected = [
        "tooltip_event_full",
        "tooltip_map_entity",
        "tooltip_map_hp",
        "tooltip_map_owner",
        "tooltip_map_coords",
        "entity_na",
    ]
    for rel in ("res/ui/style.txt", "res/ui-it/style.txt"):
        text = (repo_root / rel).read_text(encoding="utf-8", errors="replace")
        missing = [key for key in expected if key not in text]
        assert missing == [], f"{rel} missing {missing}"


# ---------------------------------------------------------------------------
# clientgame.py MOUSEMOTION wiring
# ---------------------------------------------------------------------------

def test_mousemotion_dispatches_set_map_hover_off_hud():
    from soundrts import clientgame

    hud = SimpleNamespace(
        handle_mouse_event=MagicMock(return_value=False),
        is_pos_over_hud=MagicMock(return_value=False),
        set_map_hover=MagicMock(),
    )
    target = object()
    grid_view = SimpleNamespace(
        object_from_mousepos=MagicMock(return_value=target),
        square_from_mousepos=MagicMock(return_value=None),
    )
    iface = SimpleNamespace(
        hud_panel=hud,
        grid_view=grid_view,
        target=None,
        an_order_requiring_a_target_is_selected=False,
        place=None,
        say_target=MagicMock(),
        display=MagicMock(),
    )
    event = SimpleNamespace(type=clientgame.MOUSEMOTION, pos=(100, 200))
    with patch.object(clientgame, "set_cursor"):
        clientgame.GameInterface._process_fullscreen_mode_mouse_event(iface, event)
    hud.set_map_hover.assert_called_with(target, (100, 200))


def test_mousemotion_clears_map_hover_when_over_hud():
    from soundrts import clientgame

    hud = SimpleNamespace(
        handle_mouse_event=MagicMock(return_value=False),
        is_pos_over_hud=MagicMock(return_value=True),
        set_map_hover=MagicMock(),
    )
    grid_view = SimpleNamespace(
        object_from_mousepos=MagicMock(return_value=None),
        square_from_mousepos=MagicMock(return_value=None),
    )
    iface = SimpleNamespace(
        hud_panel=hud,
        grid_view=grid_view,
        target=None,
        an_order_requiring_a_target_is_selected=False,
        place=None,
        say_target=MagicMock(),
        display=MagicMock(),
    )
    event = SimpleNamespace(type=clientgame.MOUSEMOTION, pos=(10, 10))
    with patch.object(clientgame, "set_cursor"):
        clientgame.GameInterface._process_fullscreen_mode_mouse_event(iface, event)
    hud.set_map_hover.assert_called_with(None, None)
