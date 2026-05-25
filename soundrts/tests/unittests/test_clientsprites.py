"""Tests for soundrts.clientsprites and its integration in GridView.

These tests are intentionally headless: they monkeypatch the sprite
cache to avoid relying on a real pygame display being initialised
(consistent with the rest of the unit-test suite).
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pygame
import pytest

from soundrts import clientgamegridview, clientsprites


REPO_ROOT = Path(__file__).resolve().parents[3]


# --- T1: cache miss --------------------------------------------------------

def test_get_returns_none_when_file_missing(tmp_path, monkeypatch):
    """A non-existent PNG must produce a None entry, not a crash."""
    monkeypatch.setattr(clientsprites, "_IMG_ROOT", tmp_path)
    clientsprites.clear()
    assert clientsprites.get("units", "does_not_exist", 32) is None


# --- T2: cache hit ---------------------------------------------------------

def _headless_display():
    """Initialise a minimal pygame display backend for surface ops."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))


def test_get_returns_surface_when_file_exists(tmp_path, monkeypatch):
    """An opaque RGBA PNG must yield a scaled Surface at target size."""
    _headless_display()
    img = pygame.Surface((64, 64), pygame.SRCALPHA)
    img.fill((255, 0, 0, 255))
    (tmp_path / "units").mkdir()
    pygame.image.save(img, str(tmp_path / "units" / "u.png"))
    monkeypatch.setattr(clientsprites, "_IMG_ROOT", tmp_path)
    clientsprites.clear()
    surf = clientsprites.get("units", "u", 32)
    assert surf is not None
    assert surf.get_size() == (32, 32)


# --- T3: clear() -----------------------------------------------------------

def test_clear_empties_the_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(clientsprites, "_IMG_ROOT", tmp_path)
    clientsprites.clear()
    clientsprites.get("units", "absent", 32)
    assert len(clientsprites._cache) == 1
    clientsprites.clear()
    assert clientsprites._cache == {}


# --- T6: category_of resolver ---------------------------------------------

@pytest.mark.parametrize("type_name,expected", [
    ("peasant", "units"),
    ("knight", "units"),
    ("submarine", "units"),
    ("townhall", "buildings"),
    ("wall", "buildings"),
    ("shipyard", "buildings"),
    ("goldmine", "resources"),
    ("wood", "resources"),
    ("unknown_thing", None),
    ("", None),
])
def test_category_of_static_map(type_name, expected):
    obj = MagicMock()
    obj.type_name = type_name
    assert clientsprites.category_of(obj) == expected


def test_category_of_handles_missing_attribute():
    """Objects without ``type_name`` must yield None (no crash)."""
    obj = object()
    assert clientsprites.category_of(obj) is None


# --- T7: transparent placeholder is treated as missing ---------------------

def test_fully_transparent_placeholder_returns_none(tmp_path, monkeypatch):
    """Round 15-B placeholders (alpha=0 RGBA) must trigger fallback."""
    _headless_display()
    ph = pygame.Surface((32, 32), pygame.SRCALPHA)
    ph.fill((0, 0, 0, 0))
    (tmp_path / "units").mkdir()
    pygame.image.save(ph, str(tmp_path / "units" / "zombie.png"))
    monkeypatch.setattr(clientsprites, "_IMG_ROOT", tmp_path)
    clientsprites.clear()
    assert clientsprites.get("units", "zombie", 32) is None


# --- T8: real res/img/ root is wired up correctly --------------------------

def test_img_root_points_at_repo_res_img():
    """_IMG_ROOT must resolve to <repo>/res/img and exist."""
    assert clientsprites._IMG_ROOT == REPO_ROOT / "res" / "img"
    assert clientsprites._IMG_ROOT.is_dir()


# --- T9: cache hit is reused (no double load) ------------------------------

def test_cache_reuses_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(clientsprites, "_IMG_ROOT", tmp_path)
    clientsprites.clear()
    first = clientsprites.get("units", "ghost", 32)
    second = clientsprites.get("units", "ghost", 32)
    assert first is None and second is None
    # Single cache entry, identical key.
    assert list(clientsprites._cache.keys()) == ["units/ghost@32"]


# --- T4: GridView.display_object falls back when sprite is missing --------

