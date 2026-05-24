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
