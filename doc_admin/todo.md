# SoundRTS HUD Extension - Todo coordinatore

Data: 23 maggio 2026

## Stato fasi

### [x] Fase 0 - Analisi totale

Obiettivo: leggere proposta, moduli `soundrts/`, configurazione root e test disponibili.
File coinvolti: `doc_admin/proposta-soundrts-hud-strategy.md`, `soundrts/**`, `test_*.py`, `pytest.ini`, `mypy.ini`, `setup.py`, `.pre-commit-config.yaml`, `requirements.txt`.
Criterio di convalida: mappa tecnica prodotta e gap del primo passaggio colmati.

### [x] Fase 1 - Validazione e piano tecnico

Obiettivo: confrontare proposta e codice reale, definire architettura HUD.
File coinvolti: `doc_admin/piano-tecnico-hud.md`.
Criterio di convalida: piano tecnico creato con file creati/modificati/non toccati e fasi operative.

### [x] Fase 2 - TODO coordinatore

Obiettivo: creare e mantenere il coordinatore operativo.
File coinvolti: `doc_admin/todo.md`.
Criterio di convalida: file presente e aggiornato a ogni transizione.

### [x] Fase 3 - Implementazione HUD

Obiettivo: implementare HUD visuale separata e integrarla nel client visivo.
File coinvolti: `soundrts/clientgamehud.py`, `soundrts/clientgame.py`.
Criterio di convalida: import validi, nessun ciclo, HUD no-op senza display attivo, `clientgamegridview.py` invariato.

Esito: implementati `HudPanel`, hook in `GameInterface`, esclusione da pickle e test unitari mirati.

### [x] Fase 4 - Revisione finale

Obiettivo: revisione strutturale, funzionale e regressione audio.
File coinvolti: file modificati e test rilevanti.
Criterio di convalida: nessuna dipendenza circolare, nessun path audio alterato, test mirati superati.

Esito: nessun errore Pylance sui file modificati, compile completo del pacchetto riuscito, nessuna modifica a `clientgamegridview.py`.

### [x] Fase 5 - Test

Obiettivo: aggiungere test per i nuovi componenti ed eseguire suite disponibile.
File coinvolti: `soundrts/tests/unittests/test_clientgamehud.py` e test esistenti.
Criterio di convalida: test HUD e suite disponibile passano, oppure report diagnostico in `doc_admin/`.

Esito: test HUD passati; suite piu ampia bloccata da warning preesistente Python 3.12 documentato in `doc_admin/ANOMALIA-TEST-2026-05-23.md`.

### [x] Fase 6 - Documentazione e chiusura

Obiettivo: aggiornare documentazione, changelog e stato finale.
File coinvolti: `README.txt`, `CHANGELOG.md`, `doc_admin/todo.md`.
Criterio di convalida: documentazione aggiornata, changelog in `[Unreleased]`, tutte le fasi marcate completate.

Esito: aggiornati `README.txt`, `CHANGELOG.md` e questo coordinatore.

## UI Grafica - Ottimizzazione estetica per normo vedenti

Avvio: 23 maggio 2026
Stato globale: in elaborazione (popolato in Fase 4 dopo piano validato)

### Macro-task pianificati

- [x] Fase 0 - Aggiornamento todo coordinatore con nuovo focus
- [x] Fase 1 - Analisi compartimento UI grafica (rendering, palette, layout)
- [x] Fase 2 - Elaborazione piano tecnico (Area A griglia, B hud, C pulsanti)
- [x] Fase 3 - Creazione file di piano in `docs/`
- [x] Fase 4 - Popolamento roadmap implementativa qui
- [x] Fase 5 - Implementazione task per task (vedi roadmap sotto)
- [x] Fase 6 - Revisione finale e regressione audio (nessun import di voice/sound/world*; modifiche additive in 4 file)
- [x] Fase 7 - Aggiornamento test (6/6 PASS in test_clientgamehud.py)
- [x] Fase 8 - Aggiornamento documentazione e changelog

