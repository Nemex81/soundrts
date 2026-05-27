"""Unit tests for 7-level speed system and Paradox-style pause."""
import sys
import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# options.py calls parse_args() at import time using sys.argv;
# strip pytest args so optparse does not choke on them.
if len(sys.argv) > 1:
    sys.argv = [sys.argv[0]]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_game_interface():
    """Return a minimal GameInterface-like object sufficient for speed/pause tests."""
    from soundrts import config as cfg

    iface = SimpleNamespace(
        speed=cfg.speed,
        is_paused=False,
        waiting_for_world_update=False,
        next_update=time.time() - 1.0,  # already due
        server=MagicMock(),
    )
    return iface


# ---------------------------------------------------------------------------
# OBIETTIVO 1 — 7 speed levels
# ---------------------------------------------------------------------------

SPEED_LEVELS = [
    (1, 0.25),
    (2, 0.5),
    (3, 1.0),
    (4, 2.0),
    (5, 3.0),
    (6, 4.0),
    (7, 5.0),
]


@pytest.mark.parametrize("level,expected_speed", SPEED_LEVELS)
def test_gm_speed_n_sends_correct_speed(level, expected_speed):
    """Each gm_speed_N() must call server.write_line('speed X') with the correct value."""
    from soundrts.clientgame import GameInterface

    server = MagicMock()
    server.interface = None

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)
        gi.server = server

    method = getattr(gi, f"gm_speed_{level}")
    method()

    server.write_line.assert_called_once_with(f"speed {expected_speed}")


def test_all_seven_gm_speed_methods_exist():
    """All seven gm_speed_N methods must be defined on GameInterface."""
    from soundrts.clientgame import GameInterface

    for n in range(1, 8):
        assert hasattr(GameInterface, f"gm_speed_{n}"), f"gm_speed_{n} missing"


def test_old_speed_methods_removed():
    """Old convenience methods should no longer exist."""
    from soundrts.clientgame import GameInterface

    for old in ("gm_slow_speed", "gm_normal_speed", "gm_fast_speed", "gm_very_fast_speed"):
        assert not hasattr(GameInterface, old), f"{old} should have been removed"


def test_speed_constants_in_msgparts():
    """All SET_SPEED_N constants must be defined in msgparts."""
    import soundrts.msgparts as mp

    for n in range(1, 8):
        name = f"SET_SPEED_{n}"
        assert hasattr(mp, name), f"mp.{name} missing"
        value = getattr(mp, name)
        assert isinstance(value, list) and len(value) == 1, f"mp.{name} must be [int]"


# ---------------------------------------------------------------------------
# OBIETTIVO 2 — Paradox-style pause
# ---------------------------------------------------------------------------

def test_is_paused_initialised_false():
    """GameInterface.__init__ must set is_paused = False."""
    from soundrts.clientgame import GameInterface

    server = MagicMock()
    server.interface = None

    with (
        patch("soundrts.clientgame.GridView"),
        patch("soundrts.clientgame.HudPanel"),
        patch("soundrts.clientgame.psounds"),
        patch("soundrts.clientgame.voice"),
        patch("soundrts.clientgame.Bindings"),
        patch("soundrts.clientgame.queue.Queue"),
    ):
        gi = GameInterface(server)

    assert gi.is_paused is False


def test_time_to_ask_blocks_when_paused():
    """_time_to_ask_for_next_update() must return False when is_paused is True."""
    from soundrts.clientgame import GameInterface

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)

    gi.is_paused = True
    gi.waiting_for_world_update = False
    gi.next_update = time.time() - 1.0  # would normally be True

    assert gi._time_to_ask_for_next_update() is False


def test_time_to_ask_proceeds_when_not_paused():
    """_time_to_ask_for_next_update() must work normally when is_paused is False."""
    from soundrts.clientgame import GameInterface

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)

    gi.is_paused = False
    gi.waiting_for_world_update = False
    gi.next_update = time.time() - 1.0  # past due

    assert gi._time_to_ask_for_next_update() is True


def test_cmd_toggle_pause_toggles_state():
    """cmd_toggle_pause() must alternate is_paused between False and True."""
    from soundrts.clientgame import GameInterface

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)

    gi.is_paused = False
    gi.next_update = time.time()

    with patch("soundrts.clientgame.voice") as mock_voice:
        gi.cmd_toggle_pause()
        assert gi.is_paused is True
        mock_voice.item.assert_called_once()

        mock_voice.item.reset_mock()
        gi.cmd_toggle_pause()
        assert gi.is_paused is False
        mock_voice.item.assert_called_once()


def test_cmd_toggle_pause_resets_next_update_on_resume():
    """Resuming from pause must set next_update to ~now so the loop fires immediately."""
    from soundrts.clientgame import GameInterface

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)

    gi.is_paused = True
    # Set next_update far in the future to simulate a frozen game
    gi.next_update = time.time() + 9999.0

    with patch("soundrts.clientgame.voice"):
        gi.cmd_toggle_pause()  # resume

    assert gi.next_update <= time.time() + 0.1  # reset to ~now


def test_pause_msgparts_constants():
    """PAUSE_ON and PAUSE_OFF must be defined in msgparts."""
    import soundrts.msgparts as mp

    assert hasattr(mp, "PAUSE_ON"), "mp.PAUSE_ON missing"
    assert hasattr(mp, "PAUSE_OFF"), "mp.PAUSE_OFF missing"
    assert isinstance(mp.PAUSE_ON, list) and len(mp.PAUSE_ON) == 1
    assert isinstance(mp.PAUSE_OFF, list) and len(mp.PAUSE_OFF) == 1


# ---------------------------------------------------------------------------
# OBIETTIVO 3 — Retrocompatibilità save file (__setstate__)
# ---------------------------------------------------------------------------

def test_setstate_without_is_paused_in_dict():
    """__setstate__ must set is_paused=False even when the dictionary (pre-Task1 save)
    does not contain the key — prevents AttributeError in _time_to_ask_for_next_update."""
    from soundrts.clientgame import GameInterface

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)

    # Simulate a pre-Task1 save dictionary without 'is_paused'
    old_save_dict = {
        "speed": 1.0,
        "waiting_for_world_update": False,
        "next_update": 0.0,
    }
    with (
        patch("soundrts.clientgame.HudPanel"),
        patch("soundrts.clientgame.psounds"),
        patch("soundrts.clientgame.queue.Queue"),
    ):
        gi.__setstate__(old_save_dict)

    assert gi.is_paused is False, "is_paused must be False after __setstate__ without key"


def test_setstate_resets_is_paused_to_false_on_load():
    """__setstate__ must always reset is_paused to False on game load,
    even if the save was made while paused."""
    from soundrts.clientgame import GameInterface

    with patch.object(GameInterface, "__init__", lambda self, *a, **kw: None):
        gi = GameInterface.__new__(GameInterface)

    # Simulate a save-while-paused dictionary
    paused_save_dict = {
        "speed": 1.0,
        "is_paused": True,
        "waiting_for_world_update": False,
        "next_update": 0.0,
    }
    with (
        patch("soundrts.clientgame.HudPanel"),
        patch("soundrts.clientgame.psounds"),
        patch("soundrts.clientgame.queue.Queue"),
    ):
        gi.__setstate__(paused_save_dict)

    assert gi.is_paused is False, "is_paused must be reset to False on game load"
