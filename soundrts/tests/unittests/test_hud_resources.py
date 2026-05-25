"""Round 12 - TASK-3: etichette HUD risorse via token TTS localizzato.

I token resource_0_title (131 -> "gold"/"oro") e resource_1_title (132 ->
"wood"/"legno") sono definiti in res/ui/style.txt e risolti tramite il
sistema TTS di soundrts.lib.sound_cache.sounds.

Questi test verificano:
  CASO-A  senza stile/suoni caricati → fallback "Resource N" (regression guard)
  CASO-B  con stile caricato ma suoni assenti → risoluzione numerica forzata
  CASO-C  metodo _resource_name risponde correttamente al token numerico
  CASO-D  il sistema di risoluzione si comporta correttamente con sounds mock
"""

from unittest.mock import MagicMock, patch

import pytest

from soundrts.clientgamehud import HudPanel


# ---------------------------------------------------------------------------
# Stub minimale per HudPanel (identico a test_clientgamehud.py)
# ---------------------------------------------------------------------------

class _DummyInterface:
    display_is_active = False
    resources = [500, 200]
    used_food = 3
    available_food = 10
    last_virtual_time = 125
    speed = 1.0
    group = []
    dobjets = {}

    def _get_relative_speed(self):
        return 1.0


# ---------------------------------------------------------------------------
# CASO-A: regression guard — nessun stile ne' suoni caricati -> "Resource N"
# ---------------------------------------------------------------------------

def test_resource_name_fallback_without_style(monkeypatch):
    """CASO-A: stile non caricato -> _resource_name ritorna 'Resource 1'/'Resource 2'."""
    # Assicura che style.get() ritorni None (stile non caricato)
    from soundrts import definitions
    original_get = definitions.style.get

    def _get_returns_none(section, key):
        return None

    monkeypatch.setattr(definitions.style, "get", _get_returns_none)

    panel = HudPanel(_DummyInterface())
    snapshot = panel.get_snapshot()

    assert "Resource 1: 500" in snapshot.resources[0], (
        f"Atteso 'Resource 1: 500', ottenuto '{snapshot.resources[0]}'"
    )
    assert "Resource 2: 200" in snapshot.resources[1], (
        f"Atteso 'Resource 2: 200', ottenuto '{snapshot.resources[1]}'"
    )


# ---------------------------------------------------------------------------
# CASO-B: stile caricato con token numerico, sounds mock che ritorna testo
# ---------------------------------------------------------------------------

def test_resource_name_resolves_numeric_token_via_sounds(monkeypatch):
    """CASO-B: token 131 -> sounds.translate_sound_number(131) = 'gold' -> 'gold: 500'."""
    from soundrts import definitions
    from soundrts.lib import sound_cache

    # Simula stile caricato: resource_0_title -> ["131"], resource_1_title -> ["132"]
    def _mock_style_get(section, key):
        if key == "resource_0_title":
            return ["131"]
        if key == "resource_1_title":
            return ["132"]
        return None

    # Simula sounds che ritorna testi localizzati
    def _mock_translate(n):
        return {131: "gold", 132: "wood"}.get(n, str(n))

    monkeypatch.setattr(definitions.style, "get", _mock_style_get)
    monkeypatch.setattr(sound_cache.sounds, "translate_sound_number", _mock_translate)

    panel = HudPanel(_DummyInterface())
    snapshot = panel.get_snapshot()

    assert "gold" in snapshot.resources[0].lower(), (
        f"Atteso 'gold' nella stringa risorsa, ottenuto '{snapshot.resources[0]}'"
    )
    assert "wood" in snapshot.resources[1].lower(), (
        f"Atteso 'wood' nella stringa risorsa, ottenuto '{snapshot.resources[1]}'"
    )


# ---------------------------------------------------------------------------
# CASO-C: sounds.translate_sound_number ritorna digit -> fallback "Resource N"
# ---------------------------------------------------------------------------

def test_resource_name_falls_back_when_translate_returns_digit(monkeypatch):
    """CASO-C: translate_sound_number(131) ritorna '131' (digit) -> fallback."""
    from soundrts import definitions
    from soundrts.lib import sound_cache

    def _mock_style_get(section, key):
        if key == "resource_0_title":
            return ["131"]
        return None

    # Simula sounds non inizializzati: ritorna stringa numerica
    def _mock_translate(n):
        return str(n)  # "131" — ancora un digit

    monkeypatch.setattr(definitions.style, "get", _mock_style_get)
    monkeypatch.setattr(sound_cache.sounds, "translate_sound_number", _mock_translate)

    panel = HudPanel(_DummyInterface())
    snapshot = panel.get_snapshot()

    assert "Resource 1" in snapshot.resources[0], (
        f"Atteso fallback 'Resource 1: 500', ottenuto '{snapshot.resources[0]}'"
    )


# ---------------------------------------------------------------------------
# CASO-D: sounds mock con token IT (oro/legno)
# ---------------------------------------------------------------------------

def test_resource_name_italian_tokens(monkeypatch):
    """CASO-D: token 131/132 risolti con testi italiani 'oro'/'legno'."""
    from soundrts import definitions
    from soundrts.lib import sound_cache

    def _mock_style_get(section, key):
        if key == "resource_0_title":
            return ["131"]
        if key == "resource_1_title":
            return ["132"]
        return None

    def _mock_translate(n):
        return {131: "oro", 132: "legno"}.get(n, str(n))

    monkeypatch.setattr(definitions.style, "get", _mock_style_get)
    monkeypatch.setattr(sound_cache.sounds, "translate_sound_number", _mock_translate)

    panel = HudPanel(_DummyInterface())
    snapshot = panel.get_snapshot()

    assert "oro" in snapshot.resources[0].lower(), (
        f"Atteso 'oro' (IT), ottenuto '{snapshot.resources[0]}'"
    )
    assert "legno" in snapshot.resources[1].lower(), (
        f"Atteso 'legno' (IT), ottenuto '{snapshot.resources[1]}'"
    )