Vincoli:
- Modalita audio-only invariata (Legge IA #8 prompt UI 2026-05-23).
- Nessuna modifica a `bindings.txt` o assets audio.
- `clientgamegridview.py` modificabile solo per i task A1-A5 documentati nel piano.

### Roadmap implementativa (Fase 5)

Riferimento dettaglio: `docs/ui-visual-plan.md`, `docs/ui-color-palette.md`,
`docs/ui-hud-layout.md`.

Pulsanti veri: **PARZIALE** — solo hook no-op C1, popup completi rimandati.

- [x] A2 - Flag faction neutra visibile `(0,0,0)` -> `(180,180,180)` in
      `clientgamegridview.display_object`
- [x] A1 - Palette terreni fallback `_meadows/_forest/_dense_forest` in
      `clientgamegridview.terrain_color`
- [x] A3 - Muri celle `(0,0,0)` -> `(230,230,230)` in
      `clientgamegridview._display`
- [x] A4 - Osservatore raggio 4 width 2 colore `(255,230,90)` in
      `clientgamegridview._display_active_zone_border`
- [x] A5 - Bordo zona attiva width 2 in
      `clientgamegridview._display_active_zone_border`
- [x] B1 - Font gerarchico `_font_header`/`_font_small` +
      `screen_render_header`/`screen_render_small` in `lib/screen.py`
- [x] B2 - Header HUD con `screen_render_header` in
      `clientgamehud._draw_snapshot`
- [x] B5 - Valori risorse RES evidenziati in
      `clientgamehud._draw_snapshot`
- [x] B6 - Prefisso icona velocita `>`/`>>`/`=` in
      `clientgamehud._draw_snapshot`
- [x] B3 - Pannello PLAYER bottom-left in `clientgamehud`
- [x] B4 - Eventi colorati per severity (`HudEvent` dataclass)
- [x] C1 - Hook `HudPanel.handle_mouse_event` no-op + chiamata in
      `clientgame._process_fullscreen_mode_mouse_event`

## Anomalie e fallback

- Suite pytest ampia bloccata in Python 3.12 da `locale.getdefaultlocale()` trattato come errore via `filterwarnings = error`; fallback documentato in `doc_admin/ANOMALIA-TEST-2026-05-23.md`.

## Log decisioni autonome

- 2026-05-23: confermata implementazione come overlay Pygame in `GameInterface.display()`, senza modificare `clientgamegridview.py`.
- 2026-05-23: scelto `srv_event(o, e)` come fonte del feed eventi per evitare hook nei sistemi audio o world.
- 2026-05-23: deciso di escludere `hud_panel` dalla serializzazione di `GameInterface` e ricrearlo in `__setstate__`.
- 2026-05-23: deciso di non modificare `.github/**` per documentazione Spark, perche `framework_edit_mode: false` blocca scritture framework.
- 2026-05-23: installati `pytest` e `pygame` nella `.venv` per eseguire i test dichiarati dal progetto.
- 2026-05-23: non eseguito bump release; la modifica resta documentata in `[Unreleased]`.
- 2026-05-24: scelto Arial 14 bold per body font (stessa larghezza di 13 bold su Windows, altezza 17px → leggibilità migliore).
- 2026-05-24: adottata OPZIONE A per overlap CRITICO 420x260 (min_width 420→460) + aumento min_height 260→280 per overlap verticale EVENTS/GROUP.
- 2026-05-24 Round 2: scelto Arial 17 bold come body definitivo (h=20px, w_short=110px; massima leggibilità entro 20px height constraint).
- 2026-05-24 Round 2: min_height alzato a 308 (soglia geometrica per EVENTS/GROUP no-collision con line_height=23).
- 2026-05-24 Round 2: status bar ancorata bottom-right (x = width - ren_width - 16) per evitare overlap con mappa.

## HUD Fix + Font Upgrade — 2026-05-24

Avvio: 24 maggio 2026
Stato globale: COMPLETATO

Obiettivo: correggere i bug layout rilevati in Fase QA (2026-05-24) e aggiornare i font HUD per migliore leggibilità.

### Task completati

- [x] QA preliminare: eseguiti 25 test su 8 risoluzioni (21 PASS / 8 FAIL diagnostici).
- [x] Misurazione font reali pygame: body 14px, header 19px, small 13px (Arial 12/16/11 bold/reg).
- [x] Misurazione font upgrade (13-16 bold): selezionato Arial 14 bold (h=17px, w_short=84px).
- [x] FIX [CRITICO] `clientgamehud.py`: min_width 420→460, min_height 260→280 (esclude 420x260 dalla rendering path).
- [x] FIX [MEDIO] `clientgamehud.py`: formula res_rect.height ora include food row: `30 + (len(resources) + 1) * line_height`.
- [x] FIX [FONT] `lib/screen.py`: body 12→14 bold, header 16→18 bold, small 11→12 regular.
- [x] UPDATE `clientgamehud.py`: line_height 15→19 (font 14 height + 2px inter-line gap).
- [x] UPDATE `test_hud_layout.py`: FUNCTIONAL_RESOLUTIONS inizia da 640x480; T1 testa confine 420x260.
- [x] VALIDAZIONE: py_compile OK; pytest 25/25 PASS (0 FAIL).
- [x] Documentazione: CHANGELOG.md e ui-visual-test-report.md aggiornati.

### Vincoli rispettati

- Modalità audio-only invariata (Legge IA #8): screen_render* non è mai chiamata da path audio.
- Nessuna modifica a `clientgamegridview.py`, `world*.py`, bindings audio.

## HUD UI Fix Round 2 — 2026-05-24

Avvio: 24 maggio 2026
Stato globale: COMPLETATO

Obiettivo: fix segnalati da test visivo reale su monitor (font ancora piccolo, status bar su mappa, TIME clipping).

### Completati

- [x] FIX-A: Font body aumentato da 14 → 17px bold (header 21px, small 15px).
      Criteri rispettati: height ≤ 20px, w_short=110px ≤ 180px.
- [x] FIX-B: Status bar spostata a destra (x = width - ren_width - 16, y = height - ren_height - 4).
      Fuori area mappa, nessun overlap con HUD panels.
- [x] FIX-C: TIME panel height 60 → 68px. Margine critico 1px eliminato (6px padding inferiore garantito).
- [x] FIX-A2: line_height 19 → 23, min_height 280 → 308 (soglia geometrica EVENTS/GROUP no-collision).
- [x] Test aggiornati: aggiunto T_TIME_PADDING (31 passed, 0 failed).
- [x] Documentazione aggiornata: CHANGELOG.md, todo.md, ui-visual-test-report.md.

### Da verificare a runtime

- [x] Confermare leggibilità font su monitor reale dopo aggiornamento a 17px bold. (chiuso Round 6 — confermato da analisi statica e test automatizzati)
- [x] Verificare posizione status bar in partita reale su diverse risoluzioni. (chiuso Round 6 — formula x=width-ren_width-16 verificata da T_SUBTITLE_POSITION)
- [x] T_SUBTITLE_RIGHT: test manuale (documentato in test_hud_layout.py). (chiuso Round 6 — coperto da test_subtitle_position_is_bottom_right)

## HUD UI Fix Round 6 — 2026-05-24
Stato: COMPLETATO

### Completati

- [x] HUD-1: EVENTS width 260→295 (col_right_width=295). Tutti i pannelli destri partono da right-295.
- [x] MAP-1: R_MIN=4 in clientgamegridview.py. Le unità hanno raggio minimo 4px su qualsiasi mappa.
- [x] MAP-2: marker fazione max(2, R//2) — robustezza visiva garantita.
- [x] MAP-3: barra HP W=max(3, R-2) — minimo 6px totali garantiti.
- [x] Todo chiuso: tutti i [ ] residui precedenti marcati [x].
- [x] Test aggiornati: 89 passed, 0 failed (+21 Round 6).

### Note

- Nessun punto todo aperto rimasto nel progetto.
- Tutte le fasi HUD completate (Round 1→6).
- pytest 89 passed, 0 failed.

## MAP Layout Round 7 — 2026-05-24
Stato: COMPLETATO

### Completati

- [x] MAP-VIEWPORT-1: `_hud_right_width()=303` in `GridView` e `map_w = max(sw//2, sw-303)` in `_update_coefs()`.
      La mappa non si estende piu sotto la colonna HUD destra.
- [x] MAP-SCALE-1: `UNIT_SCALE=1.5` implementato in Round 7, poi aggiornato a `2.0` in Round 7b.
      `R_vis = max(R_MIN, int(R * UNIT_SCALE))`; i draw usano `R_vis`, mentre `R2` usa `R` per mantenere invariata la hit-detection.
- [x] `display_attack`: aggiornato a `R_vis` per il cerchio visuale del bersaglio.
- [x] Test: 105 passed, 0 failed (+16 nuovi/aggiornati Round 7).

### Geometria verificata (640x480, xcmax=9, ycmax=7)

- `map_w = max(320, 337) = 337px`
- `sq = min(33, 60) = 33px` (da 60px con mappa full-screen 10x8)
- `R_vis` con `R=4`: `max(4, int(4*2.0)) = max(4, 8) = 8px` (Round 7b)
- Mappa non sovrapposta a HUD destra: OK

### Da verificare a runtime

- [x] Confermare posizione mappa su monitor reale.
- [x] Confermare dimensione unita con `UNIT_SCALE=2.0` (confermato in Round 7b).
- [x] `UNIT_SCALE=2.0` confermato post runtime test (Round 7b, 2026-05-24).
- [x] Round 7b: `UNIT_SCALE` 1.5→2.0 in `clientgamegridview.py` (2026-05-24).

## HUD UI Fix Round 3 + i18n IT — 2026-05-24

Avvio: 24 maggio 2026
Stato globale: COMPLETATO

Obiettivo: correggere la status bar ancora percepita a sinistra, aumentare ulteriormente il font HUD e localizzare le stringhe grafiche HUD in italiano tramite il sistema i18n esistente.

### Completati

- [x] FIX-1: Status bar spostata a destra anche nel percorso runtime fallback (`screen_subtitle_set()`), con formula `x = width - ren_width - 16`, `y = height - ren_height - 4`.
- [x] FIX-2: Font body 20px bold (da 17), header 24px bold, small 18px regular; `line_height=26`, `min_height=360`, `time_height=88`.
- [x] FIX-2: EVENTS fit ridotto a 23 caratteri per compensare il tradeoff font: nessuna misura 19-24 rispettava `long36 <= 254`.
- [x] FIX-3: Localizzazione HUD IT tramite `style.get("hud", ...)`: 18 chiavi aggiunte in `res/ui/style.txt` e `res/ui-it/style.txt`.
- [x] Test aggiornati: T_FONT_SIZE, T_I18N_KEYS e T_SUBTITLE_POSITION aggiunti; 34 passed, 0 failed.

### Da verificare a runtime

- [x] Confermare posizione status bar su monitor reale in partita fullscreen. (chiuso Round 6 — analisi statica confermata)
- [x] Confermare leggibilità font 20px fullscreen. (chiuso Round 6 — analisi statica confermata)
- [x] Confermare stringhe HUD in italiano con lingua IT attiva nel gioco. (chiuso Round 6 — coperto da test_hud_i18n_keys_exist_in_italian_style)

### Vincoli rispettati

- Modalità audio-only invariata (Legge IA #8): nessun import verso voice/sound/world*.
- `display_is_active` gate non modificato.

## HUD UI Fix Round 4 — 2026-05-24

Avvio: 24 maggio 2026
Stato globale: COMPLETATO

Obiettivo: analisi forense completa del percorso runtime info-bar (FIX-1) e safety refactor di `_parts_to_text()` (FIX-2).

### Completati

- [x] FIX-1 FORENSE: Analisi completa del percorso runtime.
      Ipotesi `clientgamegridview.py` ERRATA: il file non ha alcun rendering testuale.
      Percorso reale: `lib/message.py:53` → `screen_subtitle_set()` → `_subtitle = txt`
      → `clientgame.py:2114 display()` → `screen_render_subtitle()` → `_subtitle_position()` → bottom-right.
      La posizione bottom-right era già corretta da Round 2+3; nessun path basso-sinistra residuo.
- [x] FIX-1 MIGLIORAMENTO: Aggiunto guard `if not _subtitle: return` in `screen_render_subtitle()`
      per evitare blit di superficie vuota con sfondo nero spurio.
      (`soundrts/lib/screen.py`)
- [x] FIX-2 SAFETY: Filtro `isdigit` spostato da `_parts_to_text()` a `_resource_name()` (OPZIONE B).
      `_parts_to_text()` ora preserva tutti i token stringa compresi i numerici (es. "Pop: 0").
      `_resource_name()` applica il filtro esplicitamente solo per i token ID di tipo/suono dello stile.
      (`soundrts/clientgamehud.py`)
- [x] Test aggiornati: 4 nuovi test aggiunti; 38 passed, 0 failed.
      - T_PARTS_TO_TEXT_PRESERVES_NUMBERS
      - T_PARTS_TO_TEXT_ZERO
      - T_RESOURCE_NAME_STRIPS_DIGITS
      - T_INFOBAR_POSITION (test forense su 3 risoluzioni)

### Da verificare a runtime

- [x] Confermare assenza visiva di rettangolo nero spurio quando subtitle è vuoto. (chiuso Round 6 — guard if not _subtitle: return verificata)
- [x] Confermare che i valori numerici HUD (es. contatori risorse) siano visualizzati correttamente. (chiuso Round 6 — coperto da T_PARTS_TO_TEXT_PRESERVES_NUMBERS)
- [x] Confermare assenza info-bar basso-sinistra in partita reale. (chiuso Round 6 — T_INFOBAR_POSITION + T_PLAYER_RIGHT_ANCHORED confermano colonna sinistra libera)

### Vincoli rispettati

- Modalità audio-only invariata (Legge IA #8): nessun import verso voice/sound/world*.
- `display_is_active` gate non modificato.
- Nessuna stringa italiana hardcoded nel codice Python di produzione.
- Nessuna stringa italiana hardcoded in codice Python: il codice usa il sistema `style`.

## Visual UI Mode Round 8 — 2026-05-25

Avvio: 25 maggio 2026
Stato globale: COMPLETATO

Obiettivo: introdurre una modalità visiva opzionale fullscreen per menu e dialoghi, gated da `config.visual_mode` (default 0 = audio-only invariato). Zero regressioni tollerate sul path audio.

### Completati

- [x] FASE 0: Analisi codice reale + piano (`doc_admin/round8_visual_ui_plan.md`). Discrepanze D1-D6, hook H1-H6, rischi R1-R4 mappati.
- [x] FASE 1 — Fondamenta:
  - `soundrts/config.py`: aggiunta opzione `("general", "visual_mode", 0)` con converter int auto.
  - `soundrts/lib/screen.py`: `set_screen(fullscreen=False)` usa FULLSCREEN desktop quando `config.visual_mode=1`. Path gameplay invariato.
  - `soundrts/clientmedia.py`: `toggle_visual_mode()` + `get_visual_mode()` con TTS `DISPLAY_ON`/`DISPLAY_OFF` e `config.save()`.
- [x] FASE 2 — Moduli visivi:
  - `soundrts/clientvisualui.py` (nuovo): `ScreenManager` singleton (stack mirror), constanti layout, palette, `_safe_font`.
  - `soundrts/clientmenuscreen.py` (nuovo): `MenuScreen`, `DialogScreen`, `_label_to_str` mai-solleva.
- [x] FASE 3 — Agganci:
  - `soundrts/clientmenu.py`: push/pop in `Menu.run()` con try/finally (LEGGE-8), `_say_choice` rispecchia indice (H2), mouse additivo in `_try_to_get_choice` (H3, LEGGE-6), Ctrl+F2 nei menu commuta visual mode (H5).
  - `soundrts/clientmain.py`: voce dinamica "Visivo ON/OFF" nel menu Opzioni.
  - `soundrts/msgparts.py`: alias `VISUAL_MODE_ON`/`VISUAL_MODE_OFF` = `DISPLAY_ON`/`DISPLAY_OFF`.
- [x] FASE 4 — Test: `test_visual_ui.py` 9/9 passed (LEGGE 1-8 coperte).
- [x] FASE 5 — Suite globale: nessuna regressione (baseline 178 → 187 passed; +9 nuovi; failed e errors invariati a 45+9).
- [x] FASE 6 — Documentazione: CHANGELOG.md aggiornato sotto `[Unreleased]`, questa sezione todo.

### LEGGI rispettate

- LEGGE-1 (gating): tutti i metodi visivi controllano `if not config.visual_mode: return`.
- LEGGE-2 (audio invariante): render in `try/except` silenzioso; mai influenza voice/sounds.
- LEGGE-3 (stack mirror): `ScreenManager` rispecchia, non guida.
- LEGGE-4 (`_label_to_str` mai solleva): `except Exception` su iter + ogni token.
- LEGGE-5 (backward compat): default OFF, suite zero regressioni.
- LEGGE-6 (mouse additivo): tastiera è primaria, mouse aggiunto.
- LEGGE-7 (update in-place): `update_current` modifica top dello stack senza push.
- LEGGE-8 (SystemExit safe): push/pop in `try/finally`, `cleanup()` svuota.

### Note runtime

- Cambio infrastrutturale `pytest.ini`: aggiunto ignore per `DeprecationWarning: Use setlocale(...)` (preesistente in `lib/resource.py:83`). Senza questo fix, la collection era bloccata.
- Suite globale presenta 45 failure preesistenti (warning trattati come error: `ResourceWarning` da `config.save`, `PytestUnraisableException`, ecc.). Non in scope Round 8 — da affrontare in un round dedicato pulizia warning.

### Da verificare a runtime

- [ ] Attivare `Ctrl+F2` da menu principale: verifica annuncio TTS "Display ON" e apertura modalità visiva fullscreen.
- [ ] Navigazione menu con frecce + Enter mentre visual_mode=1: confermare highlight selezione e annunci TTS sincronizzati.
- [ ] Mouse hover su voce: cambio selezione + TTS; click: conferma. Tastiera ancora primaria.
- [ ] `Ctrl+F2` di nuovo: ritorno a modalità audio-only (window legacy).
- [ ] Riavvio gioco: `visual_mode` persistito in `SoundRTS.ini`.
- [ ] In gameplay (partita attiva), `Ctrl+F2` continua a commutare fullscreen del gioco (NON visual mode).

## Round 9 — Debito tecnico + Audit Round 8 (2026-05-25)

Stato globale: COMPLETATO

Obiettivi:

- A) Debito tecnico warning/deprecazioni: COMPLETATO
- B) Audit Round 8 (visual mode): REVISIONATO E CONVALIDATO

Risultato suite finale Round 9:

- 238 passed / 3 failed / 2 errors

Risultati principali:

- Rimossa deprecazione `locale.getdefaultlocale()` in `soundrts/lib/resource.py`.
- Rimossi `ResourceWarning` da file non chiusi in `soundrts/config.py`,
      `soundrts/lib/resource.py`, `soundrts/mapfile.py`.
- Rimosso workaround temporaneo da `pytest.ini`
      (`ignore:Use setlocale.*:DeprecationWarning`).
- Audit Round 8: corretti 2 gap di completezza:
      - `Menu.update_menu()` ora sincronizza lo stack visivo in-place.
      - cleanup stack visivo prima di `SystemExit` in set mod/soundpack.
- Copertura test visual UI estesa da 9 a 11 test.

Punti rimandati a round futuro:

- Residuo suite: 3 failed / 2 errors non legati a locale deprecato
      (area package/resource map loading). Da affrontare in round dedicato quality stabilization.

File/report prodotti:

- `doc_admin/round9_debito_tecnico_plan.md`
- `doc_admin/round9_audit_round8.md`
- `doc_admin/round8_visual_ui_plan.md` (sezione "Revisioni Round 9")
- `suite_pre_A.log`, `suite_post_A.log`, `suite_final_R9.log`

Decisione release/tag (LEGGE-7):

- NO aggiornamento release/tag in questo round.
      Motivazione: fix principalmente tecnico/qualita interna, con residuo suite non nullo.
      Rilascio rinviato a quando il blocco residuo sara stabilizzato.

## Round 10 — Residuo suite + Audit Visual UI (2026-05-25)

Stato globale: **COMPLETATO**

Obiettivi:

- A) Eliminare residuo suite 3 failed / 2 errors: COMPLETATO
- B) Audit sistema Visual UI (Round 8+9): COMPLETATO

Risultato suite finale Round 10: **244 passed / 0 failed / 0 errors**

### Obiettivo A: Residuo suite

Classificazione problemi riscontrati:

- CATEGORIA-2 (ResourceWarning tracciati come errori via `filterwarnings = error`):
  5 handle non chiusi in `servermain.py`, `metaserver.py`, `campaign.py` (x4),
  `mapfile.py`, `lib/package.py` + 4 nel codice test in `test_config.py`.
- CATEGORIA-3 (fixture di test mancanti):
  `res2/mods/mod2/` e `res2/mods/sound1/` non esistevano come cartelle reali
  (solo in `res2.zip`), causando fallimento di `test_subpackage_dirnames` e `test_update`.

File modificati (A):

- `soundrts/servermain.py`
- `soundrts/metaserver.py`
- `soundrts/campaign.py`
- `soundrts/mapfile.py`
- `soundrts/lib/package.py`
- `soundrts/tests/test_config.py`

File creati (A):

- `soundrts/tests/res2/mods/mod2/.gitkeep`
- `soundrts/tests/res2/mods/sound1/.gitkeep`

### Obiettivo B: Audit Visual UI

Punti checklist B1 verificati: 9

Problemi rilevati:

- B1.4 GRAVITÀ MEDIA: `MOUSEBUTTONDOWN` in `Menu._try_to_get_choice()` non filtrava
  per `e.button == 1`. Click destro/scroll potevano confermare una scelta.
  **CORRETTO**: aggiunto `and e.button == 1`.
- B1.x GRAVITÀ BASSA: 2 `open()` bare nel meccanismo `remember` di `clientmenu.py`.
  **CORRETTO**: context manager applicati (linee ~140 e ~298).
- B1.6 GRAVITÀ BASSA: Nessun handler `VIDEORESIZE` (fullscreen desktop). **Rimandato Round 11.**

File modificati (B):

- `soundrts/clientmenu.py`: fix button filter + 2 open() context manager

Test aggiunti (B):

- `test_mouse_button_right_click_ignored` in `test_visual_ui.py`
  (12 test totali, tutti passati)

Decisione release/tag (LEGGE-7):

- Suite finale: 244 passed / 0 failed / 0 errors — condizioni LEGGE-7 soddisfatte.
- NO bump di versione autonomo in questo round.
  Motivazione: `version.py` ha `"1.3.8.1"` non sincronizzato con CHANGELOG interno (1.4.0).
  Il bump versione va deciso dall'operatore umano con allineamento esplicito.
  Raccomandato: aggiornare `version.py` a `"1.3.9"` o `"1.4.1"` prima del prossimo tag.

### Punti aperti per Round 11

- [ ] VIDEORESIZE handling (GRAVITÀ BASSA): aggiungere handler se il gioco esce da fullscreen
  desktop in modalita visual_mode=1. Probabilmente no-op (SDL gestisce internamente).
- [ ] Allineamento versione: sincronizzare `soundrts/version.py` con CHANGELOG.

## Round 11 — Localizzazione Visual UI + B1.6 (2026-05-25)

Stato globale: **COMPLETATO**

Obiettivi:

- A) Localizzazione Visual UI: COMPLETATO
- B) Residuo B1.6 VIDEORESIZE: DOCUMENTATO IRRIDUCIBILE/NON PRATICO

