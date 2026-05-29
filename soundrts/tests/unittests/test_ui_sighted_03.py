"""Tests for UI-SIGHTED-03 round (sighted-player UX layer, wave 3).

Coverage matrix:
  - SI-08: dynamic hotkey legend from res/ui/bindings.txt with cache
    and graceful fallback to the static label list.
  - SI-09: stack badge differentiated by owner category (own/enemy/
    ally) with retro-compatibility with the SI-05 signature.
  - SI-10: SIZEALL cursor surfaced while dragging a rubber-band
    selection, with priority over the SI-07 attack cursor and a
    display_is_active guard.

LEGGE-10: every test is self-contained; no imports from sibling
test_ui_sighted_0{1,2}.py modules.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pytest

from soundrts.clientgamegridview import GridView
from soundrts.clientgamehud import HudPanel
from soundrts.lib import mouse as mouse_lib


REPO_ROOT = Path(__file__).resolve().parents[3]
BINDINGS_TXT = REPO_ROOT / "res" / "ui" / "bindings.txt"


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


def _make_grid_view(player=None):
    iface = _make_interface()
    if player is not None:
        iface.player = player
    gv = GridView.__new__(GridView)
    gv.interface = iface
    return gv


# ---------------------------------------------------------------------------
# SI-08 dynamic hotkey legend
# ---------------------------------------------------------------------------


def test_load_bindings_real_file():
    if not BINDINGS_TXT.exists():
        pytest.skip("bindings.txt not in repo (unexpected)")
    bindings = HudPanel._load_bindings_from_file(str(BINDINGS_TXT))
    assert isinstance(bindings, dict)
    assert len(bindings) > 0
    # Verified actions from the canonical bindings.txt
    # (lines 24, 92, 250, 255).
    assert "unit_status" in bindings
    assert "default" in bindings
    assert "toggle_pause" in bindings


def test_load_bindings_missing_path():
    result = HudPanel._load_bindings_from_file("/nonexistent/path/bindings.txt")
    assert result == {}


def test_load_bindings_skips_comments_and_blank():
    # Indirect proof: a parsed file should never contain keys starting
    # with ';' or '#'.
    if not BINDINGS_TXT.exists():
        pytest.skip("bindings.txt not in repo")
    bindings = HudPanel._load_bindings_from_file(str(BINDINGS_TXT))
    for action in bindings:
        assert not action.startswith(";")
        assert not action.startswith("#")


def test_get_bindings_cache():
    hud = HudPanel(_make_interface())
    first = hud._get_bindings()
    second = hud._get_bindings()
    assert first is second  # cache hit, O(1) after first call
    assert isinstance(first, dict)


def test_get_bindings_fallback_empty(monkeypatch):
    hud = HudPanel(_make_interface())
    monkeypatch.setattr(
        HudPanel, "_load_bindings_from_file", staticmethod(lambda path: {})
    )
    bindings = hud._get_bindings()
    assert bindings == {}


# ---------------------------------------------------------------------------
# SI-09 owner-differentiated stack badge
# ---------------------------------------------------------------------------


def _captured_blits(screen):
    """Return the list of Surface objects passed to screen.blit."""
    calls = []
    for call in screen.blit.call_args_list:
        args, _ = call
        if args:
            calls.append(args[0])
    return calls


def test_badge_own_color_green():
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    gv._draw_stack_badge(
        screen, (50, 50), 3,
        color=(60, 166, 60), border_color=(80, 200, 80),
    )
    surfaces = _captured_blits(screen)
    assert len(surfaces) >= 1
    # The fill color should be present in the surface body
    # (at_least a centre-pixel sample matches the green tint).
    s = surfaces[0]
    px = s.get_at((s.get_width() // 2, s.get_height() // 2))
    assert (px.r, px.g, px.b) == (60, 166, 60)


def test_badge_enemy_color_red():
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    gv._draw_stack_badge(
        screen, (50, 50), 2,
        color=(166, 60, 60), border_color=(200, 80, 80),
    )
    surfaces = _captured_blits(screen)
    assert surfaces
    px = surfaces[0].get_at((9, 7))
    assert (px.r, px.g, px.b) == (166, 60, 60)


def test_badge_retrocompat_default_color():
    # SI-05 callers used positional args only; the default color
    # parameters keep them working.
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    screen = MagicMock()
    gv = _make_grid_view()
    gv._draw_stack_badge(screen, (50, 50), 5)
    assert screen.blit.called


def test_display_objects_groups_by_owner(monkeypatch):
    pygame.display.init()
    pygame.display.set_mode((200, 200))
    own = SimpleNamespace(name="me")
    own.player_is_an_enemy = lambda other: False
    enemy = SimpleNamespace(name="foe")
    enemy.player_is_an_enemy = lambda other: other is own
    # Cell-1 has 3 own + 2 enemy. Cell-2 has 1 own only.
    place_a = SimpleNamespace(id="A")
    place_b = SimpleNamespace(id="B")

    def mk(player, place, idx):
        o = SimpleNamespace()
        o.player = player
        o.place = place
        o.is_inside = False
        o.is_memory = False
        o.type_name = "unit{}".format(idx)
        return o

    units = [
        mk(own, place_a, 1), mk(own, place_a, 2), mk(own, place_a, 3),
        mk(enemy, place_a, 4), mk(enemy, place_a, 5),
        mk(own, place_b, 6),
    ]
    gv = _make_grid_view(player=own)
    gv.interface.dobjets = {i: u for i, u in enumerate(units)}
    gv.display_object = MagicMock()
    gv._object_coords = lambda o: (50, 50)
    badges = []
    gv._draw_stack_badge = lambda screen, pos, count, color=None, border_color=None: (
        badges.append((count, color))
    )
    monkeypatch.setattr(
        "soundrts.clientgamegridview.get_screen", lambda: MagicMock()
    )
    gv.display_objects()
    counts = sorted([(c, col) for c, col in badges])
    # Expect: own badge count=3 green, enemy badge count=2 red.
    # Cell-B own=1 → no badge.
    assert (2, (166, 60, 60)) in counts
    assert (3, (60, 166, 60)) in counts
    assert len(counts) == 2


# ---------------------------------------------------------------------------
# SI-10 SIZEALL cursor during rubber-band drag
# ---------------------------------------------------------------------------


def test_sizeall_cursor_registered_in_mouse_lib():
    assert "sizeall" in mouse_lib.my_cursors
    cursor = mouse_lib.my_cursors["sizeall"]
    assert len(cursor) == 4


def test_apply_rubber_band_cursor_during_drag():
    from soundrts.clientgame import GameInterface
    self_obj = SimpleNamespace()
    self_obj.display_is_active = True
    self_obj.mouse_select_origin = (10, 10)
    with patch("soundrts.clientgame.set_cursor") as mocked:
        result = GameInterface._apply_rubber_band_cursor(self_obj, (50, 50))
    assert result is True
    mocked.assert_called_once_with("sizeall")


def test_apply_rubber_band_cursor_no_origin():
    from soundrts.clientgame import GameInterface
    self_obj = SimpleNamespace()
    self_obj.display_is_active = True
    self_obj.mouse_select_origin = None
    with patch("soundrts.clientgame.set_cursor") as mocked:
        result = GameInterface._apply_rubber_band_cursor(self_obj, (50, 50))
    assert result is False
    mocked.assert_not_called()


def test_apply_rubber_band_cursor_display_off():
    from soundrts.clientgame import GameInterface
    self_obj = SimpleNamespace()
    self_obj.display_is_active = False
    self_obj.mouse_select_origin = (10, 10)
    with patch("soundrts.clientgame.set_cursor") as mocked:
        result = GameInterface._apply_rubber_band_cursor(self_obj, (50, 50))
    assert result is False
    mocked.assert_not_called()


def test_apply_rubber_band_cursor_zero_drag():
    # MOUSEBUTTONDOWN frame: pos == origin → suppress flicker.
    from soundrts.clientgame import GameInterface
    self_obj = SimpleNamespace()
    self_obj.display_is_active = True
    self_obj.mouse_select_origin = (50, 50)
    with patch("soundrts.clientgame.set_cursor") as mocked:
        result = GameInterface._apply_rubber_band_cursor(self_obj, (50, 50))
    assert result is False
    mocked.assert_not_called()


def test_priority_sizeall_over_attack():
    # When a drag is in progress, the SIZEALL cursor must win even if
    # the cursor is over an enemy: _apply_rubber_band_cursor returns
    # True and the handler exits before the SI-07 attack branch.
    from soundrts.clientgame import GameInterface
    self_obj = SimpleNamespace()
    self_obj.display_is_active = True
    self_obj.mouse_select_origin = (10, 10)
    with patch("soundrts.clientgame.set_cursor") as mocked:
        result = GameInterface._apply_rubber_band_cursor(self_obj, (80, 80))
    assert result is True
    # Only one cursor call (sizeall); no fall-through to "attack".
    assert mocked.call_count == 1
    assert mocked.call_args.args == ("sizeall",)
