"""Unit tests for Round UI-MASTER-01 (T3/T4/T6 + new mouse commands).

These tests exercise small, deterministic behaviours of the visual HUD
helpers added in this round; they avoid spinning up pygame or a real
GameInterface and instead mock the dependencies that are not relevant
for the unit under test.
"""
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# options.py parses sys.argv at import time; strip pytest args first.
if len(sys.argv) > 1:
    sys.argv = [sys.argv[0]]


# ---------------------------------------------------------------------------
# T3/T4 — HudPanel state defaults & toggle helpers
# ---------------------------------------------------------------------------

def _make_hud():
    """Build a HudPanel against a mock interface (no pygame side effects)."""
    from soundrts.clientgamehud import HudPanel

    interface = MagicMock()
    interface.player = None
    return HudPanel(interface)


def test_hud_panel_defaults_events_visible_true():
    hud = _make_hud()
    assert hud.events_visible is True


def test_hud_panel_defaults_activity_hidden_tab_all():
    hud = _make_hud()
    assert hud.activity_visible is False
    assert hud.activity_tab == "all"


def test_hud_classify_order_training():
    hud = _make_hud()
    order = SimpleNamespace(cls=SimpleNamespace(keyword="train"))
    assert hud._classify_order(order) == "training"


def test_hud_classify_order_research():
    hud = _make_hud()
    order = SimpleNamespace(cls=SimpleNamespace(keyword="research"))
    assert hud._classify_order(order) == "research"


def test_hud_classify_order_build_and_upgrade():
    hud = _make_hud()
    o_build = SimpleNamespace(cls=SimpleNamespace(keyword="build"))
    o_upg = SimpleNamespace(cls=SimpleNamespace(keyword="upgrade_to"))
    assert hud._classify_order(o_build) == "build"
    assert hud._classify_order(o_upg) == "build"


def test_hud_classify_order_unknown_returns_empty():
    hud = _make_hud()
    o = SimpleNamespace(cls=SimpleNamespace(keyword="move"))
    assert hud._classify_order(o) == ""


def test_hud_collect_activity_handles_missing_player():
    hud = _make_hud()
    # `interface.player` is None on the mocked interface above, but
    # MagicMock auto-creates attributes. Force the None to assert the
    # defensive guard returns an empty list.
    hud.interface.player = None
    assert hud._collect_activity() == []


def test_hud_collect_activity_aggregates_units():
    hud = _make_hud()
    train_order = SimpleNamespace(
        cls=SimpleNamespace(keyword="train"),
        type=SimpleNamespace(type_name="soldier"),
        time=10,
        time_cost=20,
    )
    research_order = SimpleNamespace(
        cls=SimpleNamespace(keyword="research"),
        type=SimpleNamespace(type_name="metal_armor"),
        time=5,
        time_cost=20,
    )
    u1 = SimpleNamespace(orders=[train_order])
    u2 = SimpleNamespace(orders=[research_order])
    u3 = SimpleNamespace(orders=[])  # idle — excluded
    hud.interface.player = SimpleNamespace(units=[u1, u2, u3])
    out = hud._collect_activity()
    kinds = sorted(o[0] for o in out)
    names = sorted(o[1] for o in out)
    assert kinds == ["research", "training"]
    assert names == ["metal_armor", "soldier"]
    # progress percentage: train = (1 - 10/20) * 100 = 50
    train_entry = next(o for o in out if o[0] == "training")
    assert train_entry[2] == 50


# ---------------------------------------------------------------------------
# T3 — cmd_toggle_events on GameInterface
# ---------------------------------------------------------------------------

def test_cmd_toggle_events_flips_state_and_voices():
    from soundrts import clientgame
    from soundrts import msgparts as mp

    iface = MagicMock()
    iface.hud_panel = SimpleNamespace(events_visible=True)
    with patch.object(clientgame, "voice") as voice_mock:
        clientgame.GameInterface.cmd_toggle_events(iface)
        assert iface.hud_panel.events_visible is False
        voice_mock.item.assert_called_once_with(mp.EVENTS_HIDDEN)
        voice_mock.reset_mock()
        clientgame.GameInterface.cmd_toggle_events(iface)
        assert iface.hud_panel.events_visible is True
        voice_mock.item.assert_called_once_with(mp.EVENTS_SHOWN)


def test_cmd_toggle_events_safe_when_hud_missing():
    """When hud_panel is None the command must not raise."""
    from soundrts import clientgame

    iface = SimpleNamespace(hud_panel=None)
    # Must not raise.
    clientgame.GameInterface.cmd_toggle_events(iface)


# ---------------------------------------------------------------------------
# T4 — cmd_toggle_activity_panel + tab selectors
# ---------------------------------------------------------------------------