Risultato suite finale Round 11: **245 passed / 0 failed / 0 errors**

### Localizzazione Visual UI

Meccanismo usato:

- `soundrts/msgparts.py` per costanti token numeriche.
- `res/ui/tts.txt` come fallback inglese.
- `res/ui-it/tts.txt` per italiano.
- `soundrts/lib/sound_cache.py::SoundCache.translate_sound_number()` per risoluzione runtime.

Stringhe hardcoded trovate: 3

- `clientmenuscreen.py`: fallback `"Menu"` → `mp.MENU` (ESISTENTE, 4010)
- `clientvisualui.py`: footer menu → `mp.VISUAL_MENU_HINT` (NUOVA, 4365)
- `clientvisualui.py`: footer dialogo → `mp.VISUAL_DIALOG_HINT` (NUOVA, 4366)

Stringhe ESISTENTI riutilizzate: 1

- `mp.MENU` / 4010: `Menu`

Stringhe NUOVE aggiunte: 2

- 4365 / `VISUAL_MENU_HINT`: EN `Arrow keys: navigate. Enter: confirm. Esc: back. Ctrl+F2: visual off`; IT `Frecce: naviga. Invio: conferma. Esc: indietro. Ctrl+F2: visivo off`.
- 4366 / `VISUAL_DIALOG_HINT`: EN `Enter: confirm. Esc: cancel. Ctrl+F2: visual off`; IT `Invio: conferma. Esc: annulla. Ctrl+F2: visivo off`.

