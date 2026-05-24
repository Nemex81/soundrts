# Round 9 - Audit Round 8 (Visual UI)

Data: 2026-05-25
Stato: REVISIONATO E CONVALIDATO

## Scope audit

File letti integralmente:

- soundrts/clientvisualui.py
- soundrts/clientmenuscreen.py
- soundrts/clientmenu.py
- soundrts/clientmedia.py
- soundrts/config.py
- soundrts/clientmain.py
- soundrts/msgparts.py
- soundrts/lib/screen.py
- soundrts/tests/unittests/test_visual_ui.py
- doc_admin/round8_visual_ui_plan.md

Verifica extra richiesta:

- soundrts/clientgame.py (separazione Ctrl+F2 gameplay)

## Verdetti punto-per-punto (B1)

1. [CONVALIDATO] FULLSCREEN GATE (LEGGE R8-1)
   - `clientvisualui.py`: metodi visivi gated da `if not config.visual_mode: return`.
   - `clientmenuscreen.py`: `render` e hit-test menu gated; dialog mouse e no-op (safe).

2. [CONVALIDATO] STACK MIRROR (LEGGE R8-3)
   - `ScreenManager` non decide navigazione; push/pop solo da agganci `Menu.run`.

3. [REVISIONE NECESSARIA -> ESEGUITA] UPDATE IN-PLACE (LEGGE R8-7)
   - Gap trovato: `Menu.update_menu()` non propagava update a `ScreenManager`.
   - Fix applicato: `Menu.update_menu()` ora chiama `get_screen_manager().update_current(...)` in try/except quando `visual_mode=1`.

4. [REVISIONE NECESSARIA -> ESEGUITA] SYSTEMEXIT CLEANUP (LEGGE R8-8)
   - Gap trovato: `set_and_launch_mod()` / `set_and_launch_soundpack()` non chiamavano `cleanup()` prima di `SystemExit`.
   - Fix applicato in `clientmain.py`: cleanup esplicito su `get_screen_manager()` prima del raise.

5. [CONVALIDATO] MOUSE ADDITIVO (LEGGE R8-6)
   - `MOUSEMOTION`/`MOUSEBUTTONDOWN` gestiti in ramo dedicato senza rimuovere logica tastiera.

6. [CONVALIDATO] CONFIG BACKWARD COMPAT (LEGGE R8-5)
   - `visual_mode` default `0` in `_options`; converter inferito `int`.

7. [CONVALIDATO] CTRL+F2 SEPARAZIONE CONTESTI
   - Menu: `Ctrl+F2 -> toggle_visual_mode()`.
   - Gameplay (`clientgame.cmd_fullscreen`): `toggle_fullscreen()` invariato.

8. [CONVALIDATO] VOCE OPZIONI DINAMICA
   - `options_menu()` usa `VISUAL_MODE_ON/OFF` in base a `config.visual_mode`.

9. [CONVALIDATO] LABEL SAFE
   - `_label_to_str` gestisce `None`, vuoto, token non traducibili, iterable che solleva, oggetti non-string.

## Verifica test (B2)

Stato iniziale test Round 8:

- 9 test presenti e verdi.

Gap rilevato:

- Mancava test esplicito su `DialogScreen.update_input()`.
- Mancava test diretto sulla propagazione `Menu.update_menu()` -> `ScreenManager.update_current()`.

Estensione eseguita:

- aggiunti 2 test in `test_visual_ui.py`:
  - `test_menu_update_menu_syncs_visual_stack`
  - `test_dialog_screen_update_input`

Esito target suite visual UI:

- 11 passed.

## Correzioni eseguite (B3)

Gravita media (completezza/coerenza):

- `soundrts/clientmenu.py`: update in-place stack visivo in `update_menu()`.
- `soundrts/clientmain.py`: cleanup stack visivo prima di `SystemExit` in set_mod/set_soundpack.
- `soundrts/tests/unittests/test_visual_ui.py`: +2 test di copertura.

Gravita alta:

- Nessuna regressione funzionale bloccante trovata oltre ai due gap sopra (corretti).

Punti rimandati:

- Nessuno in ambito specifico Round 8 audit.

## Convalida finale audit

Suite completa (B4):

- 238 passed / 3 failed / 2 errors
- Nessun errore di collection da deprecazione locale.
- Nessuna nuova failure introdotta rispetto a post-A.

Verdetto finale:

- ROUND 8 REVISIONATO E CONVALIDATO
