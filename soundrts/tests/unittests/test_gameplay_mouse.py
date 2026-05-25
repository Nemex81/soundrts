"""Round 12 - TASK-2: mouse nel gameplay visivo.

La gestione mouse era gia' implementata in soundrts.clientgame.GameInterface
nei round precedenti (_process_fullscreen_mode_mouse_event).

Questi test verificano:
  - il metodo handler esiste ed e' chiamabile
  - display_is_active e' una property (guard visual-mode)
  - click sinistro senza ordine attivo imposta mouse_select_origin
  - click destro su casella valida chiama cmd_default
  - click centrale (button=2) non genera azioni
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pygame
import pytest


# ---------------------------------------------------------------------------
# Fixture: inizializza pygame una volta sola (serve per pygame.key.get_mods())
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


# ---------------------------------------------------------------------------
# Helper: stub minimale di GameInterface senza istanziarlo davvero
# ---------------------------------------------------------------------------

def _make_stub():
    """Crea un stub MagicMock con i soli attributi richiesti dall'handler."""
    stub = MagicMock()
    stub.hud_panel.handle_mouse_event.return_value = False
    # Simula assenza di ordine attivo (nessun target da selezionare)
    stub.an_order_requiring_a_target_is_selected = False
    stub.target = None
    stub.mouse_select_origin = None
    # Casella valida dal grid_view
    mock_square = MagicMock()
    stub.grid_view.square_from_mousepos.return_value = mock_square
    stub.grid_view.object_from_mousepos.return_value = None
    stub.place = mock_square  # stessa casella → nessun say_square
    return stub


def _btn_event(event_type, button, pos=(100, 100)):
    """Costruisce un pygame.event.Event di tipo mouse button."""
    return pygame.event.Event(event_type, {"button": button, "pos": pos})


# ---------------------------------------------------------------------------
# Test strutturali (read-only, non richiedono inizializzazione game)
# ---------------------------------------------------------------------------

def test_mouse_handler_method_exists():
    """_process_fullscreen_mode_mouse_event deve esistere in GameInterface."""
    from soundrts.clientgame import GameInterface

    assert callable(
        getattr(GameInterface, "_process_fullscreen_mode_mouse_event", None)
    ), "Il metodo handler mouse non esiste"


def test_display_is_active_is_property():
    """display_is_active deve essere una property usata come guard."""
    from soundrts.clientgame import GameInterface

    assert isinstance(
        GameInterface.__dict__.get("display_is_active"), property
    ), "display_is_active deve essere una property"


# ---------------------------------------------------------------------------
# Test comportamentali tramite stub
# ---------------------------------------------------------------------------

def test_left_click_without_active_order_sets_mouse_select_origin():
    """Click sinistro senza ordine attivo: imposta mouse_select_origin = e.pos."""
    from soundrts.clientgame import GameInterface

    stub = _make_stub()
    e = _btn_event(pygame.MOUSEBUTTONDOWN, button=1, pos=(120, 80))
    GameInterface._process_fullscreen_mode_mouse_event(stub, e)

    # Dopo il click sinistro senza ordine, mouse_select_origin deve essere impostato
    assert stub.mouse_select_origin == (120, 80), (
        f"Atteso mouse_select_origin=(120,80), ottenuto {stub.mouse_select_origin}"
    )


def test_right_click_on_valid_square_calls_cmd_default():
    """Click destro su casella valida deve chiamare cmd_default()."""
    from soundrts.clientgame import GameInterface

    stub = _make_stub()
    e = _btn_event(pygame.MOUSEBUTTONDOWN, button=3, pos=(100, 100))
    GameInterface._process_fullscreen_mode_mouse_event(stub, e)

    stub.cmd_default.assert_called(), "cmd_default deve essere chiamato"


def test_right_click_on_empty_area_does_not_call_cmd_default():
    """Click destro su area vuota (no casella) non chiama cmd_default."""
    from soundrts.clientgame import GameInterface

    stub = _make_stub()
    stub.grid_view.square_from_mousepos.return_value = None  # area vuota
    e = _btn_event(pygame.MOUSEBUTTONDOWN, button=3, pos=(0, 0))
    GameInterface._process_fullscreen_mode_mouse_event(stub, e)

    stub.cmd_default.assert_not_called()


def test_middle_click_does_not_trigger_any_command():
    """Click centrale (button=2) non deve chiamare cmd_default ne' cmd_validate."""
    from soundrts.clientgame import GameInterface

    stub = _make_stub()
    e = _btn_event(pygame.MOUSEBUTTONDOWN, button=2, pos=(100, 100))
    GameInterface._process_fullscreen_mode_mouse_event(stub, e)

    stub.cmd_default.assert_not_called()
    stub.cmd_validate.assert_not_called()


def test_left_click_with_active_order_calls_cmd_validate():
    """Click sinistro con ordine attivo deve chiamare cmd_validate()."""
    from soundrts.clientgame import GameInterface

    stub = _make_stub()
    stub.an_order_requiring_a_target_is_selected = True
    e = _btn_event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
    GameInterface._process_fullscreen_mode_mouse_event(stub, e)

    stub.cmd_validate.assert_called()