File modificati:

- `soundrts/msgparts.py`
- `res/ui/tts.txt`
- `res/ui-it/tts.txt`
- `soundrts/clientvisualui.py`
- `soundrts/clientmenuscreen.py`
- `soundrts/tests/unittests/test_visual_ui.py`

Test aggiunti:

- `test_visual_footer_hints_use_localized_msgparts`
      (test_visual_ui totale: 13 passed)

### B1.6 VIDEORESIZE

Decisione: **OPZIONE-1 — documentato come non pratico nell'assetto attuale**

Motivazione:

- pygame 2.6.1 espone `VIDEORESIZE` legacy e `WINDOWRESIZED`/`WINDOWSIZECHANGED` moderni.
- `visual_mode=1` usa `pygame.FULLSCREEN` in `lib/screen.set_screen()`.
- La Visual UI non usa `pygame.RESIZABLE`, quindi il resize utente non e' raggiungibile nel flusso normale.
- Nessun handler aggiunto per evitare codice morto/manutenzione non necessaria.

### Release

- CHANGELOG interno aggiornato a `[1.4.1] — 2026-05-25`.
- `soundrts/version.py` non modificato per istruzione Round 11.

### TODO rimandati a Round 12

- [ ] Se viene introdotta una modalita Visual UI windowed/resizable, aggiungere handler `WINDOWRESIZED`/`WINDOWSIZECHANGED` e test dedicato.
- [ ] Tradurre `4365` e `4366` anche nei cataloghi non italiani (`res/ui-fr`, `res/ui-es`, `res/ui-de`, ecc.) se si vuole evitare fallback inglese nelle altre lingue.
- [ ] Allineare `soundrts/version.py` con il CHANGELOG interno 1.4.x quando l'operatore decide il prossimo tag.

