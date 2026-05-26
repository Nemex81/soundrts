# Round 11 — Localizzazione Visual UI + B1.6 VIDEORESIZE

Data: 2026-05-25
Stato: COMPLETATO

---

## Baseline ingresso

| Metrica | Valore |
|---------|--------|
| Suite ingresso | 244 passed / 0 failed / 0 errors |
| Suite post-A | 245 passed / 0 failed / 0 errors |
| Suite finale | 245 passed / 0 failed / 0 errors |
| test_visual_ui.py | 13 passed |

---

## A0 — Sistema di localizzazione

SoundRTS non usa gettext per i menu. Il sistema reale e' custom:

- Le etichette UI sono liste di token numerici definite in `soundrts/msgparts.py`.
- I token vengono risolti da `soundrts/lib/sound_cache.py::SoundCache.translate_sound_number()`.
- I testi base sono in `res/ui/tts.txt`.
- Le traduzioni localizzate sono in `res/ui-*/tts.txt`, ad esempio `res/ui-it/tts.txt`.
- `ResourceStack` carica `res/ui/tts.txt` e poi `res/ui-<lingua>/tts.txt`; le chiavi localizzate sovrascrivono il fallback inglese.
- La lingua viene scelta all'avvio da `cfg/language.txt` oppure dal locale di sistema (`soundrts/lib/resource.py::preferred_language`).

File stringhe letti:

- `res/ui/tts.txt` (inglese fallback)
- `res/ui-it/tts.txt` (italiano)

---

## A1 — Inventario hardcoded Visual UI

| File | Stringa hardcoded | Chiave | Stato | Esito |
|------|-------------------|--------|-------|-------|
| `clientmenuscreen.py` | `"Menu"` fallback titolo | `mp.MENU` / 4010 | ESISTENTE | Riutilizzata |
| `clientvisualui.py` | `"Up/Down Naviga   Enter Conferma   Esc Indietro   Ctrl+F2 Visivo OFF"` | `mp.VISUAL_MENU_HINT` / 4365 | NUOVA | Aggiunta EN+IT |
| `clientvisualui.py` | `"Enter Conferma   Esc Annulla   Ctrl+F2 Visivo OFF"` | `mp.VISUAL_DIALOG_HINT` / 4366 | NUOVA | Aggiunta EN+IT |

Nota: le voci menu principali (`Options`, `Quit`, `single player`, `Visual Mode ON/OFF`, ecc.) erano gia' token `msgparts` nel flusso audio (`mp.OPTIONS`, `mp.QUIT2`, `mp.VISUAL_MODE_ON/OFF`) e quindi non richiedevano nuove stringhe.

---

## A2 — Stringhe aggiunte al sistema

| Chiave | EN (`res/ui/tts.txt`) | IT (`res/ui-it/tts.txt`) |
|--------|------------------------|---------------------------|
| 4365 / `VISUAL_MENU_HINT` | `Arrow keys: navigate. Enter: confirm. Esc: back. Ctrl+F2: visual off` | `Frecce: naviga. Invio: conferma. Esc: indietro. Ctrl+F2: visivo off` |
| 4366 / `VISUAL_DIALOG_HINT` | `Enter: confirm. Esc: cancel. Ctrl+F2: visual off` | `Invio: conferma. Esc: annulla. Ctrl+F2: visivo off` |

Costanti aggiunte in `soundrts/msgparts.py`:

- `VISUAL_MENU_HINT = [4365]`
- `VISUAL_DIALOG_HINT = [4366]`

Le altre lingue mantengono il fallback inglese finche' non verranno tradotte nei rispettivi `res/ui-*/tts.txt`.

---

## A3 — Sostituzione hardcoded → localizzato

File modificati:

- `soundrts/clientvisualui.py`
  - `FOOTER_HINT_MENU` ora punta a `mp.VISUAL_MENU_HINT`.
  - `FOOTER_HINT_DIALOG` ora punta a `mp.VISUAL_DIALOG_HINT`.
- `soundrts/clientmenuscreen.py`
  - Fallback titolo `"Menu"` sostituito con `_label_to_str(mp.MENU)`.
  - Footer menu/dialog renderizzati con `_label_to_str(vui.FOOTER_HINT_*)`.

Test aggiunto:

- `test_visual_footer_hints_use_localized_msgparts`
  - Verifica che i footer Visual UI usino token `msgparts`.
  - Verifica che `_label_to_str()` risolva le stesse stringhe di `sounds.translate_sound_number()`.

Convalida A3:

- `py_compile`: OK
- `test_visual_ui.py`: 13 passed

---

## A4 — Boot localizzazione e cambio lingua runtime

Flusso boot verificato:

1. `clientmain.main()` chiama `init_media()`.
2. `clientmedia.init_media()` chiama `minimal_init()` e poi `sounds.load_default(res)`.
3. `ResourceStack` ha gia' calcolato `language` tramite `preferred_language`.
4. Solo dopo `init_media()`, `clientmain.main()` entra in `main_menu()` e crea i menu visuali.

Conclusione: la localizzazione e' inizializzata prima della creazione/render dei `MenuScreen`.

Cambio lingua runtime:

- Non esiste un'opzione menu per cambiare lingua a runtime.
- La lingua e' letta da `cfg/language.txt` all'avvio.
- Le stringhe Visual UI vengono risolte al render tramite `_label_to_str()`; se in futuro la lingua venisse ricaricata e `sounds` aggiornato, i footer seguirebbero la nuova cache senza dover ricreare le costanti.

---

## Obiettivo B — B1.6 VIDEORESIZE

Versione pygame verificata:

- pygame 2.6.1 (SDL 2.28.4)
- `VIDEORESIZE` presente ma legacy
- `WINDOWRESIZED` / `WINDOWSIZECHANGED` presenti nel modello pygame 2.x

Analisi codice:

- `soundrts/lib/screen.py::set_screen()` usa `pygame.FULLSCREEN` quando:
  - gameplay fullscreen e' attivo, oppure
  - `config.visual_mode == 1` nei menu/dialoghi.
- Il codice non usa `pygame.RESIZABLE` per Visual UI.
- La finestra Visual UI non e' ridimensionabile dall'utente nel flusso normale.

Decisione: **OPZIONE-1 — documentato come irriducibile/non pratico nell'assetto attuale**.

Motivazione: aggiungere un handler `VIDEORESIZE`/`WINDOWRESIZED` oggi non intercetterebbe un caso utente reale, perche' Visual UI e' fullscreen desktop e non resizable. Un handler ora aumenterebbe superficie di manutenzione senza beneficio pratico.

Riaprire solo se in Round futuro viene introdotta una modalita' Visual UI windowed/resizable.

---

## Compliance LEGGI

| Legge | Esito |
|-------|-------|
| LEGGE-0 READ-BEFORE-WRITE | Rispettata |
| LEGGE-1 AUDIO INVARIANTE | Nessuna modifica a `voice.*`, `psounds.*`, `sounds.*` |
| LEGGE-2 VISUAL GATE | Guard intatti |
| LEGGE-3 BACKWARD COMPAT | `visual_mode` default 0 invariato |
| LEGGE-4 LOCALIZZAZIONE SORGENTE UNICA | Footer e fallback usano `msgparts`/`tts.txt` |
| LEGGE-5 MAX TENTATIVI | Non raggiunto |
| LEGGE-6 SUITE NON REGREDISCE | 245 >= 244 |
| LEGGE-7 RELEASE SOLO SE MOTIVATO | Changelog interno 1.4.1 creato, `version.py` invariato |
| LEGGE-8 NO GIT | Nessun comando git eseguito |
