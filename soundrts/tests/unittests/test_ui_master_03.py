"""Unit tests for Round UI-MASTER-03.

Coverage:
- C1-HITTEST: rect_for / panel_names public API.
- T7-COORD: (col,row) coordinates appended to the map tooltip.
- T8-BOTTOMBAR: horizontal bottom bar replaces the TIME panel.
- T8-ACTIVITY: ACTIVITY header always visible; click toggles state;
  row rects + tooltip; body fits above bottom_bar.
"""
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame


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


def _draw(hud, snap, size=(800, 600)):
    screen = pygame.Surface(size)
    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header"):
        hud._draw_snapshot(screen, snap)
    return screen


# ---------------------------------------------------------------------------
# C1-HITTEST
# ---------------------------------------------------------------------------

def test_rect_for_returns_none_for_unknown():
    hud = _make_hud()
    assert hud.rect_for("nonexistent_panel") is None


def test_rect_for_returns_rect_after_draw():
    hud = _make_hud()
    _draw(hud, _snapshot())
    assert isinstance(hud.rect_for("res"), pygame.Rect)
    assert hud.rect_for("events_header") is not None


def test_panel_names_not_empty_after_draw():
    hud = _make_hud()
    _draw(hud, _snapshot())
    names = hud.panel_names()
    assert isinstance(names, tuple)
    assert len(names) > 0
    assert "res" in names


# ---------------------------------------------------------------------------
# T7-COORD
# ---------------------------------------------------------------------------

def test_tooltip_includes_coords_when_square_given():
    hud = _make_hud()
    entity = SimpleNamespace(type_name="orc", hp=10, hp_max=10)
    square = SimpleNamespace(col=3, row=7)
    text = hud._build_map_tooltip(entity, (0, 0), square=square)
    assert "3" in text
    assert "7" in text


def test_tooltip_no_coords_when_square_none():
    hud = _make_hud()
    entity = SimpleNamespace(type_name="orc", hp=10, hp_max=10)
    text = hud._build_map_tooltip(entity, (0, 0), square=None)
    assert "None" not in text
    assert "(," not in text


def test_set_map_hover_accepts_square_kwarg():
    hud = _make_hud()
    entity = SimpleNamespace(type_name="orc")
    square = SimpleNamespace(col=1, row=2)
    # Should not raise.
    hud.set_map_hover(entity, (50, 50), square=square)
    assert hud._map_hover_square is square


def test_tooltip_skips_coords_if_square_missing_attrs():
    hud = _make_hud()
    entity = SimpleNamespace(type_name="orc")
    square = SimpleNamespace()  # no col/row
    text = hud._build_map_tooltip(entity, (0, 0), square=square)
    assert "None" not in text


# ---------------------------------------------------------------------------
# T8-BOTTOMBAR
# ---------------------------------------------------------------------------

def test_bottom_bar_rect_registered():
    hud = _make_hud()
    _draw(hud, _snapshot())
    assert hud.rect_for("bottom_bar") is not None


def test_bottom_bar_top_position():
    hud = _make_hud()
    _draw(hud, _snapshot(), size=(800, 600))
    bar = hud.rect_for("bottom_bar")
    assert bar.top == 600 - hud.margin - hud.bottom_bar_height


def test_time_panel_not_in_panel_names():
    hud = _make_hud()
    _draw(hud, _snapshot())
    assert "time" not in hud.panel_names()


def test_bottom_bar_full_width():
    hud = _make_hud()
    _draw(hud, _snapshot(), size=(1024, 768))
    bar = hud.rect_for("bottom_bar")
    assert bar.width == 1024 - 2 * hud.margin


# ---------------------------------------------------------------------------
# T8-ACTIVITY
# ---------------------------------------------------------------------------

def test_activity_header_always_visible():
    hud = _make_hud()
    hud.activity_visible = False
    _draw(hud, _snapshot())
    assert hud.rect_for("activity_header") is not None


def test_activity_header_click_toggles_visible():
    hud = _make_hud()
    hud.activity_visible = False
    _draw(hud, _snapshot())
    header = hud.rect_for("activity_header")
    click = SimpleNamespace(
        type=pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=(header.centerx, header.centery),
    )
    consumed = hud.handle_mouse_event(click)
    assert consumed is True
    assert hud.activity_visible is True


def test_activity_rows_visible_when_open():
    hud = _make_hud()
    hud.activity_visible = True
    # Inject two fake activity items via _collect_activity patch.
    with patch.object(
        type(hud), "_collect_activity",
        return_value=[("training", "orc", 42), ("build", "tower", 10)],
    ):
        _draw(hud, _snapshot())
    assert hud.rect_for("activity_row_0") is not None
    assert hud.rect_for("activity_row_1") is not None


def test_activity_tooltip_on_row():
    hud = _make_hud()
    hud.activity_visible = True
    with patch.object(
        type(hud), "_collect_activity",
        return_value=[("training", "orc", 42)],
    ):
        _draw(hud, _snapshot())
    row = hud.rect_for("activity_row_0")
    assert row is not None
    hud._update_tooltip((row.centerx, row.centery))
    assert hud._tooltip_text != ""
    assert "42" in hud._tooltip_text


def test_activity_tooltip_on_header_show_hide():
    hud = _make_hud()
    hud.activity_visible = False
    _draw(hud, _snapshot())
    header = hud.rect_for("activity_header")
    hud._update_tooltip((header.centerx, header.centery))
    # tooltip_activity_show is defined in style.txt (EN: "Show activity")
    assert hud._tooltip_text != ""


def test_activity_body_fits_above_bottom_bar():
    hud = _make_hud()
    hud.activity_visible = True
    with patch.object(
        type(hud), "_collect_activity",
        return_value=[("training", "u", 50)],
    ):
        _draw(hud, _snapshot(), size=(800, 600))
    row = hud.rect_for("activity_row_0")
    bar = hud.rect_for("bottom_bar")
    assert row is not None and bar is not None
    assert row.bottom <= bar.top


def test_activity_header_hidden_label_uses_activity_collapsed_key():
    # When activity_visible is False the header label must include the
    # localized "(hidden)" suffix (style key: activity_collapsed).
    from soundrts.clientgamehud import HudPanel

    hud = _make_hud()
    hud.activity_visible = False
    captured = []

    def fake_header(text, pos, color=None):
        captured.append(text)

    with patch("soundrts.lib.screen.screen_render"), \
         patch("soundrts.lib.screen.screen_render_header", side_effect=fake_header):
        hud._draw_snapshot(pygame.Surface((800, 600)), _snapshot())
    activity_labels = [t for t in captured if "ACTIVITY" in t or "ATTIVIT" in t.upper()]
    assert any("(" in t for t in activity_labels), captured


# ---------------------------------------------------------------------------
# Localization sanity
# ---------------------------------------------------------------------------

def test_en_it_style_have_ui_master_03_keys():
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    expected = [
        "bottom_bar_time_fmt",
        "bottom_bar_speed_fmt",
        "activity_collapsed",
        "tooltip_activity_show",
        "tooltip_activity_hide",
    ]
    for rel in ("res/ui/style.txt", "res/ui-it/style.txt"):
        text = (repo_root / rel).read_text(encoding="utf-8", errors="replace")
        missing = [key for key in expected if key not in text]
        assert missing == [], f"{rel} missing {missing}"
        # tooltip_map_entity must now include the {coords} placeholder.
        assert "{coords}" in text, f"{rel} tooltip_map_entity missing {{coords}}"