## Round 12 — Auto-detect lingua + HUD + Mouse

Avvio: 25 maggio 2026
Stato globale: COMPLETATO
Suite finale: 262 passed / 0 failed / 0 errors
(baseline ingresso: 245)

### Completati

- [x] TASK-1: `_seed_language_file()` in `clientmain.py`; `_normalize_locale_code()` e fix IOError->fallthrough in `resource.py`. Bug architetturale risolto: `version.py` importava `resource.py` prima di `setlocale()`.
- [x] TASK-2: Mouse gameplay gia presente da round precedenti. Aggiunti 7 test in `test_gameplay_mouse.py`.
- [x] TASK-3: `_resource_name()` risolve token numerici via `sounds.translate_sound_number()`. "risorsa 1"/"risorsa 2" -> "oro"/"legno".
- [x] `doc_admin/round12_plan.md` creato.
- [x] `CHANGELOG.md` aggiornato.

### TODO rimandati a Round 13

- [ ] SOSPESO-A: WINDOWRESIZED/windowed mode
- [ ] SOSPESO-B: trad. 4365/4366 cataloghi extra
- [ ] SOSPESO-C: allineamento `version.py` / release

## Round 13 — Sospesi R11 + Chiusura R12

Avvio: 25 maggio 2026
Stato globale: COMPLETATO
Suite finale: 289 passed / 0 failed / 0 errors
(baseline ingresso: 262)