def test_cmd_toggle_activity_panel_flips():
    from soundrts import clientgame
    from soundrts import msgparts as mp

    iface = MagicMock()
    iface.hud_panel = SimpleNamespace(activity_visible=False)
    with patch.object(clientgame, "voice") as voice_mock:
        clientgame.GameInterface.cmd_toggle_activity_panel(iface)
    assert iface.hud_panel.activity_visible is True
    voice_mock.item.assert_called_once_with(mp.ACTIVITY_PANEL_SHOWN)


def test_cmd_activity_tab_training_sets_state_and_opens_panel():
    from soundrts import clientgame
    from soundrts import msgparts as mp

    # Use a SimpleNamespace and bind _set_activity_tab as a method so the
    # public cmd_activity_tab_* method dispatches to the real helper.
    iface = SimpleNamespace(
        hud_panel=SimpleNamespace(activity_visible=False, activity_tab="all"),
    )
    iface._set_activity_tab = clientgame.GameInterface._set_activity_tab.__get__(iface)
    with patch.object(clientgame, "voice") as voice_mock:
        clientgame.GameInterface.cmd_activity_tab_training(iface)
    assert iface.hud_panel.activity_tab == "training"
    assert iface.hud_panel.activity_visible is True
    voice_mock.item.assert_called_once_with(mp.ACTIVITY_TAB_TRAINING)


# ---------------------------------------------------------------------------
# T6 — display_is_active honours config.visual_mode
# ---------------------------------------------------------------------------

def test_display_is_active_true_when_visual_mode_enabled():
    from soundrts import clientgame
    from soundrts import config as cfg

    iface = SimpleNamespace()
    original = getattr(cfg, "visual_mode", 0)
    try:
        cfg.visual_mode = 1
        with patch.object(clientgame, "get_fullscreen", return_value=False), \
             patch.object(clientgame, "IS_DEV_VERSION", False):
            assert clientgame.GameInterface.display_is_active.fget(iface) is True
    finally:
        cfg.visual_mode = original


def test_display_is_active_false_when_all_off():
    from soundrts import clientgame
    from soundrts import config as cfg

    iface = SimpleNamespace()
    original = getattr(cfg, "visual_mode", 0)
    try:
        cfg.visual_mode = 0
        with patch.object(clientgame, "get_fullscreen", return_value=False), \
             patch.object(clientgame, "IS_DEV_VERSION", False):
            assert clientgame.GameInterface.display_is_active.fget(iface) is False
    finally:
        cfg.visual_mode = original


# ---------------------------------------------------------------------------
# T2 — GridView y_offset is positive and shifts coordinates
# ---------------------------------------------------------------------------

def test_grid_view_get_view_coords_applies_y_offset():
    """When _y_offset > 0, the y returned by _get_view_coords_from_world_coords
    is shifted downwards by exactly that offset (compared to the
    unshifted formula).
    """
    from soundrts.clientgamegridview import GridView

    iface = SimpleNamespace(square_width=1000)
    gv = GridView(iface)
    gv.square_view_width = 10
    gv.square_view_height = 10
    gv.ymax = 100
    gv._y_offset = 60
    x, y = gv._get_view_coords_from_world_coords(0, 0)
    # base formula (no offset): y = ymax = 100. With offset: 160.
    assert y == 160
    assert x == 0


def test_grid_view_get_rect_applies_y_offset():
    from soundrts.clientgamegridview import GridView

    iface = SimpleNamespace()
    gv = GridView(iface)
    gv.square_view_width = 10
    gv.square_view_height = 10
    gv.ymax = 100
    gv._y_offset = 60
    left, top, w, h = gv._get_rect_from_map_coords(0, 9)  # top-row square
    # top = y_offset + ymax - (9+1)*10 = 60 + 100 - 100 = 60
    assert top == 60
    assert left == 0


# ---------------------------------------------------------------------------
# T1 — Localization coverage: each tts.txt has IDs 4367..4383
# ---------------------------------------------------------------------------

def test_all_languages_have_round_tts_ids():
    import re
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    res = repo_root / "res"
    expected = [
        4367, 4368, 4369, 4370, 4371, 4372, 4373, 4374, 4375,  # T1
        4376, 4377,                                              # T3
        4378, 4379, 4380, 4381, 4382, 4383,                      # T4
    ]
    files = [res / "ui" / "tts.txt"] + sorted(
        (res / d.name / "tts.txt") for d in res.iterdir()
        if d.is_dir() and d.name.startswith("ui-")
    )
    assert files, "no tts.txt found"
    missing = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        for i in expected:
            if not re.search(rf"(?m)^{i}\s", text):
                missing.append((p.relative_to(repo_root).as_posix(), i))
    assert missing == [], (
        "missing TTS entries: " + ", ".join(f"{p}->{i}" for p, i in missing)
    )
