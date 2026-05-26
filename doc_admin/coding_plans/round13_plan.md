# Round 13 — Sospesi R11 + Chiusura R12

Data: 2026-05-25
Stato globale: COMPLETATO
Baseline ingresso: 262 passed / 0 failed / 0 errors
Suite finale: 289 passed / 0 failed / 0 errors

## TASK-0 — Chiusura formale R12

Aggiunta sezione "Round 12 — Auto-detect lingua + HUD + Mouse" in `doc_admin/todo.md` con esito completato e i tre TODO rimandati a R13.

## TASK-1 — SOSPESO-A (WINDOWRESIZED / WINDOWSIZECHANGED)

### Valutazione utilità — Verdetto: **SCARTATO-PREMATURO**

Evidenze dal codice reale:

- `soundrts/lib/screen.py` riga 4: `from pygame.locals import FULLSCREEN`. Nessun import di `RESIZABLE`.
- `soundrts/lib/screen.py` `set_screen(fullscreen)` righe 126-149:
  - se `fullscreen=True` → `window_style = FULLSCREEN`;
  - se `fullscreen=False` e `config.visual_mode=1` → `window_style = FULLSCREEN`;
  - altrimenti → `window_style = 0` (legacy small window, audio-only).
- Nessuna chiamata a `pygame.display.set_mode(..., RESIZABLE)` in tutto il modulo `soundrts/`.
- Conseguenza: in `visual_mode=1` la finestra è SEMPRE fullscreen desktop; un resize utente non è raggiungibile fisicamente; gli eventi `WINDOWRESIZED`/`WINDOWSIZECHANGED` non vengono mai prodotti dal flusso.

CONDIZIONE-A (`visual_mode=1` usa FULLSCREEN, non RESIZABLE) → **SÌ**.
Handler = codice morto. Nessuna implementazione, nessun test runtime; solo skip documentato (vedi `test_visual_ui.py`, sezione "Round 13 SOSPESO-A").

## TASK-2 — SOSPESO-B (traduzione 4365/4366 nei cataloghi extra)

### Valutazione utilità — Verdetto: **UTILE → IMPLEMENTATO**

Evidenze:

- 11 cataloghi `res/ui-XX/tts.txt` presenti oltre a `ui/` (EN) e `ui-it/` (IT): `ui-be`, `ui-cs`, `ui-de`, `ui-es`, `ui-fr`, `ui-pl`, `ui-pt-BR`, `ui-ru`, `ui-sk`, `ui-vi`, `ui-zh`.
- Tutti privi dei token `4365` e `4366` (`Select-String -Pattern "^4365 "` → `False` su 11/11).

### Strategia

Le righe aggiunte rispettano formato `<id> <testo>` con EOL CRLF e BOM UTF-8 (coerente con i file esistenti). Il testo è stato adattato dal testo EN con la stessa struttura sintattica `<tasto>: <azione>. ...`. Le forme native dei caratteri sono UTF-8.

> ⚠️ Traduzione automatica — da verificare da madrelingua. Annotato anche in CHANGELOG.

### Implementazione

- Script `scripts/_r13_add_4365_4366.py` (idempotente, preserva BOM/EOL) ha aggiornato i file. Lo script è temporaneo e può essere rimosso.
- Test `soundrts/tests/unittests/test_i18n_hints.py`: 27 test parametrizzati (`13 locale_dirs × 2 tokens + 1 sanity`).

## TASK-3 — SOSPESO-C (allineamento `version.py`)

### Analisi `server_is_compatible()`

```python
def server_is_compatible(version):
    if version in ["1.2-c12", "1.3.0", "1.3.1"]:
        version = "0"
    return version == SERVER_COMPATIBILITY
```

Dove `SERVER_COMPATIBILITY = "0"` e `CLIENT_COMPATIBILITY = "16"`. La stringa `VERSION` **non** è usata per il confronto di protocollo.

`clientversion.py` usa `VERSION` solo per costruire l'URL del file `<major>.<minor>version.txt` su `jlpo.free.fr` (check "update available", interamente in `try/except`).

### Verdetto: **RAMO-BUMP**

- Versione attuale: `"1.3.8.1"`.
- Versione target: `"1.4.2"` (ultima sezione marcata nel CHANGELOG interno prima di Round 13).
- Rischio protocollo: nullo. Rischio update-check: l'URL passa da `1.3version.txt` a `1.4version.txt`; il check è best-effort (eccezione silenziata) e non blocca il client.

### Implementazione

- `soundrts/version.py` riga 6: `VERSION = "1.4.2"`.
- CHANGELOG.md: aggiunta sezione `[1.4.3] — 2026-05-25` con voce R13 (i18n hint + bump version.py + nota SOSPESO-A).

## Suite finale

```
.venv\Scripts\python.exe -m pytest
289 passed in 6.03s
```

Test aggiunti in Round 13: **27** (`test_i18n_hints.py`). Totale unittests aumentato da 262 a 289.

## TODO Round 14

- [ ] Revisione da madrelingua delle traduzioni `4365`/`4366` nei cataloghi `res/ui-{be,cs,de,es,fr,pl,pt-BR,ru,sk,vi,zh}` (qualità linguistica, non funzionalità).
- [ ] Pubblicazione tag `v1.4.3` quando l'operatore deciderà la release.
- [ ] Verificare se i file `1.4version.txt`/`1.4.2version.txt` esistano effettivamente sul server `jlpo.free.fr` o se serve coordinarsi con il gestore del server per popolarli.
