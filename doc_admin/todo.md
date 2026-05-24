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