def _make_gridview_with_object(shape: str, type_name: str):
    """Return a GridView and a stub object exercising display_object."""
    gv = clientgamegridview.GridView.__new__(clientgamegridview.GridView)
    iface = MagicMock()
    iface.target = None
    iface.group = set()
    iface.player = MagicMock()
    iface.player.allied = []
    iface.player.player_is_an_enemy = MagicMock(return_value=False)
    gv.interface = iface
    obj = MagicMock()
    obj.is_inside = False
    obj.id = "obj-1"
    obj.shape = MagicMock(return_value=shape)
    obj.collision = False
    obj.type_name = type_name
    obj.corrected_color = MagicMock(return_value=(10, 20, 30))
    obj.model = MagicMock(player=None)
    return gv, obj


def test_display_object_circle_fallback_calls_set_at(monkeypatch):
    """When category_of yields None, the legacy set_at path must run."""
    gv, obj = _make_gridview_with_object("circle", "no_such_unit")
    monkeypatch.setattr(clientgamegridview, "R", 4, raising=False)
    monkeypatch.setattr(clientgamegridview, "R2", 16, raising=False)
    monkeypatch.setattr(gv, "_object_coords", lambda o: (100, 100))
    fake_screen = MagicMock()
    monkeypatch.setattr(clientgamegridview, "get_screen",
                        lambda: fake_screen)
    monkeypatch.setattr(clientsprites, "get",
                        lambda *a, **kw: None)
    gv.display_object(obj)
    fake_screen.set_at.assert_called_once()


def test_display_object_square_fallback_calls_draw_rect(monkeypatch):
    """When category_of yields None for a square, draw_rect must run."""
    gv, obj = _make_gridview_with_object("square", "no_such_building")
    monkeypatch.setattr(clientgamegridview, "R", 4, raising=False)
    monkeypatch.setattr(clientgamegridview, "R2", 16, raising=False)
    monkeypatch.setattr(gv, "_object_coords", lambda o: (50, 50))
    monkeypatch.setattr(clientgamegridview, "get_screen",
                        lambda: MagicMock())
    monkeypatch.setattr(clientsprites, "get",
                        lambda *a, **kw: None)
    with patch.object(clientgamegridview, "draw_rect") as draw_rect_mock:
        gv.display_object(obj)
    draw_rect_mock.assert_called_once()


def test_display_object_circle_uses_sprite_when_available(monkeypatch):
    """A non-None sprite must be blit; circle/set_at must NOT run."""
    gv, obj = _make_gridview_with_object("circle", "peasant")
    monkeypatch.setattr(clientgamegridview, "R", 4, raising=False)
    monkeypatch.setattr(clientgamegridview, "R2", 16, raising=False)
    monkeypatch.setattr(gv, "_object_coords", lambda o: (40, 40))
    fake_screen = MagicMock()
    monkeypatch.setattr(clientgamegridview, "get_screen",
                        lambda: fake_screen)
    fake_sprite = object()
    monkeypatch.setattr(clientsprites, "get",
                        lambda *a, **kw: fake_sprite)
    with patch.object(clientgamegridview.pygame.draw, "circle") as draw_circle:
        gv.display_object(obj)
    fake_screen.blit.assert_called_once_with(fake_sprite,
                                             (40 - 8, 40 - 8))
    draw_circle.assert_not_called()
    fake_screen.set_at.assert_not_called()


# --- T5: GridView._display terrain fallback is preserved -------------------

def test_display_terrain_calls_sprite_cache(monkeypatch):
    """_display() must consult clientsprites.get with category=terrain
    for every observed square (PR-1 integration smoke test)."""
    gv = clientgamegridview.GridView.__new__(clientgamegridview.GridView)
    iface = MagicMock()
    iface.xcmax = 0
    iface.ycmax = 0
    sq = MagicMock()
    sq.type_name = "_meadows"
    sq.exits = []
    sq.x = 0
    sq.y = 0
    iface.player.world.grid = {(0, 0): sq}
    iface.player.observed_squares = {sq}
    iface.player.observed_before_squares = set()
    gv.interface = iface
    gv.square_view_width = 32
    gv.square_view_height = 32
    gv.ymax = 32
    calls = []

    def fake_get(category, name, size):
        calls.append((category, name, size))
        return None

    monkeypatch.setattr(clientsprites, "get", fake_get)
    monkeypatch.setattr(clientgamegridview, "get_screen",
                        lambda: MagicMock())
    monkeypatch.setattr(clientgamegridview, "draw_rect",
                        lambda *a, **kw: None)
    monkeypatch.setattr(clientgamegridview, "draw_line",
                        lambda *a, **kw: None)
    monkeypatch.setattr(clientgamegridview, "square_color",
                        lambda sq: (0, 0, 0))
    monkeypatch.setattr(clientgamegridview, "fade",
                        lambda c: c)
    gv._display()
    assert ("terrain", "meadows", 32) in calls
