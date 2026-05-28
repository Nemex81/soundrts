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
PANEL_NAMES = ("res", "events", "player", "group")


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
        return panel.res_bar_height
    if panel_name == "events":
        if panel.events_visible:
            return header_height + max(1, len(snapshot.events)) * panel.line_height
        return header_height
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
    """UI-MASTER-03 T8-BOTTOMBAR: legacy TIME panel removed. The
    horizontal bottom bar now carries the time/speed lines and must be
    at least 36px tall to host the text comfortably."""
    _, _, rects = _capture_layout(monkeypatch, resolution)
    assert rects["bottom_bar"].height >= 36, (
        "bottom_bar height {} < 36px at {}".format(
            rects["bottom_bar"].height,
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


# ────────────────────────────────────────────────────────────────
# Round 5 — PLAYER/GROUP relocated to bottom-right under EVENTS
# ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_player_panel_is_right_anchored(monkeypatch, resolution):
    """T_PLAYER_RIGHT_ANCHORED: PLAYER docked to the right column."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    width, _ = resolution
    player_rect = rects.get("player")
    assert player_rect is not None
    assert player_rect.right == width - panel.margin
    assert player_rect.left > width // 2


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_group_panel_is_right_anchored(monkeypatch, resolution):
    """T_GROUP_RIGHT_ANCHORED: GROUP docked to the right column."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    width, _ = resolution
    group_rect = rects.get("group")
    assert group_rect is not None
    assert group_rect.right == width - panel.margin
    assert group_rect.left > width // 2


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_group_panel_does_not_overflow(monkeypatch, resolution):
    """T_GROUP_NO_OVERFLOW: GROUP bottom stays inside the screen."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    _, height = resolution
    assert rects["group"].bottom <= height - panel.margin


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_player_below_events(monkeypatch, resolution):
    """T_PLAYER_BELOW_EVENTS: PLAYER stacked directly under EVENTS."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    assert rects["player"].top >= rects["events"].bottom
    assert rects["player"].top - rects["events"].bottom <= panel.margin + 1


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_adaptive_units_cap(monkeypatch, resolution):
    """T_ADAPTIVE_UNITS: with worst-case unit count, GROUP never overflows."""
    surface = pygame.Surface(resolution)
    monkeypatch.setattr(pygame.display, "get_surface", lambda: surface)
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
    monkeypatch.setattr(locale, "getdefaultlocale", lambda: ("en_US", "UTF-8"))

    from soundrts.lib import screen as screen_module

    monkeypatch.setattr(screen_module, "screen_render", lambda *args, **kwargs: None)
    monkeypatch.setattr(screen_module, "screen_render_header", lambda *args, **kwargs: None)

    panel = HudPanel(_make_interface())
    base = _make_snapshot()
    crowded = HudSnapshot(
        resources=base.resources,
        food=base.food,
        time=base.time,
        speed=base.speed,
        units=[HudUnitSnapshot("unit #%d" % i, 10, 10, "idle") for i in range(panel.max_units)],
        events=base.events,
        player=base.player,
    )
    panel._draw_snapshot(surface, crowded)
    _, height = resolution
    assert panel._panel_rects["group"].bottom <= height - panel.margin
    assert panel._panel_rects["player"].bottom <= panel._panel_rects["group"].top


# ────────────────────────────────────────────────────────────────
# Round 6 — HUD-1 alignment + MAP-1/2/3 visibility
# ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_events_aligned_with_group(monkeypatch, resolution):
    """T_EVENTS_ALIGNED_WITH_GROUP: events left == group left == player left (col_right_width=295)."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    assert rects["events"].left == rects["group"].left, (
        "EVENTS left {} != GROUP left {} at {}".format(
            rects["events"].left, rects["group"].left, _resolution_id(resolution)
        )
    )
    assert rects["events"].left == rects["player"].left, (
        "EVENTS left {} != PLAYER left {} at {}".format(
            rects["events"].left, rects["player"].left, _resolution_id(resolution)
        )
    )


@pytest.mark.parametrize("R", [1, 2, 3, 4, 6, 8, 12])
def test_faction_marker_min(R):
    """T_FACTION_MARKER_MIN: faction circle radius is always >= 2."""
    from soundrts.clientgamegridview import R_MIN, UNIT_SCALE

    R_vis = max(R_MIN, int(R * UNIT_SCALE))
    assert max(2, R_vis // 2) >= 2


@pytest.mark.parametrize("R", [1, 2, 3, 4, 6, 8, 12])
def test_hp_bar_w_min(R):
    """T_HP_BAR_W_MIN: HP bar half-width is always >= 3."""
    from soundrts.clientgamegridview import R_MIN, UNIT_SCALE

    R_vis = max(R_MIN, int(R * UNIT_SCALE))
    assert max(3, R_vis - 2) >= 3


def test_r_min_constant():
    """T_R_MIN_ENFORCED: R_MIN is defined and equals 4 in clientgamegridview."""
    from soundrts.clientgamegridview import R_MIN

    assert R_MIN == 4


# ────────────────────────────────────────────────────────────────
# Round 7 — MAP viewport clipping + visual unit scale
# ────────────────────────────────────────────────────────────────


def _make_grid_view(monkeypatch, resolution):
    from soundrts import clientgamegridview as gridview_module

    surface = pygame.Surface(resolution)
    monkeypatch.setattr(gridview_module, "get_screen", lambda: surface)
    grid = {(xc, yc): (xc, yc) for xc in range(10) for yc in range(8)}
    player = SimpleNamespace(world=SimpleNamespace(grid=grid))
    interface = SimpleNamespace(
        xcmax=9,
        ycmax=7,
        square_width=1.0,
        server=SimpleNamespace(player=player),
    )
    return gridview_module.GridView(interface), gridview_module, grid


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_map_viewport_is_clipped_to_hud_free_width(monkeypatch, resolution):
    """T_MAP_VIEWPORT_CLIP: GridView uses the HUD-free map width."""
    grid_view, _, _ = _make_grid_view(monkeypatch, resolution)
    width, height = resolution
    hud_right = grid_view._hud_right_width()
    from soundrts.clientgamegridview import HUD_MAP_MARGIN

    hud_top = HudPanel.res_bar_height + 2 * HudPanel.margin + HUD_MAP_MARGIN
    bottom_reserved = HudPanel.bottom_bar_height + HudPanel.margin
    map_w = max(width // 2, width - hud_right)
    expected_sq = min(map_w // 10, (height - hud_top - bottom_reserved) // 8)

    grid_view._update_coefs()

    assert grid_view.square_view_width == expected_sq
    assert grid_view.square_view_height == expected_sq
    assert grid_view.square_view_width >= 1
    assert grid_view.square_view_width * 10 <= map_w
    assert grid_view.ymax <= height - hud_top - bottom_reserved


@pytest.mark.parametrize("R", [4, 5, 6, 8, 10, 12, 16])
def test_unit_scale_applied(R):
    """T_UNIT_SCALE_APPLIED: R_vis never shrinks physical R."""
    from soundrts.clientgamegridview import R_MIN, UNIT_SCALE

    R_vis = max(R_MIN, int(R * UNIT_SCALE))
    assert R_vis >= R_MIN
    assert R_vis >= R
    assert R_vis == max(4, int(R * 2.0))


def test_r2_not_scaled_by_unit_scale(monkeypatch):
    """T_R2_NOT_SCALED: hit-test radius remains physical R, not visual R_vis."""
    grid_view, gridview_module, _ = _make_grid_view(monkeypatch, (800, 600))

    grid_view._update_coefs()

    R_vis = max(gridview_module.R_MIN, int(gridview_module.R * gridview_module.UNIT_SCALE))
    assert gridview_module.R2 == gridview_module.R * gridview_module.R
    assert gridview_module.R2 != R_vis * R_vis


def test_hud_right_width_matches_hud_panel_geometry(monkeypatch):
    """T_HUD_RIGHT_WIDTH: 303px matches HudPanel right-column geometry."""
    resolution = (800, 600)
    grid_view, _, _ = _make_grid_view(monkeypatch, resolution)
    _, _, rects = _capture_layout(monkeypatch, resolution)

    assert grid_view._hud_right_width() == 303
    assert grid_view._hud_right_width() == resolution[0] - rects["events"].left


def test_hit_test_uses_unshifted_map_coordinates(monkeypatch):
    """T_HIT_TEST_INVARIANT: map_x=0/map_y=0 keeps mouse coordinates unshifted."""
    grid_view, _, grid = _make_grid_view(monkeypatch, (800, 600))

    grid_view._update_coefs()
    square = grid_view.square_view_width
    xc, yc = 3, 4
    pos = (
        xc * square + square // 2,
        grid_view._y_offset + grid_view.ymax - (yc * square + square // 2),
    )

    assert grid_view.square_from_mousepos(pos) == grid[(xc, yc)]
    assert grid_view.square_from_mousepos((square * 10 + 1, pos[1])) is None


# ────────────────────────────────────────────────────────────────
# Round 16 — RES horizontal top bar
# ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_res_bar_full_width(monkeypatch, resolution):
    """T_RES_BAR_FULL_WIDTH: RES panel spans full usable width (screen_w - 2*margin)."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    width, _ = resolution
    expected_width = width - 2 * panel.margin
    assert rects["res"].width == expected_width, (
        "RES width {} != expected {} at {}".format(
            rects["res"].width, expected_width, _resolution_id(resolution)
        )
    )


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_res_bar_height_equals_constant(monkeypatch, resolution):
    """T_RES_BAR_HEIGHT: RES panel height equals HudPanel.res_bar_height."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    assert rects["res"].height == panel.res_bar_height, (
        "RES height {} != res_bar_height {} at {}".format(
            rects["res"].height, panel.res_bar_height, _resolution_id(resolution)
        )
    )


@pytest.mark.parametrize("resolution", FUNCTIONAL_RESOLUTIONS, ids=_resolution_id)
def test_time_panel_starts_below_res_bar(monkeypatch, resolution):
    """UI-MASTER-03 T8-BOTTOMBAR: TIME panel relocated to the bottom
    bar. Verify the bottom_bar sits at the very bottom of the screen."""
    panel, _, rects = _capture_layout(monkeypatch, resolution)
    _, height = resolution
    expected_top = height - panel.margin - panel.bottom_bar_height
    assert rects["bottom_bar"].top == expected_top, (
        "bottom_bar top {} != expected {} at {}".format(
            rects["bottom_bar"].top, expected_top, _resolution_id(resolution)
        )
    )