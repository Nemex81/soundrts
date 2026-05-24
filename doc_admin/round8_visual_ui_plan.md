# Round 8 — Visual UI Mode (Piano Tecnico)

Data: 2026-05-25
Stato: IN PROGRESS
Protocollo: DUSU-ORCH-REV v3

## Sommario

Aggiunta modalita visiva opzionale fullscreen per menu, sotto-menu e dialoghi
di input. Comportamento audio-only invariato quando `visual_mode=0` (default).

## Analisi discrepanze (FASE 0)

| # | Discrepanza | Decisione |
|---|-------------|-----------|
| D1 | Ctrl+F2 in `clientmenu._process_keydown` gia chiama `toggle_fullscreen` | In menu Ctrl+F2 viene rimappato su `toggle_visual_mode`. In gameplay (`clientgame.py:2119`) resta `toggle_fullscreen`. |
| D2 | `msgparts.VISUAL_MODE_ON/OFF` non esistono | Alias di `DISPLAY_ON` (=4206) e `DISPLAY_OFF` (=4207). Audio gia presente, semantica utente coerente. |
| D3 | `Menu.run()` non ha return esplicito finale | `try/finally` per push/pop visivo intorno al blocco audio. |
| D4 | `set_screen(fullscreen)` parametro = gameplay flag | Quando `fullscreen=False` e `config.visual_mode`, usa FULLSCREEN desktop. Gameplay invariato. |
| D5 | Converter `config._options` inferito da `type(default)` | Default `0` (int) → converter `int`. Compat. ConfigParser. |
| D6 | `_label_to_str` riusa pattern di `_first_letter` | OK: `sounds.translate_sound_number(n)` con try/except per token. |

## File toccati

### Creati
- `soundrts/clientvisualui.py` — `ScreenManager`, palette, layout, singleton `_screen_manager`.
- `soundrts/clientmenuscreen.py` — `MenuScreen`, `DialogScreen`, `_label_to_str`.
- `soundrts/tests/unittests/test_visual_ui.py` — 9 test.

### Modificati
- `soundrts/config.py` — aggiunge `("general", "visual_mode", 0)` in `_options`.
- `soundrts/lib/screen.py` — `set_screen()` ramo `visual_mode` per menu fullscreen.
- `soundrts/clientmedia.py` — `toggle_visual_mode()`, `get_visual_mode()`.
- `soundrts/clientmenu.py` — 4 agganci chirurgici + Ctrl+F2 rimappato su `toggle_visual_mode`.
- `soundrts/clientmain.py` — voce dinamica in `options_menu()`.
- `soundrts/msgparts.py` — alias `VISUAL_MODE_ON`, `VISUAL_MODE_OFF`.
- `CHANGELOG.md`, `doc_admin/todo.md`.

### Non toccati (LEGGE-2 audio invariante)
- `clientgame.py` (gameplay), `worldclient.py`, `clientmedia.toggle_fullscreen`,
  voice/sounds/psounds.

## Agganci esatti

| Hook | File | Riga riferimento | Tipo |
|------|------|------------------|------|
| H1 | `clientmenu.Menu.run` | ~290 (inizio metodo) | push MenuScreen |
| H2 | `clientmenu.Menu._say_choice` | ~125 | update_current |
| H3 | `clientmenu.Menu._try_to_get_choice` | ~265 | handle_mouse |
| H4 | `clientmenu.Menu.run` | ~295 (try/finally) | pop |
| H5 | `clientmenu.Menu._process_keydown` | ~178 (K_F2+CTRL) | rimappa toggle_visual_mode |
| H6 | `clientmain.options_menu` | 317 | voce visual_mode dinamica |

## Dipendenze e ordine

1. `config.py` (visual_mode default 0)
2. `lib/screen.py` (set_screen ramo visivo)
3. `clientmedia.py` (toggle_visual_mode)
4. `clientvisualui.py` (ScreenManager)
5. `clientmenuscreen.py` (MenuScreen, DialogScreen, _label_to_str)
6. `msgparts.py` (VISUAL_MODE_ON/OFF alias)
7. `clientmenu.py` (4 agganci + Ctrl+F2)
8. `clientmain.py` (options_menu voce)
9. `test_visual_ui.py`

Nessun import circolare: `clientvisualui` → `pygame`, `config`, `lib.screen`.
`clientmenuscreen` → `pygame`, `clientvisualui`, `lib.sound_cache`.
`clientmenu` → `clientmenuscreen`, `clientvisualui` (lazy import nel metodo o
import top-level, non importa nulla del menu nei moduli visivi).

## Rischi residui e mitigazioni

- **R1**: `pygame.display` non inizializzato in test → tutti i metodi di
  render hanno guard `if not config.visual_mode: return` (LEGGE-1).
- **R2**: `update_menu()` (TrainingMenu) ricostruisce le choices → uso
  `update_current(title, choices, index)` senza push/pop (LEGGE-7).
- **R3**: `SystemExit` da `set_and_launch_mod` → `ScreenManager.cleanup()`
  in `try/finally` di `Menu.run` (LEGGE-8).
- **R4**: token non traducibili in label → `_label_to_str` try/except per
  ogni token, fallback su `str(token)`, label vuota → `""` (LEGGE-4).

## Criteri di convalida

- F1: `config.visual_mode` persiste save/load come int 0/1.
- F2: `_label_to_str([])` → `""`; `_label_to_str([99999])` non solleva.
- F3: diff `clientmenu.py` mostra solo agganci, zero modifica a voice/sounds.
- F4: pytest visual_ui 9/9, suite globale invariata (105+).
- F5: `visual_mode=0` → comportamento attuale identico (zero render).

## Revisioni Round 9

- Audit B1.4: aggiunto `get_screen_manager().cleanup()` in
  `set_and_launch_mod()` e `set_and_launch_soundpack()` prima di `SystemExit`.
- Audit B1.3: `Menu.update_menu()` ora propaga l'update in-place allo stack
  visivo tramite `ScreenManager.update_current(...)` quando `visual_mode=1`.
- Audit B2: copertura test estesa da 9 a 11 test in
  `soundrts/tests/unittests/test_visual_ui.py` con casi su:
  - sync `Menu.update_menu()` -> `ScreenManager`
  - `DialogScreen.update_input()`