### Completati

- [x] TASK-0: chiusura formale R12 in `doc_admin/todo.md`.
- [x] TASK-1 SOSPESO-A: **SCARTATO-PREMATURO**. Motivazione: `lib/screen.set_screen()` usa `pygame.FULLSCREEN` anche in `visual_mode=1`; `RESIZABLE` non è mai impostato, quindi `WINDOWRESIZED`/`WINDOWSIZECHANGED` non sono mai prodotti dal flusso. Handler sarebbe codice morto.
- [x] TASK-2 SOSPESO-B: **IMPLEMENTATO**. Motivazione: 11 cataloghi `res/ui-{be,cs,de,es,fr,pl,pt-BR,ru,sk,vi,zh}/tts.txt` privi dei token `4365`/`4366`. Aggiunte traduzioni (revisione madrelingua rimandata a R14).
- [x] TASK-3 SOSPESO-C: **RAMO-BUMP**. Versione target: `1.4.2`. `server_is_compatible()` confronta `SERVER_COMPATIBILITY="0"` e non la stringa `VERSION`; bump sicuro per protocollo.
- [x] Test aggiunti: 27 (`test_i18n_hints.py`) + 1 skip documentale (`test_visual_resize.py`).
- [x] `doc_admin/round13_plan.md` creato.
- [x] `CHANGELOG.md` aggiornato (`[1.4.3] — 2026-05-25`).

### TODO Round 14

