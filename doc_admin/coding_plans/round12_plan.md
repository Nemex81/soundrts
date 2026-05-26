# Round 12 — Piano Tecnico

**Data:** 2026-05-26
**Versione target:** 1.4.2
**Suite baseline:** 245 passed → finale: 262 passed (+17)

---

## TASK-1 — Auto-detect lingua dal locale di sistema

**Problema (PROBLEMA-1):** `_preferred_language()` in `soundrts/lib/resource.py`
restituiva immediatamente `"en"` quando `cfg/language.txt` era assente (IOError),
ignorando il locale del sistema operativo. Risultato: la Visual UI mostrava
stringhe in inglese anche su sistemi configurati in italiano (o altra lingua).

**Causa radice:**
```python
# PRIMA (bug)
except IOError:
    warning("couldn't read cfg/language.txt")
    return "en"  # ← early return errato
```

**Fix applicati:**
1. `soundrts/lib/resource.py` — aggiunta `_normalize_locale_code()` per gestire
   il formato Windows `"Italian_Italy"` via `locale.normalize("italian")` → `"it"`.
   Fix `_preferred_language()`: IOError imposta `cfg = ""` invece di `return "en"`,
   poi rileva la lingua via `locale.getlocale()` con normalizzazione.

2. `soundrts/clientmain.py` — aggiunta `_seed_language_file()` chiamata dopo
   `locale.setlocale(LC_ALL, "")`. Scrive il codice ISO in `cfg/language.txt`
   se assente o vuoto; non sovrascrive mai scelte esplicite dell'utente.
   Senza mai bloccare l'avvio (except generico silenzioso).

**Note architetturali:**
- `preferred_language` è una costante di modulo — inizializza a import time.
- `version.py` importa `resource.py` PRIMA che `locale.setlocale()` venga chiamato
  in `clientmain.py`. Il fix in `resource.py` garantisce il funzionamento nella
  run corrente; il seed in `clientmain.py` prepara le run successive.
- Windows locale: `locale.getlocale()` → `"Italian_Italy"`;
  `locale.normalize("italian")` → `"it_IT.ISO8859-1"` → split → `"it"`. ✓

---

## TASK-2 — Mouse nel gameplay visivo

**Problema (PROBLEMA-2):** Richiesta di abilitare il mouse nel gameplay visivo.

**Esito dell'analisi:** Il mouse nel gameplay era **già completamente implementato**
in `soundrts/clientgame.py` (implementazione dei round precedenti):

- `_process_fullscreen_mode_mouse_event(self, e)` — handler completo:
  - `MOUSEMOTION` → seleziona casella/target, aggiorna cursore
  - `MOUSEBUTTONDOWN button=1` (sx) — se ordine attivo: `cmd_validate()`; altrimenti
    imposta `mouse_select_origin` per drag-select
  - `MOUSEBUTTONDOWN button=3` (dx) — su casella valida: `cmd_default()`
  - `MOUSEBUTTONUP button=1` — click: `cmd_command_unit()`; drag: selezione gruppo
- Guard: `elif self.display_is_active:` in `_process_events()` — no mouse in audio mode.
- `display_is_active`: `get_fullscreen() or IS_DEV_VERSION`

**Azione:** Nessuna modifica al codice. Aggiunti 7 test strutturali e comportamentali
che documentano e proteggono la funzionalità esistente.

---

## TASK-3 — Etichette HUD risorse localizzate ("Resource 1/2" → "oro/legno")

**Problema (PROBLEMA-3):** L'HUD visivo mostrava "Resource 1: 500" e "Resource 2: 200"
invece dei nomi localizzati ("oro"/"legno" in italiano, "gold"/"wood" in inglese).

**Causa radice:** In `clientgamehud.py`, `_resource_name()` filtrava i token
numerici con `p.isdigit()` invece di risolverli:
```python
# PRIMA (bug)
parts = [p for p in parts if not (isinstance(p, str) and p.isdigit())]
# → ["131"] diventa [] → label = "" → fallback "Resource 1"
```

Il file `res/ui/style.txt` ha già:
```
resource_0_title 131   # → "gold"/"oro"
resource_1_title 132   # → "wood"/"legno"
```
e `res/ui/tts.txt` + `res/ui-it/tts.txt` contengono i token 131/132/133.

**Fix applicato** (`soundrts/clientgamehud.py`):
- Aggiunta importazione `from .lib.sound_cache import sounds`
- `_resource_name()` ora risolve token numerici via `sounds.translate_sound_number(int(p))`
  invece di scartarli. Se la traduzione è ancora un digit (sounds non caricati →
  test unitari), filtra e cade nel fallback "Resource N". Test legacy pass invariati.

---

## Suite

| Fase | Risultato |
|------|-----------|
| Baseline pre-R12 | 245 passed / 0 failed |
| Post-modifiche codice | 245 passed / 0 failed |
| Post-nuovi test | 262 passed / 0 failed |

Nuovi test: +17 (+6 T1, +7 T2, +4 T3)
