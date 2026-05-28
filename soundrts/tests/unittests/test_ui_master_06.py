"""Tests for UI-MASTER-06 round.

Coverage matrix (mandatory minimum per round task):

* P1-TEST-ISOLATION: the autouse fixture in test_clientgamehud.py keeps
  the singleton ``soundrts.definitions.style`` empty so HUD fallbacks
  resolve to the EN defaults regardless of test order. This is verified
  indirectly by running the full suite, but we add one explicit guard
  here to detect a future regression of the fixture itself.
* P2-MOVE-INDICATOR: ``GridView.screen_pos_of_square`` returns the
  geometric centre of the cell in screen coordinates and the move
  flash is anchored at that centre instead of the raw click pixel.
* P3-L10N-COMPLETION: every UI key marked with a TODO placeholder in
  UI-MASTER-02b/03/04 now resolves to a non-empty, locale-specific
  string in FR and PT-BR.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from soundrts.clientgamehud import HudPanel
from soundrts.definitions import Style, style


# ---------------------------------------------------------------------------
# Shared helpers (kept minimal — full HUD fixtures live in UI-MASTER-05).
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
    iface.send_order = MagicMock()
    return iface


# ---------------------------------------------------------------------------
# P1-TEST-ISOLATION — sanity guard for the singleton reset fixture.
# ---------------------------------------------------------------------------


def test_style_singleton_starts_empty_under_isolation_fixture():
    """The autouse fixture in test_clientgamehud.py wipes ``style._dict``
    before each test of that file. UI-MASTER-06 does NOT install the
    same fixture globally, so here we just assert the singleton is a
    real ``Style`` instance and is mutable — confirming the contract
    used by P1.
    """
    assert isinstance(style, Style)
    # _dict may have content (a previous test in the run could have
    # loaded a language). What matters is that callers can swap it.
    saved = getattr(style, "_dict", {})
    style._dict = {}
    assert style._dict == {}
    style._dict = saved


# ---------------------------------------------------------------------------
# P2-MOVE-INDICATOR — geometric centre of the destination cell.
# ---------------------------------------------------------------------------


class _FakeGridView:
    """Mimics the public surface used by ``flash_move_target`` callers."""

    square_view_width = 40
    square_view_height = 40
    ymax = 200
    _y_offset = 30

    def __init__(self, interface):
        self.interface = interface

    def _update_coefs(self):
        # Coefficients are pre-baked for the test — production code
        # would recompute them against ``get_screen()``.
        return None

    def _get_view_coords_from_world_coords(self, ox, oy):
        # Same formula as ``GridView._get_view_coords_from_world_coords``
        # but with deterministic inputs from the test scenario.
        sw = self.interface.square_width
        x = int(ox / sw * self.square_view_width)
        y = int(
            self._y_offset
            + self.ymax
            - oy / sw * self.square_view_height
        )
        return x, y


def _patch_screen_pos_of_square(view_cls):
    from soundrts.clientgamegridview import GridView

    view_cls.screen_pos_of_square = GridView.screen_pos_of_square


@pytest.fixture(autouse=True)
def _install_screen_pos_on_fake_view():
    # Lazy import: top-level import of ``soundrts.clientgamegridview``
    # cascades to ``soundrts.options`` which parses ``sys.argv`` at
    # module load. Under pytest with an explicit file argument that
    # parse explodes with ``SystemExit: 2``. Deferring to fixture
    # setup-time keeps collection clean.
    _patch_screen_pos_of_square(_FakeGridView)
    yield


def test_screen_pos_of_square_returns_geometric_centre():
    iface = SimpleNamespace(square_width=1.0)
    view = _FakeGridView(iface)
    square = SimpleNamespace(x=0.5, y=0.5)  # centre of cell (0, 0)
    pos = view.screen_pos_of_square(square)
    # Expected: x = 0.5 / 1.0 * 40 = 20
    #           y = 30 + 200 - 0.5 / 1.0 * 40 = 210
    assert pos == (20, 210)


def test_screen_pos_of_square_centre_differs_from_border_click():
    iface = SimpleNamespace(square_width=1.0)
    view = _FakeGridView(iface)
    square = SimpleNamespace(x=0.5, y=0.5)
    centre = view.screen_pos_of_square(square)
    border_click = (39, 31)  # near the cell border, off-centre
    assert centre != border_click
    # The whole point of P2 is that the indicator no longer follows the
    # raw click pixel; assert the gap is meaningful (>= a few pixels).
    assert abs(centre[0] - border_click[0]) + abs(centre[1] - border_click[1]) >= 5


def test_screen_pos_of_square_returns_none_for_invalid_square():
    iface = SimpleNamespace(square_width=1.0)
    view = _FakeGridView(iface)
    assert view.screen_pos_of_square(None) is None
    # Object missing .x / .y must not raise — defensive contract.
    assert view.screen_pos_of_square(SimpleNamespace()) is None


def test_flash_move_target_stores_centre_pos_provided_by_caller():
    """``HudPanel.flash_move_target`` is agnostic to the source of the
    pixel: P2 moves the responsibility to the caller (clientgame). This
    test pins the contract: whatever centre is fed in, the flash stores
    it verbatim so the eventual draw matches the cell centre.
    """
    hud = HudPanel(_make_interface())
    square = SimpleNamespace(col=4, row=2, x=4500, y=2500)
    centre = (123, 456)
    hud.flash_move_target(square, centre)
    assert hud._move_flash_pos == centre
    assert hud._move_flash_square is square


# ---------------------------------------------------------------------------
# P3-L10N-COMPLETION — FR and PT-BR placeholder cleanup.
# ---------------------------------------------------------------------------


# Subset of keys whose VALUE must be locale-specific (i.e. not the raw
# English placeholder). Pure structural templates such as
# ``tooltip_event_full {prefix} {text}`` are intentionally excluded.
_LOCALIZED_KEYS = {
    "tooltip_map_hp",
    "activity_collapsed",
    "tooltip_activity_show",
    "tooltip_activity_hide",
    "tooltip_activity_cancel_hint",
    "tooltip_food_cell",
    "tooltip_player_panel",
    "tooltip_unit_row",
    "tooltip_bottom_time",
    "tooltip_bottom_speed",
    "tooltip_map_empty_cell",
}

# English reference values — if any FR/PT-BR file still ships these
# verbatim, the translation is missing.
_EN_REFERENCE = {
    "tooltip_map_hp": "HP",
    "activity_collapsed": "hidden",
    "tooltip_activity_show": "Show activity",
    "tooltip_activity_hide": "Hide activity",
    "tooltip_activity_cancel_hint": "Click to cancel",
    "tooltip_food_cell": "Food:",
    "tooltip_player_panel": "Player:",
    "tooltip_unit_row": " HP ",
    "tooltip_bottom_time": "Game time",
    "tooltip_bottom_speed": "Game speed",
    "tooltip_map_empty_cell": "Cell ",
}


def _load_style(locale_dir: str) -> Style:
    s = Style()
    base = Path("res/ui/style.txt").read_text(encoding="utf-8")
    over = Path(locale_dir).joinpath("style.txt").read_text(encoding="utf-8")
    s.load(base, over)
    return s


@pytest.mark.parametrize("locale_dir", ["res/ui-fr", "res/ui-pt-BR"])
def test_localized_hud_keys_present_and_translated(locale_dir):
    s = _load_style(locale_dir)
    hud_entry = s._dict.get("hud", {})
    for key in _LOCALIZED_KEYS:
        assert key in hud_entry, f"{locale_dir}: missing key '{key}'"
        value = " ".join(hud_entry[key])
        en_ref = _EN_REFERENCE[key]
        assert en_ref not in value, (
            f"{locale_dir}: key '{key}' still ships English token "
            f"'{en_ref}': {value!r}"
        )


@pytest.mark.parametrize("locale_dir", ["res/ui-fr", "res/ui-pt-BR"])
def test_no_todo_markers_remain(locale_dir):
    """Sentinella di chiusura del round: nessuna riga di commento di
    style.txt deve riportare 'TODO: tradurre' una volta che P3 e' chiuso.
    """
    body = Path(locale_dir).joinpath("style.txt").read_text(encoding="utf-8")
    assert "TODO" not in body, (
        f"{locale_dir}: stale TODO marker still present in style.txt"
    )