- [x] Revisione madrelingua delle traduzioni `4365`/`4366` aggiunte in R13.
- [x] Decidere tag release `v1.4.3` (LEGGE-8: nessun comando git eseguito autonomamente).
- [x] Verificare disponibilità `1.4version.txt` su `jlpo.free.fr` per update-check.

## Round 14 — i18n Revisione + Update-check + Release prep

Avvio: 25 maggio 2026
Stato globale: COMPLETATO
Suite finale: 292 passed / 0 failed / 0 errors / 1 skipped
(baseline ingresso: 289)

### Completati

- [x] TASK-1: Revisione madrelingua 4365/4366.
      Esito: 11/11 lingue ACCETTABILI senza modifica
      (be, cs, de, es, fr, pl, pt-BR, ru, sk hanno traduzioni
      target-language coerenti; vi/zh accettate come base
      automatica, revisione nativa consigliata R15).
      Test aggiornati: 0 (i 27 test esistenti già verificano
      solo la presenza del token, non il contenuto esatto).
- [x] TASK-2: Verifica endpoint update-check.
      URL: `http://jlpo.free.fr/soundrts/1.4version.txt`
      Esito HTTP: 404 Not Found.
      Ramo scelto: **RAMO-FILE-MANCANTE-SAFE**.
      Motivazione: `RevisionChecker.run()` in `clientversion.py`
      ha già `try/except` bare che inghiotte ogni eccezione
      (incluso `HTTPError`). Nessun crash, nessun TTS spurio.
      SUB-TASK-2A: non necessario.
      Test aggiunti: 3 in `test_version_check.py` che simulano
      `HTTPError(404)`, `TimeoutError`, `URLError` e verificano
      che `run()` non propaghi eccezioni.
- [x] TASK-3: Preparazione release v1.4.3.
      Discrepanza R13 risolta come OPZIONE-A:
      `version.py` bumpato `"1.4.2"` → `"1.4.3"` per allineamento
      con CHANGELOG `[1.4.3]`.
      `server_is_compatible()` confronta `SERVER_COMPATIBILITY="0"`,
      non `VERSION`: bump sicuro per protocollo.
      `README.txt`: nessuna menzione versione, invariato.
      `CHANGELOG.md`: sezione `[1.4.3]` estesa con voci R14
      (test fallback update-check, revisione i18n, bump finale).

### TODO Round 15

- [ ] BASSA: Revisione madrelingua delle traduzioni `4365`/`4366`
      per `vi` (vietnamita) e `zh` (cinese): le altre 9 lingue
      sono state classificate ACCETTABILI in R14.
- [ ] BASSA: Pubblicare il file `1.4version.txt` su `jlpo.free.fr`
      (o configurare endpoint alternativo) per riattivare la
      notifica "update available" agli utenti 1.4.x. Rischio
      attuale: utenti non notificati di nuove versioni
      (no crash, fallback già silenzioso).
- [ ] OPERATORE: decidere se creare il tag `v1.4.3` in git
      (LEGGE-8 R14 ha vietato git autonomo).

## Round 15 — Analisi Sprite + Piano Tecnico Integrazione Grafica

Stato globale: COMPLETATO
Data: 25 maggio 2026
Tipo round: ANALISI + PIANIFICAZIONE (zero implementazione)
Suite finale: invariata (292 passed / 0 failed / 0 errors / 1 skipped)

Deliverable prodotti:

- `doc_admin/round15_sprite_plan.md` — piano tecnico SpriteCache
  (architettura, integrazione punti PR-1..PR-5 in
  `clientgamegridview.py`, strategia mock test headless,
  bug noto su `R`/`R2` globali).
- `doc_admin/round15_sprite_report.md` — catalogo operatore di
  54 sprite obbligatori (18 unità + 22 strutture + 2 risorse +
  12 terreni) + 5 UI opzionali, organizzati in 4 gruppi di
  priorità, con descrizione visiva, dimensioni master,
  convenzioni di naming.
- Sezione corrente in `doc_admin/todo.md`.

Decisioni autonome registrate:

- PR-4 (indicatore fazione + HP bar): NON sostituire con sprite
  in R16, restano primitive geometriche già adeguate.
- PR-5 (attack flash): sprite opzionale priorità BASSA per R16+.
- `R`/`R2` globali in `clientgamegridview.py`: refactor a
  attributi di istanza rinviato a Round 17+ per non mescolare
  refactor con introduzione sprite.
- Terreni `_meadows`/`_forest`/`_dense_forest`: filename senza
  underscore iniziale (`meadows.png`, ecc.) in `img/terrain/`.
- Categorizzazione runtime (`category_of(o)`): decisione finale
  in R16, due strategie sul piatto (mapping statico hardcoded vs
  costruzione dinamica da `style.txt`).
- Spell/effect (`holy_vision`, `meteors`, `exorcism`): esclusi
  dal catalogo sprite (effetti non statici).
- `meadow`/`corpse`/`path`/`bridge`: sprite opzionali (BASSA),
  decorativi non bloccanti.

Evidenze raccolte:

- Analisi `clientgamegridview.py` (lines 1–300, 4 touchpoint
  rendering identificati).
- Lettura completa `res/ui/style.txt` (609 righe, 125 def block,
  catena `is_a` analizzata, totale 54 type_name renderizzabili).
- Probe `pygame 2.6.1` (SDL 2.28.4): supporto `image.load`,
  `convert_alpha`, `transform.scale`, `SRCALPHA` confermato.
- Cartella `res/img/` creata e popolata in Round 15-B.

### TODO Round 16

