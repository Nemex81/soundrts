"""Round 8 - tests visual UI.

Coprono LEGGI inviolabili: gating visual_mode (LEGGE-1), backward compat
(LEGGE-5), _label_to_str safe (LEGGE-4), stack mirror (LEGGE-3),
update_menu in-place (LEGGE-7), cleanup SystemExit (LEGGE-8),
mouse additivo (LEGGE-6).
"""

import pygame
import pytest

from soundrts import clientmedia, config
from soundrts.lib.resource import ResourceStack
from soundrts.lib.sound_cache import sounds
from soundrts.paths import BASE_PACKAGE_PATH


@pytest.fixture(scope="module")
def default(request):
    clientmedia.minimal_init()
    res = ResourceStack([BASE_PACKAGE_PATH])
    sounds.load_default(res)
    request.addfinalizer(pygame.display.quit)
    return res


@pytest.fixture
def visual_off():
    """Garantisce visual_mode=0 attorno al test (LEGGE-5)."""
    prev = config.visual_mode
    config.visual_mode = 0
    yield
    config.visual_mode = prev


@pytest.fixture
def visual_on():
    """Forza visual_mode=1 senza toccare il display (no fullscreen reale)."""
    prev = config.visual_mode
    config.visual_mode = 1
    yield
    config.visual_mode = prev


def test_visual_mode_persists_in_config(default, visual_off):
    """LEGGE-5: l'opzione esiste e default e 0 (audio-only)."""
    assert hasattr(config, "visual_mode")
    assert int(config.visual_mode) == 0


def test_menu_screen_noop_when_visual_off(default, visual_off):
    """LEGGE-1: con visual_mode=0 il ScreenManager non fa nulla."""
    from soundrts.clientvisualui import get_screen_manager
    from soundrts.clientmenuscreen import MenuScreen

    sm = get_screen_manager()
    sm.cleanup()
    sm.push(MenuScreen([], [], 0))
    assert sm.current is None  # push e no-op
    sm.pop()  # pop su stack vuoto e no-op
    assert sm.handle_mouse_motion((0, 0)) is None
    assert sm.handle_mouse_click((0, 0)) is None


def test_label_to_str_safe_with_bad_tokens(default):
    """LEGGE-4: token misti, oggetti strani, mai eccezione."""
    from soundrts.clientmenuscreen import _label_to_str

    class Weird:
        def __iter__(self):
            raise RuntimeError("boom")

    # numero sconosciuto -> fallback stringa (non solleva)
    out = _label_to_str([99999])
    assert isinstance(out, str)

    # token virgola: skippato
    out2 = _label_to_str([",", "orc"])
    assert "orc" in out2

    # oggetto iterabile che esplode: ritorna ""
    out3 = _label_to_str(Weird())
    assert out3 == ""


def test_label_to_str_empty_label(default):
    """LEGGE-4: None e vuoto -> ''."""
    from soundrts.clientmenuscreen import _label_to_str

    assert _label_to_str(None) == ""
    assert _label_to_str([]) == ""
    assert _label_to_str("") == ""


def test_screen_manager_push_pop(default, visual_on, monkeypatch):
    """LEGGE-3: stack mirror push/pop con visual_mode=1, render disabilitato."""
    from soundrts.clientvisualui import get_screen_manager
    from soundrts.clientmenuscreen import MenuScreen

    sm = get_screen_manager()
    sm.cleanup()
    # disattiva render reale (nessuna superficie pygame inizializzata in test)
    monkeypatch.setattr(sm, "_render_current", lambda: None)

    a = MenuScreen("A", [], 0)
    b = MenuScreen("B", [], 0)
    sm.push(a)
    assert sm.current is a
    sm.push(b)
    assert sm.current is b
    sm.pop()
    assert sm.current is a
    sm.pop()
    assert sm.current is None


def test_screen_manager_update_inplace_no_push(default, visual_on, monkeypatch):
    """LEGGE-7: update_current modifica lo screen corrente senza push/pop."""
    from soundrts.clientvisualui import get_screen_manager
    from soundrts.clientmenuscreen import MenuScreen

    sm = get_screen_manager()
    sm.cleanup()
    monkeypatch.setattr(sm, "_render_current", lambda: None)

    s = MenuScreen("old", [["a"]], 0)
    sm.push(s)
    sm.update_current("new", [["a"], ["b"]], 1)
    assert sm.current is s
    assert s.title == "new"
    assert len(s.choices) == 2
    assert s.index == 1
    # nessun push aggiuntivo
    sm.pop()
    assert sm.current is None


def test_mouse_rect_hit_detection(default, visual_on, monkeypatch):
    """LEGGE-6: hit-test mouse usa _item_rects pre-calcolati."""
    from soundrts.clientmenuscreen import MenuScreen

    ms = MenuScreen("t", [["a"], ["b"], ["c"]], 0)
    # simula tre rect precalcolati (li userebbe render)
    ms._item_rects = [
        (pygame.Rect(0, 0, 100, 40), 0),
        (pygame.Rect(0, 40, 100, 40), 1),
        (pygame.Rect(0, 80, 100, 40), 2),
    ]
    # motion: nessun cambio se gia su quello
    assert ms.handle_mouse_motion((10, 10)) is None
    # motion: cambio idx
    assert ms.handle_mouse_motion((10, 60)) == 1
    # click ritorna l'indice del rect colpito
    assert ms.handle_mouse_click((10, 100)) == 2
    # fuori dai rect: None
    assert ms.handle_mouse_click((500, 500)) is None


def test_systemexit_cleanup(default, visual_on, monkeypatch):
    """LEGGE-8: cleanup() svuota lo stack (chiamata in finally su SystemExit)."""
    from soundrts.clientvisualui import get_screen_manager
    from soundrts.clientmenuscreen import MenuScreen

    sm = get_screen_manager()
    sm.cleanup()
    monkeypatch.setattr(sm, "_render_current", lambda: None)
    sm.push(MenuScreen("a", [], 0))
    sm.push(MenuScreen("b", [], 0))
    sm.cleanup()
    assert sm.current is None


def test_visual_mode_toggle_updates_screen(default, visual_off, monkeypatch):
    """toggle_visual_mode commuta il flag e salva config (no display reale)."""
    from soundrts import clientmedia as cm

    # blocca set_screen e config.save per evitare side-effect su disco/display
    calls = {"set_screen": [], "save": 0}
    monkeypatch.setattr(cm, "set_screen", lambda fs: calls["set_screen"].append(fs))
    monkeypatch.setattr(config, "save", lambda: calls.__setitem__("save", calls["save"] + 1))
    # azzera voice.item per evitare TTS reale
    monkeypatch.setattr(cm.voice, "item", lambda *a, **k: None)

    assert int(config.visual_mode) == 0
    cm.toggle_visual_mode()
    assert int(config.visual_mode) == 1
    cm.toggle_visual_mode()
    assert int(config.visual_mode) == 0
    assert calls["save"] == 2
    assert len(calls["set_screen"]) == 2
