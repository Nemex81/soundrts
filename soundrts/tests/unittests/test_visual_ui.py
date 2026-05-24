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


def test_visual_footer_hints_use_localized_msgparts(default):
    """Round 11: i footer Visual UI usano token msgparts, non testo hardcoded."""
    from soundrts import clientvisualui as vui
    from soundrts import msgparts as mp
    from soundrts.clientmenuscreen import _label_to_str
    from soundrts.lib.sound_cache import sounds

    assert vui.FOOTER_HINT_MENU == mp.VISUAL_MENU_HINT
    assert vui.FOOTER_HINT_DIALOG == mp.VISUAL_DIALOG_HINT
    assert _label_to_str(vui.FOOTER_HINT_MENU) == sounds.translate_sound_number(4365)
    assert _label_to_str(vui.FOOTER_HINT_DIALOG) == sounds.translate_sound_number(4366)


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


def test_menu_update_menu_syncs_visual_stack(default, visual_on, monkeypatch):
    """Audit Round 9: Menu.update_menu aggiorna ScreenManager in-place."""
    from soundrts.clientmenu import Menu
    import soundrts.clientmenu as cmenu

    class DummySM:
        def __init__(self):
            self.calls = []

        def update_current(self, title, choices, index):
            self.calls.append((title, choices, index))

    sm = DummySM()
    monkeypatch.setattr(cmenu, "get_screen_manager", lambda: sm)

    m = Menu(["old"], [(["a"], lambda: None)])
    m.choice_index = 0
    m.update_menu(Menu(["new"], [(["a"], lambda: None), (["b"], lambda: None)]))
    assert len(sm.calls) == 1
    assert sm.calls[0][0] == ["new"]
    assert len(sm.calls[0][1]) == 2


def test_dialog_screen_update_input(default, visual_on):
    """Audit Round 9: DialogScreen.update_input sostituisce il testo corrente."""
    from soundrts.clientmenuscreen import DialogScreen

    d = DialogScreen(["prompt"], "abc")
    assert d.current_input == "abc"
    d.update_input("xyz")
    assert d.current_input == "xyz"
    d.update_input("")
    assert d.current_input == ""


def test_mouse_button_right_click_ignored(default, visual_on, monkeypatch):
    """B1.4: MOUSEBUTTONDOWN con button != 1 non conferma la scelta.

    Solo il click sinistro (button=1) deve attivare _confirm_choice.
    Click destro (button=2,3) e scroll (4,5) devono essere ignorati.
    """
    import soundrts.clientmenu as cmenu
    from soundrts.clientmenu import Menu

    choices = [([1], lambda: None), ([2], lambda: None)]
    m = Menu(["title"], choices)
    m.choice_index = 0

    confirm_calls = []
    monkeypatch.setattr(m, "_confirm_choice", lambda: confirm_calls.append(1))
    # blocca voice.update usato in _try_to_get_choice
    monkeypatch.setattr(cmenu.voice, "update", lambda: None)

    class FakeCurrent:
        def handle_mouse_click(self, pos):
            return 0  # indice 0 sempre in area

    class FakeSM:
        current = FakeCurrent()

    monkeypatch.setattr(cmenu, "get_screen_manager", lambda: FakeSM())

    # button=2 (click destro): nessuna conferma
    ev_right = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=2)
    m._try_to_get_choice(ev_right)
    assert len(confirm_calls) == 0, "click destro non deve confermare"

    # button=4 (scroll): nessuna conferma
    ev_scroll = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=4)
    m._try_to_get_choice(ev_scroll)
    assert len(confirm_calls) == 0, "scroll non deve confermare"

    # button=1 (click sinistro): conferma
    ev_left = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=1)
    m._try_to_get_choice(ev_left)
    assert len(confirm_calls) == 1, "click sinistro deve confermare"