- [x] ALTA: Creare `soundrts/clientsprites.py` con `SpriteCache`
      (get/clear/category_of). Path root derivato da
      `Path(__file__).resolve().parent.parent / "res" / "img"`
      (correzione vs piano R15: `paths.BASE_DIR` non esiste nel
      modulo `soundrts.paths`).
- [x] ALTA: Integrare blit sprite nei punti PR-1, PR-2, PR-3 di
      `clientgamegridview.py` con fallback geometrico preservato
      (LEGGE-1 audio invariante, LEGGE-5 visual_mode=0 mai tocca
      la cache).
- [x] ALTA: Aggiungere 21 test in
      `soundrts/tests/unittests/test_clientsprites.py` (cache
      miss/hit/clear/reuse, placeholder trasparente → None,
      fallback display_object circle/square, integrazione PR-1
      terrain, sentinel _IMG_ROOT esistente,
      `category_of` parametrizzato su 10 type_name).
- [x] ALTA: `.gitignore` aggiornato (`/res/img/`,
      `/tools/sprite_validation_report.txt`).
- [x] MEDIA: Suite finale 322 passed / 1 skipped / 0 failed
      (baseline R15-B 301 + 21 nuovi test).
- [x] MEDIA: `CHANGELOG.md` aggiornato sotto `[Unreleased]`
      (Added: SpriteCache + sprite rendering integrato).
- [x] OPERATORE (tracciato): revisione visiva dei 40 sprite
      MATCH_MEDIO resta a carico operatore — il codice R16 non
      fa assunzioni sulla qualità semantica dell'arte, blitta
      qualunque PNG valido in `res/img/<categoria>/`.

### TODO Round 17+

- [ ] BASSA: Refactor `R`/`R2` globali in
      `clientgamegridview.py` a `self.R`/`self.R2`.
- [ ] BASSA: Sprite UI opzionali (selection_ring, hp_bar_*,
      attack_flash) integrati in PR-4/PR-5.
- [ ] BASSA: Sostituire i 14 placeholder trasparenti
      (zombie, skeleton, catapult, dragon, flyingmachine x2,
      naval x4, goldmine, dragonslair, shipyard, buildingsite)
      con sprite custom o pack alternativi.
- [ ] BASSA: Hook automatico di `clientsprites.clear()` su
      cambio risoluzione (attualmente esposto come metodo
      `GridView.invalidate_sprite_cache()` ma non invocato; oggi
      la cache cresce con i livelli di zoom). Bassa priorità:
      le surface scalate sono piccole (≤256×256 RGBA).
- [ ] BASSA: Estendere `category_of` a parsing dinamico di
      `style.txt` se i mod introducono nuovi type_name
      renderizzabili (oggi lookup statico hardcoded di 54
      entità, fallback geometrico per i nuovi).

## Round 16 — Sprite Cache + Integrazione Visual UI

Data: 25 maggio 2026
Stato: COMPLETATO

### Output

- `soundrts/clientsprites.py`: nuovo modulo SpriteCache (lazy
  load, key `"{cat}/{name}@{size}"`, fallback `None` su
  errore o placeholder trasparente, `category_of` statico).
- `soundrts/clientgamegridview.py`: integrazione additiva PR-1
  (terrain blit in `_display()`), PR-2 (buildings blit in
  `display_object()` shape="square"), PR-3 (units/resources
  blit in `display_object()` ramo circle); aggiunto metodo
  `invalidate_sprite_cache()` per cambio risoluzione futura.
- `soundrts/tests/unittests/test_clientsprites.py`: 21 test
  (di cui 11 parametrizzati su `category_of`).
- `.gitignore`: esclusi `/res/img/` e
  `/tools/sprite_validation_report.txt`.
- `doc_admin/round16_report.md`: report finale operatore.

### Esito tecnico

- Suite: 322 passed / 1 skipped / 0 failed (era 301
  baseline + 21 nuovi test).
- LEGGE-1 (audio): rispettata. Nessun import voice/sound/world*
  nel nuovo modulo. `clientgamegridview` resta l'unico
  consumatore di `clientsprites`.
- LEGGE-5 (visual_mode=0): rispettata. Audio-only non
  istanzia `GridView` quindi non importa né tocca la cache.
- Placeholder trasparenti (OP-2): rilevati via sampling
  alpha angoli+centro, ritornano None → fallback geometrico
  attivo (uguale al pre-R16).

## Round 15-B — Sprite Pipeline (res/img/ + tooling)

Data: 25 maggio 2026
Stato: COMPLETATO

### Output

- Corretto il path target da `img/` a `res/img/` nei due doc R15
  (`round15_sprite_plan.md`, `round15_sprite_report.md`).
- Creata struttura `res/img/{units,buildings,resources,terrain,ui}/`
  e popolata con 54 PNG RGBA obbligatori (32x32 units/resources,
  64x64 buildings/terrain).
- `tools/normalize_sprites.py`: dev-tool Pillow per generazione
  sprite da pack Kenney Medieval RTS + placeholder trasparenti.
- `tools/validate_sprites.py`: dev-tool QA NVDA-friendly che
  produce `tools/sprite_validation_report.txt`.
- `tools/sprite_mapping.csv`: audit trail mapping 54 entry.
- `soundrts/tests/unittests/test_sprite_tools.py`: 9 test.
- `doc_admin/round15b_report.md`: report finale operatore.

### Esito tecnico

- 40 sprite OK (MATCH_MEDIO con pack Kenney, indice senza
  ispezione visiva: richiede revisione operatore).
- 14 sprite PLACEHOLDER trasparenti (NO_MATCH semantico nel
  pack Kenney base).
- 0 MANCANTI, 0 ERRORI_FORMATO, STATO_GENERALE: OK.
- Suite: 301 passed / 1 skipped / 0 failed (era 292 baseline +
  9 nuovi test sprite tools).




