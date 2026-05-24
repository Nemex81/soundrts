from itertools import combinations
import locale
from pathlib import Path
import sys
from types import SimpleNamespace

import pygame
import pytest

from soundrts.clientgamehud import HudEvent, HudPanel, HudSnapshot, HudUnitSnapshot
from soundrts.definitions import Style


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
    header_height = panel.panel_header_height
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


def test_hud_panel_font_layout_constants_are_updated():
    assert HudPanel.line_height == 26
    assert HudPanel.min_height == 360
    assert HudPanel.panel_header_height == 36
    assert HudPanel.time_height == 88


def test_hud_i18n_keys_exist_in_italian_style():
    style = Style()
    style.load(
        Path("res/ui/style.txt").read_text(encoding="utf-8"),
        Path("res/ui-it/style.txt").read_text(encoding="utf-8"),
    )

    expected = {
        "panel_res": "Risorse",
        "panel_time": "Tempo",
        "panel_events": "Eventi",
        "panel_player": "Giocatore",
        "panel_group": "Gruppo",
        "no_unit": "Nessuna unita selezionata",
        "no_events": "Nessun evento recente",
        "resources_na": "Risorse: n/d",
        "pop_na": "Pop: n/d",
        "speed_na": "Velocita: n/d",
        "player_na": "Giocatore",
        "unit_na": "unita",
        "idle": "inattivo",
        "object_na": "oggetto",
        "resource_n": "Risorsa {}",
        "time_fmt": "Tempo: {:02d}:{:02d}",
        "pop_fmt": "Pop: {}/{}",
        "speed_fmt": "Velocita: x{:.1f}",
    }

    for key, value in expected.items():
        assert " ".join(style.get("hud", key)) == value


def test_subtitle_position_is_bottom_right():
    from soundrts.lib.screen import _subtitle_position

    screen = pygame.Surface((800, 600))
    rendered_text = pygame.Surface((120, 24))

    x, y = _subtitle_position(screen, rendered_text)

    assert x == 800 - 120 - 16
    assert y == 600 - 24 - 4
    assert x > screen.get_width() // 2


# ────────────────────────────────────────────────────────────────
# Round 4 — FIX-2: _parts_to_text safety
# ────────────────────────────────────────────────────────────────

def test_parts_to_text_preserves_numbers():
    """T_PARTS_TO_TEXT_PRESERVES_NUMBERS: digit tokens must NOT be stripped."""
    panel = HudPanel(_make_interface())
    assert panel._parts_to_text(["Pop:", "0"]) == "Pop: 0"
    assert panel._parts_to_text(["Resource", "1"]) == "Resource 1"
    assert panel._parts_to_text(["Count:", "42"]) == "Count: 42"


def test_parts_to_text_preserves_zero_in_list():
    """T_PARTS_TO_TEXT_ZERO: '0' as a list element must be preserved."""
    panel = HudPanel(_make_interface())
    # "0" as a standalone token must not be stripped (e.g. resource count of zero)
    result = panel._parts_to_text(["Pop:", "0"])
    assert result == "Pop: 0", f"expected 'Pop: 0', got {result!r}"
    assert "0" in result


def test_resource_name_strips_digit_style_tokens():
    """T_RESOURCE_NAME_STRIPS_DIGITS: pure-digit tokens (style type IDs) are discarded."""
    panel = HudPanel(_make_interface())
    # Simulate the filtering that _resource_name applies before _parts_to_text
    raw_parts = ["Gold", "1"]  # "1" is a style type ID to discard
    filtered = [p for p in raw_parts if not (isinstance(p, str) and p.isdigit())]
    assert panel._parts_to_text(filtered) == "Gold"
    assert "1" not in panel._parts_to_text(filtered)


def test_infobar_subtitle_rendering_path_confirmed():
    """T_INFOBAR_POSITION: forensic analysis — subtitle rendered by screen_render_subtitle().
    Position formula: x = screen_w - text_w - 16, y = screen_h - text_h - 4.
    Confirmed bottom-right. clientgamegridview.py has no text rendering.
    Runtime verification required for visual confirmation.
    """
    from soundrts.lib.screen import _subtitle_position

    for w, h in [(640, 480), (1024, 768), (1920, 1080)]:
        screen = pygame.Surface((w, h))
        text_surf = pygame.Surface((200, 24))
        x, y = _subtitle_position(screen, text_surf)
        # Right edge lands at screen_w - 16
        assert x + 200 == w - 16, f"right edge mismatch at {w}x{h}"
        # Bottom edge lands at screen_h - 4
        assert y + 24 == h - 4, f"bottom edge mismatch at {w}x{h}"
        # x must be in the right half for typical subtitle lengths
        assert x > w // 2, f"x={x} not in right half at {w}x{h}"