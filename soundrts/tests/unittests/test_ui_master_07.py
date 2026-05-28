"""Tests for UI-MASTER-07 round.

Coverage matrix (mandatory minimum per round task):

* P0-OPTIONS-FIX: ``soundrts.options`` no longer triggers ``optparse``
  parsing at import time. The previous top-level ``_parse_options()``
  call exited with ``SystemExit: 2`` whenever ``sys.argv`` contained
  tokens not recognised by the SoundRTS CLI (e.g. pytest path
  arguments).
* P1-UNIT-SELECTION: ``GridView.display_object`` draws a
  ``_SELECTION_HIGHLIGHT_COLOR`` rect-highlight around units whose id
  belongs to ``interface.group``. Units outside the group keep the
  legacy rendering, and an empty group must not crash the render path.
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pytest


# ---------------------------------------------------------------------------
# P0-OPTIONS-FIX
# ---------------------------------------------------------------------------


def test_import_options_does_not_invoke_parser():
    """Re-importing ``soundrts.options`` must never call ``sys.exit``.

    UI-MASTER-07/P0: regression guard for the import-time parsing bug
    that broke ``python -m pytest <path>`` invocations.
    """
    # Force a clean import so we exercise the module-level statements.
    sys.modules.pop("soundrts.options", None)
    # Inject an argv that the SoundRTS parser would reject ("--xyz" is
    # not a registered option). If parse_args ran at import time this
    # would raise SystemExit(2).
    saved_argv = sys.argv
    sys.argv = ["pytest", "--xyz", "unknown"]
    try:
        import soundrts.options as opts  # noqa: F401 — import is the test
    finally:
        sys.argv = saved_argv
    assert opts.port == 2500  # default still intact


def test_parse_args_help_exits_cleanly():
    """``parse_args(['--help'])`` must use optparse's own ``SystemExit(0)``."""
    from soundrts import options as opts

    with pytest.raises(SystemExit) as excinfo:
        opts.parse_args(["--help"])
    # optparse exits with code 0 for --help.
    assert excinfo.value.code == 0


def test_parse_args_overrides_port():
    """``parse_args(['-p', '3000'])`` must update ``options.port``."""
    from soundrts import options as opts

    original = opts.port
    try:
        opts.parse_args(["-p", "3000"])
        assert opts.port == 3000
    finally:
        opts.parse_args(["-p", str(original)])  # restore for the rest


def test_legacy_alias_points_to_parse_args():
    """Back-compat alias ``_parse_options`` must remain wired."""
    from soundrts import options as opts

    assert opts._parse_options is opts.parse_args


# ---------------------------------------------------------------------------
# P1-UNIT-SELECTION
# ---------------------------------------------------------------------------


class _DummySurface:
    """Minimal pygame.Surface stand-in for blit/set_at/draw calls."""

    def blit(self, *_args, **_kwargs):
        return None

    def set_at(self, *_args, **_kwargs):
        return None


def _make_grid_view(group_ids):
    """Build a ``GridView`` wired with the bare minimum collaborators."""
    from soundrts import clientgamegridview

    player = SimpleNamespace(allied=[], world=None)
    interface = SimpleNamespace(
        target=None,
        group=list(group_ids),
        player=player,
        square_width=1,
    )
    gv = clientgamegridview.GridView(interface)
    gv._y_offset = 0
    gv.square_view_width = 32
    gv.square_view_height = 32
    gv.ymax = 32
    # ``R`` (and ``R2``) are module-level globals normally set by
    # ``_update_coefs``; the tests skip that path, so seed a sane
    # value here.
    clientgamegridview.R = 6
    clientgamegridview.R2 = 36
    # Bypass _object_coords (depends on the world geometry).
    gv._object_coords = lambda _o: (50, 50)
    return gv, clientgamegridview


def _make_unit(unit_id, *, in_player_group=False, with_player=True):
    """Build a unit object compatible with ``display_object``."""
    player_obj = SimpleNamespace(allied=[], units=[])
    model = SimpleNamespace(player=player_obj if with_player else None)
    unit = SimpleNamespace(
        id=unit_id,
        is_inside=False,
        shape=lambda: "circle",
        collision=True,
        corrected_color=lambda: (200, 200, 200),
        model=model,
        player=player_obj,
        hp=None,
        hp_max=None,
    )
    unit.player.player_is_an_enemy = lambda _other: False
    if in_player_group:
        # Caller already adds the id to interface.group.
        pass
    return unit


@pytest.fixture(autouse=True)
def _silence_pygame_display(monkeypatch):
    """Avoid touching the real screen during the gridview tests."""
    from soundrts.lib import screen as screen_mod

    monkeypatch.setattr(screen_mod, "get_screen", lambda: _DummySurface())
    # Some helpers in clientgamegridview import ``get_screen`` directly.
    from soundrts import clientgamegridview as cgv

    monkeypatch.setattr(cgv, "get_screen", lambda: _DummySurface())
    yield


def test_selection_highlight_drawn_for_grouped_unit():
    """Units in ``interface.group`` get the ``_SELECTION_HIGHLIGHT_COLOR`` rect."""
    gv, cgv = _make_grid_view(group_ids=[42])
    unit = _make_unit(42)
    gv.interface.player = unit.player  # ensure the colour branch runs

    with patch.object(cgv, "draw_rect") as draw_rect_mock, \
            patch.object(cgv.pygame.draw, "circle"):
        gv.display_object(unit)

    highlight_calls = [
        call for call in draw_rect_mock.call_args_list
        if call.args and call.args[0] == cgv._SELECTION_HIGHLIGHT_COLOR
    ]
    assert highlight_calls, "expected rect-highlight for grouped unit"
    # Border-only rendering: width argument must be 2.
    assert highlight_calls[0].args[2] == 2


def test_selection_highlight_skipped_outside_group():
    """Units not in the group must NOT receive the highlight rect."""
    gv, cgv = _make_grid_view(group_ids=[1, 2, 3])
    unit = _make_unit(99)  # id outside the group
    gv.interface.player = unit.player

    with patch.object(cgv, "draw_rect") as draw_rect_mock, \
            patch.object(cgv.pygame.draw, "circle"):
        gv.display_object(unit)

    highlight_calls = [
        call for call in draw_rect_mock.call_args_list
        if call.args and call.args[0] == cgv._SELECTION_HIGHLIGHT_COLOR
    ]
    assert highlight_calls == []


def test_display_object_with_empty_group_does_not_crash():
    """``interface.group == []`` is the steady-state UI: must render cleanly."""
    gv, cgv = _make_grid_view(group_ids=[])
    unit = _make_unit(7)
    gv.interface.player = unit.player

    with patch.object(cgv, "draw_rect"), patch.object(cgv.pygame.draw, "circle"):
        # No assertion needed — the test passes if no exception is raised.
        gv.display_object(unit)
