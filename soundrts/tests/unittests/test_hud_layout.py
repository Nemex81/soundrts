from itertools import combinations
import locale
import sys
from types import SimpleNamespace

import pygame
import pytest

from soundrts.clientgamehud import HudEvent, HudPanel, HudSnapshot, HudUnitSnapshot


RESOLUTIONS = [
    (400, 300),
    (420, 260),
    (640, 480),
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1920, 1080),
]

FUNCTIONAL_RESOLUTIONS = RESOLUTIONS[2:]
PANEL_NAMES = ("res", "time", "events", "player", "group")


def _resolution_id(resolution):
    return "{}x{}".format(*resolution)


def _make_interface(display_is_active=True):
    player = SimpleNamespace(name="QA Player", race="human")
    unit_a = SimpleNamespace(type_name="peasant", number=1, hp=12, hp_max=20, orders=[SimpleNamespace(keyword="harvest")])
    unit_b = SimpleNamespace(type_name="soldier", number=2, hp=18, hp_max=20, orders=[SimpleNamespace(keyword="guard")])
    return SimpleNamespace(
        display_is_active=display_is_active,
        resources=[999, 888, 777],
        used_food=12,
        available_food=20,
        last_virtual_time=615,
        speed=1.0,
        player=player,
        group=[1, 2],
        dobjets={1: unit_a, 2: unit_b},
        _get_relative_speed=lambda: 1.5,
    )


def _make_snapshot():
    return HudSnapshot(
        resources=["Gold: 999", "Wood: 888", "Food: 777"],
        food="Pop: 12/20",
        time="Time: 10:15",
        speed="Speed: x1.5",
        units=[
            HudUnitSnapshot("peasant #1", 12, 20, "harvest"),
            HudUnitSnapshot("soldier #2", 18, 20, "guard"),
        ],
        events=[
            HudEvent("combat", "under attack: town hall at 4,5"),
            HudEvent("info", "worker ready at 5,5"),
            HudEvent("alert", "enemy spotted near bridge"),
            HudEvent("combat", "peasant attacked at 6,4"),
            HudEvent("info", "research complete at barracks"),
        ],
        player="QA Player (human)",
    )


def _capture_layout(monkeypatch, resolution):
    surface = pygame.Surface(resolution)
    monkeypatch.setattr(pygame.display, "get_surface", lambda: surface)
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
    monkeypatch.setattr(locale, "getdefaultlocale", lambda: ("en_US", "UTF-8"))

    from soundrts.lib import screen as screen_module

    monkeypatch.setattr(screen_module, "screen_render", lambda *args, **kwargs: None)
    monkeypatch.setattr(screen_module, "screen_render_header", lambda *args, **kwargs: None)

    panel = HudPanel(_make_interface())
    snapshot = _make_snapshot()
    panel._draw_snapshot(surface, snapshot)
    return panel, snapshot, panel._panel_rects


def _estimated_content_height(panel, snapshot, panel_name):
    header_height = 20
    if panel_name == "res":
        return header_height + (len(snapshot.resources) + 1) * panel.line_height
    if panel_name == "events":
        return header_height + max(1, len(snapshot.events)) * panel.line_height
    if panel_name == "group":
        return header_height + max(1, len(snapshot.units)) * panel.line_height
    raise AssertionError("unexpected dynamic panel: {}".format(panel_name))


def test_display_skips_hud_below_minimum_resolution(monkeypatch):
    interface = _make_interface(display_is_active=True)
    panel = HudPanel(interface)
    surface = pygame.Surface((420, 260))
    draw_calls = []

    monkeypatch.setattr(pygame.display, "get_surface", lambda: surface)
    monkeypatch.setattr(panel, "_draw_snapshot", lambda *args, **kwargs: draw_calls.append(args))

    panel.display()

    assert draw_calls == []


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_hud_panels_do_not_overlap(monkeypatch, resolution):
    _, _, rects = _capture_layout(monkeypatch, resolution)

    for first_name, second_name in combinations(PANEL_NAMES, 2):
        assert not rects[first_name].colliderect(rects[second_name]), (
            "{} overlaps {} at {} with rects {} and {}".format(
                first_name,
                second_name,
                _resolution_id(resolution),
                rects[first_name],
                rects[second_name],
            )
        )


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_hud_panels_stay_within_vertical_bounds(monkeypatch, resolution):
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    _, height = resolution
    bottom_limit = height - panel.margin

    for name, rect in rects.items():
        assert rect.bottom <= bottom_limit, (
            "{} exceeds vertical bounds at {}: bottom={} limit={}".format(
                name,
                _resolution_id(resolution),
                rect.bottom,
                bottom_limit,
            )
        )


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_hud_panels_stay_within_horizontal_bounds(monkeypatch, resolution):
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    width, _ = resolution
    right_limit = width - panel.margin

    for name, rect in rects.items():
        assert rect.right <= right_limit, (
            "{} exceeds horizontal bounds at {}: right={} limit={}".format(
                name,
                _resolution_id(resolution),
                rect.right,
                right_limit,
            )
        )


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_dynamic_panel_content_fits_estimated_height(monkeypatch, resolution):
    panel, snapshot, rects = _capture_layout(monkeypatch, resolution)

    for name in ("res", "events", "group"):
        estimated_height = _estimated_content_height(panel, snapshot, name)
        assert estimated_height <= rects[name].height, (
            "{} estimated content height {} exceeds panel height {} at {}".format(
                name,
                estimated_height,
                rects[name].height,
                _resolution_id(resolution),
            )
        )


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_time_panel_has_minimum_height(monkeypatch, resolution):
    """T_TIME_PADDING: TIME panel must be at least 68px to avoid descender clipping."""
    _, _, rects = _capture_layout(monkeypatch, resolution)
    assert rects["time"].height >= 68, (
        "TIME panel height {} < 68px at {}; text at y+42 would be clipped".format(
            rects["time"].height,
            _resolution_id(resolution),
        )
    )


# T_SUBTITLE_RIGHT: screen_render_subtitle() positions the status bar at
# x = screen_width - text_width - 16 (bottom-right anchor, outside map area).
# Requires a running pygame display to verify at runtime; not mockable here.
# Manual verification: launch a game session and confirm the subtitle appears
# in the bottom-right quadrant (x > screen_width // 2) at all resolutions.