# Changelog

## [Unreleased]

### Added

- [UI-MASTER-07/P1-UNIT-SELECTION] `soundrts/clientgamegridview.py`: rect-highlight visivo attorno alle unità appartenenti a `interface.group`. Nuova costante modulo `_SELECTION_HIGHLIGHT_COLOR = (100, 255, 100)` (verde pastello, distinto dal verde acceso `(0,255,0)` del marker centrale del gruppo e dal verde scuro `(60,140,60)` delle unità alleate). In `display_object()`, dopo il cerchio colore e prima della barra HP, viene disegnato un bordo (width=2) con `draw_rect(_SELECTION_HIGHLIGHT_COLOR, hl_rect, 2)`; `side = max(R_vis*2+4, square_view_width//2)` garantisce visibilità sia su sprite piccoli (zoom out) sia su mappe grandi. Risolve la difficoltà di leggere a colpo d'occhio quale gruppo è selezionato, problema noto del cerchio centrale `R_vis//2` (≤4 px nelle mappe più ampie).
- [UI-MASTER-07] `soundrts/tests/unittests/test_ui_master_07.py`: 7 nuovi test (4 P0-OPTIONS-FIX: import senza `SystemExit`, `--help` exit code 0, override `-p`, alias `_parse_options`; 3 P1-UNIT-SELECTION: rect-highlight presente per unità nel gruppo, assente fuori gruppo, render con `group=[]` non crasha). Pattern lazy-import + mock di `draw_rect` per evitare side-effect CLI.

### Changed

- [UI-MASTER-07/P0-OPTIONS-FIX] `soundrts/options.py`: rimossa la chiamata top-level `_parse_options()`. La funzione è stata rinominata `parse_args(argv=None)`, resa pubblica e documentata. Alias `_parse_options = parse_args` mantenuto per compat. Entry points `soundrts.py` e `server.py` ora invocano esplicitamente `options.parse_args()` PRIMA degli import di `clientmain`/`server` per preservare il binding di `options.port` come default in `clientserver.connect_and_play`. Conseguenza: `python -m pytest <path>` non termina più con `SystemExit: 2` quando `sys.argv` contiene token non riconosciuti dal CLI SoundRTS.
- [UI-MASTER-07/OPT-1] `soundrts/clientgamehud.py`: hit-test e tooltip delle righe attività (`_panel_rects["activity_row_N"]`) passano da scan lineare di tutto `_panel_rects` con filtro `startswith("activity_row_")` (n ≈ 20+ rect totali, due loop per click+hover) a iterazione diretta sul nuovo dict `_activity_row_rects: Dict[int, Rect]` popolato in parallelo nel render. Complessità per evento: **PRIMA O(n) ≈ 20+, DOPO O(k) ≤ 8**. Allocazione invariata (un solo `pygame.Rect` per riga, ora referenziato due volte). Leggibilità migliorata: scompare il parsing `int(key.split("_", 2)[2])` lato handler. Reset coerente in `_draw_snapshot` e cleanup quando il pannello è collassato. `test_cancel_handler_removes_row_immediately_for_ui_feedback` aggiornato per popolare anche `_activity_row_rects` (nuovo contratto).

### Fixed

- [UI-MASTER-07/P0-OPTIONS-FIX] Risolto il side-effect import-time di `soundrts.options` che bloccava qualsiasi tool esterno (pytest path-esplicito, sphinx, mypy) il cui `sys.argv` contenesse token non gestiti dal parser interno. Causa: `_parse_options()` chiamato al top-level → `optparse.OptionParser.parse_args(None)` legge `sys.argv` → `SystemExit(2)` immediato. Fix: parsing delegato agli entry points (vedi Changed).

### Optimization (Not Applied)

- [UI-MASTER-07/AREA-1] **FlashEffect dataclass** valutata e non applicata: esiste un solo flash type (`_move_flash_*`), refactoring per future estensioni non giustificato (LEGGE-OPT-2: leggibilità > micro-opt). Riapplicare se si aggiunge un secondo flash type.
- [UI-MASTER-07/AREA-2] **ActivityRow dataclass** valutata e non applicata: i tre dict `_activity_row_{texts,units,kinds}` sono già accessibili in modo simmetrico (`.get(idx)`). Sostituzione con dataclass richiederebbe touch su tutti i 13 test che mockano direttamente le mappe; riduzione righe stimata ≤ 10% < soglia 15% del prompt.
- [UI-MASTER-07/AREA-5] **`_update_coefs()` caching** non applicata: senza profiler runtime e flag dirty robusto, il rischio di stale geometry su resize/visual_mode toggle supera il guadagno teorico. Skip per LEGGE-OPT-2.
- [UI-MASTER-07/AREA-6] **Cache `R_vis` in `display_object`** non necessaria: c'è già un singolo calcolo locale (`R_vis = max(R_MIN, int(R * UNIT_SCALE))`), nessuna duplicazione da ottimizzare.
- [UI-MASTER-07/AREA-4] **Helper `_debounce_elapsed`** valutata non applicata: solo 2 siti d'uso (`_update_tooltip` con `_map_tooltip_delay` e `_empty_cell_tooltip_delay`); riduzione duplicazione marginale (-2 righe) a fronte di una indirezione in più sui hot path tooltip.

### Added

- [UI-MASTER-06/P2-MOVE-INDICATOR] `soundrts/clientgamegridview.py`: nuovo metodo pubblico `GridView.screen_pos_of_square(square)` che restituisce il centro geometrico della cella in coordinate schermo riusando `_get_view_coords_from_world_coords`. Defensive: ritorna `None` se `square` è `None` o privo di `.x`/`.y`. `soundrts/clientgame.py`: il blocco right-click in `_process_fullscreen_mode_mouse_event` ora calcola `flash_pos = self.grid_view.screen_pos_of_square(right_square)` e lo passa a `hud_panel.flash_move_target(...)`; fallback su `e.pos` in caso di `None`. Chiude la deviazione documentata in UI-MASTER-05/T10-MOVE-INDICATOR: il flash è ora ancorato al centro geometrico della cella, non più al pixel di click.
- [UI-MASTER-06/P3-L10N-COMPLETION] `res/ui-fr/style.txt`, `res/ui-pt-BR/style.txt`: tradotte tutte le chiavi `def hud` ereditate dai blocchi placeholder UI-MASTER-02b/03/04. FR (convenzioni tipografiche: spazio fine prima di `:`): `tooltip_map_hp PV : {hp}/{hp_max}`, `activity_collapsed || (masqué)`, `tooltip_activity_show Afficher l'activité`, `tooltip_activity_hide Masquer l'activité`, `tooltip_activity_cancel_hint Cliquer pour annuler`, `tooltip_food_cell Nourriture : {food}`, `tooltip_player_panel Joueur : {name}`, `tooltip_unit_row {label} - {hp}/{hp_max} PV - {status}`, `tooltip_bottom_time Temps de jeu : {time}`, `tooltip_bottom_speed Vitesse de jeu : {speed}`, `tooltip_map_empty_cell Cellule ({col},{row})`. PT-BR: `PV: {hp}/{hp_max}`, `|| (oculto)`, `Mostrar atividade`, `Ocultar atividade`, `Clique para cancelar`, `Comida: {food}`, `Jogador: {name}`, `Tempo de jogo: {time}`, `Velocidade do jogo: {speed}`, `Célula ({col},{row})`. Le chiavi puramente strutturali (`tooltip_event_full`, `tooltip_map_entity`, `tooltip_map_owner`, `tooltip_map_coords`, `bottom_bar_time_fmt`, `bottom_bar_speed_fmt`, `tooltip_activity_row_full`, `tooltip_res_cell`, `tooltip_unit_row_nohp`, `entity_na`) sono mantenute identiche perché lingua-agnostiche. Rimossi i marker `; TODO: tradurre`.
- [UI-MASTER-06] `soundrts/tests/unittests/test_ui_master_06.py`: 9 nuovi test (1 P1 sanity guard + 4 P2-MOVE-INDICATOR + 4 P3-L10N-COMPLETION parametrizzati su FR e PT-BR). Fixture autouse module-scope installa `screen_pos_of_square` sull'`_FakeGridView` con import lazy per evitare il side-effect di `soundrts.options._parse_options()` durante la collection di pytest.

### Changed

- [UI-MASTER-06/P1-TEST-ISOLATION] `soundrts/tests/unittests/test_clientgamehud.py`: aggiunta fixture autouse function-scope `_reset_style_singleton` che azzera `soundrts.definitions.style._dict` prima di ogni test e lo ripristina nel teardown. Causa pollution identificata: `soundrts/tests/test_cache.py` istanzia `ResourceStack` il cui `__init__ -> _reload()` invoca `load_style()` con la lingua di sistema rilevata da `_preferred_language()` (IT su Windows it-IT), riempiendo il singleton globale prima che `test_clientgamehud.py` venga eseguito (i due file girano in ordine alfabetico path). Senza la fixture, `_hud_text` restituiva chiavi IT (`Risorsa 1`, `Giocatore`, `Pop`) invece dei default EN attesi dai test. Fixture function-scope per massima safety e zero perturbazione della suite a valle.

### Fixed

- [UI-MASTER-06/P1-TEST-ISOLATION] Risolto il test pollution pre-esistente segnalato in `doc_admin/todo.md` come "Aperture per UI-MASTER-06 voce 5": `test_hud_snapshot_collects_gameplay_data` e `test_hud_player_line_falls_back_when_missing` ora passano sia in isolamento sia in sequenza con la suite completa. Verdetto suite: 466 passed, 1 skipped (era 455 passed + 2 failed prima del fix).
- [UI-MASTER-06/P2-MOVE-INDICATOR] Risolta la deviazione documentata in UI-MASTER-05/T10-MOVE-INDICATOR: l'ancora visiva del flash post right-click è ora il centro geometrico della cella di destinazione, garantendo allineamento semantico anche per click vicini ai bordi.

### Added (UI-MASTER-05 e precedenti)

- [UI-MASTER-05/T10-TOOLTIP-THROTTLE] `soundrts/clientgamehud.py`: debounce 0.25 s sul tooltip della cella vuota mappa (`set_map_hover` con `entity=None` e `square≠None`). Nuovi attributi `_empty_cell_hover_square`, `_empty_cell_hover_start`, `_empty_cell_tooltip_delay`. Confronto cella per valore `(col,row)` (non per identità) per resistere ai ricalcoli per-frame di `grid_view.square_from_mousepos`. Stato debounce ripulito su `set_map_hover(None, None)`.
- [UI-MASTER-05/T10-CANCEL-SERVER] `soundrts/clientgamehud.py`: `_cancel_unit_order(unit, kind)` ora notifica il server per i tre kind tracciati (`training`→`cancel_training`, `research`→`cancel_upgrading`, `build`→`cancel_building`) via `self.interface.send_order(keyword, None, [])` quando disponibile (`getattr` difensivo). `orders.pop(0)` mantenuto come riduttore di flash UI. Nuovo dizionario `_activity_row_kinds: Dict[int, str]` popolato in `_draw_activity_panel` parallelamente a `_activity_row_units`. `handle_mouse_event` rimuove immediatamente la riga dalle tre mappe `_activity_row_{texts,units,kinds}` post-click per feedback visivo istantaneo. Per kind non mappato: solo client-only pop (documentato come limitazione nota).
- [UI-MASTER-05/T10-MOVE-INDICATOR] `soundrts/clientgamehud.py`, `soundrts/clientgame.py`: feedback visivo transitorio sul right-click. Nuovi attributi `_move_flash_square`, `_move_flash_pos`, `_move_flash_start`, `_move_flash_duration=0.5`. Nuovo metodo pubblico `HudPanel.flash_move_target(square, pos)` e privato `_draw_move_flash(screen)` che dipinge un cerchio verde semi-trasparente `(140,220,140,180)` raggio 10 px sul punto di click; auto-decadimento dopo 0.5 s. Hook nel blocco right-click di `_process_fullscreen_mode_mouse_event`. **Deviazione documentata vs prompt**: usata la posizione di click come ancora visiva invece del centro geometrico della cella (calcolare il centro avrebbe richiesto accoppiamento con `grid_view`; il punto cliccato è un'ancora stabile in-cella, visivamente equivalente per il giocatore).
- [UI-MASTER-05] `soundrts/tests/unittests/test_ui_master_05.py`: 13 nuovi test (4 T10-TOOLTIP-THROTTLE + 6 T10-CANCEL-SERVER + 4 T10-MOVE-INDICATOR + 1 L10N audit).
- [UI-MASTER-04/T9-CANCEL] `soundrts/clientgamehud.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: click sinistro su una riga `activity_row_N` annulla il primo ordine dell'unità sorgente. `_collect_activity` ora restituisce tuple `(kind, name, pct, unit)`; `_draw_activity_panel` registra la mappa `_activity_row_units` consumata da `handle_mouse_event`. Nuovo helper `_cancel_unit_order(unit)` (best-effort, non solleva). Tooltip riga arricchito con hint `Click to cancel` (IT: `Clicca per annullare`) via template `tooltip_activity_row_full`.
- [UI-MASTER-04/T9-TOOLTIP-GLOBAL] `soundrts/clientgamehud.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: tooltip su ogni elemento HUD interattivo o informativo: celle risorsa (`res_cell_N`), cella cibo (`food_cell`), pannello giocatore (`player`), righe gruppo (`group_row_N`), celle barra inferiore (`bottom_time`, `bottom_speed`) e cella vuota della mappa (`tooltip_map_empty_cell`). `_draw_snapshot` registra i nuovi rect e memorizza lo snapshot corrente in `_last_snapshot`. `set_map_hover(entity=None, pos, square=...)` sorgente il tooltip coords-only quando il cursore non punta a entità.
- [UI-MASTER-04/T9-L10N-AUDIT] `res/ui/style.txt`, `res/ui-it/style.txt`: nuove chiavi `tooltip_activity_cancel_hint`, `tooltip_activity_row_full`, `tooltip_res_cell`, `tooltip_food_cell`, `tooltip_player_panel`, `tooltip_unit_row`, `tooltip_unit_row_nohp`, `tooltip_bottom_time`, `tooltip_bottom_speed`, `tooltip_map_empty_cell`. `res/ui-fr/style.txt`, `res/ui-pt-BR/style.txt`: introdotta sezione `def hud` con placeholder EN marcati `; TODO: tradurre` per le chiavi UI-MASTER-02b/03/04.
- [UI-MASTER-04] `soundrts/tests/unittests/test_ui_master_04.py`: 21 test (T9-CANCEL 5 + T9-TOOLTIP-GLOBAL 13 + T9-L10N-AUDIT 3) incluso test generativo `test_all_hud_text_keys_present_in_en_and_it` che estrae via regex tutte le chiavi `_hud_(text|format|named_format)` da `clientgamehud.py` e ne verifica la presenza nelle sezioni `def hud` di EN+IT.

### Changed

- [UI-MASTER-05/T10-CANCEL-SERVER] `soundrts/clientgamehud.py`: firma `_cancel_unit_order` da `(unit)` a `(unit, kind="")`. Backward-compatible (parametro opzionale con default).
- [UI-MASTER-05/T10-TOOLTIP-THROTTLE] `soundrts/tests/unittests/test_ui_master_04.py`: aggiornato `test_map_empty_cell_tooltip_via_set_map_hover` per riflettere il nuovo debounce (un sample singolo non genera più tooltip immediato).
- [UI-MASTER-04/T9-CANCEL] `soundrts/clientgamehud.py`: `_collect_activity` cambia signature di ritorno da 3-tupla a 4-tupla (aggiunto riferimento `unit`). `_draw_activity_panel` usa unpacking permissivo per restare compatibile con i mock 3-tupla dei test esistenti.

### Not Applicable

- [UI-MASTER-05/T10-ENCODING-FIX] **Premessa task falsificata dal sorgente** (LEGGE-6). `soundrts/lib/encoding.py` (`encoding(text, filename)`, linee 22-24) forza incondizionatamente `return "utf-8"` per qualsiasi file il cui basename non è `tts.txt`: il branch chardet è raggiungibile solo per `tts.txt`. Aggiungere `# coding: utf-8` in cima a `res/ui/style.txt` sarebbe puro rumore senza effetto runtime. Nessuna modifica necessaria. Schedulato come nota in `doc_admin/todo.md` per estendere `encoding()` se in futuro verranno introdotti file non-UTF-8 oltre `tts.txt`.

 `soundrts/clientgamehud.py`: API pubblica `HudPanel.rect_for(name)` e `HudPanel.panel_names()` per accesso read-only ai rect dei pannelli HUD. Disaccoppia i consumer esterni dall'attributo privato `_panel_rects`.
- [UI-MASTER-03/T7-COORD] `soundrts/clientgamehud.py`, `soundrts/clientgame.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: tooltip mappa arricchito con coordinate `(col,row)` della cella sotto al cursore. `set_map_hover` e `_build_map_tooltip` accettano `square=None`; `tooltip_map_entity` aggiorna il template includendo `{coords}`. Il segmento è soppresso quando la cella non espone `col`/`row`.
- [UI-MASTER-03/T8-BOTTOMBAR] `soundrts/clientgamehud.py`, `soundrts/clientgamegridview.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: barra inferiore orizzontale full-width con tempo di gioco e velocità su due celle. Nuova costante `HudPanel.bottom_bar_height = 40`. Clip area della mappa estesa anche verso il basso (`sh_effective` sottrae `bottom_bar_height + margin`). Nuove chiavi `bottom_bar_time_fmt`, `bottom_bar_speed_fmt`.
- [UI-MASTER-03/T8-ACTIVITY] `soundrts/clientgamehud.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: pannello ACTIVITY di prima classe con header sempre visibile. Click sull'header (`activity_header` in `_panel_rects`) commuta `activity_visible`. Quando aperto, mostra tab strip + righe ordini con barra di progresso visiva (rettangolo verde proporzionale a `pct`). Ogni riga registra `activity_row_N` per hit-test/tooltip; testi completi conservati in `_activity_row_texts`. Nuove chiavi `activity_collapsed`, `tooltip_activity_show`, `tooltip_activity_hide`.
- [UI-MASTER-03] `res/ui-fr/style.txt`, `res/ui-pt-BR/style.txt`: aggiornati placeholder TODO con le nuove chiavi UI-MASTER-03 + `{coords}` in `tooltip_map_entity`.
- [UI-MASTER-03] `soundrts/tests/unittests/test_ui_master_03.py`: 19 test per C1-HITTEST (rect_for/panel_names), T7-COORD (coordinate + difensive), T8-BOTTOMBAR (rect, posizione, larghezza, TIME panel rimosso), T8-ACTIVITY (header sempre visibile, toggle click, righe + tooltip, fit sopra bottom_bar, label localizzata `(hidden)`).
- [UI-MASTER-02b/T7-EVENTI] `soundrts/clientgamehud.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: tooltip popup sulle righe del pannello EVENTS. Hover su una voce mostra la stringa evento completa (non troncata) tramite `tooltip_event_full`. Registrati rect `event_row_N` in `_panel_rects` e dizionario `_event_row_texts` con i testi completi.
- [UI-MASTER-02b/T7-MAPPA] `soundrts/clientgamehud.py`, `soundrts/clientgame.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: tooltip popup sugli elementi della mappa (unità, edifici, risorse) con delay 400 ms di hover stabile. Nuovi metodi `HudPanel.set_map_hover()`, `HudPanel._build_map_tooltip()`, `HudPanel.is_pos_over_hud()`. Dispatch MOUSEMOTION in `_process_fullscreen_mode_mouse_event` riconosce sovrapposizione HUD e instrada al map-hover solo fuori dai pannelli.
- [UI-MASTER-02b] `res/ui/style.txt`, `res/ui-it/style.txt`, `res/ui-fr/style.txt`, `res/ui-pt-BR/style.txt`: chiavi `[hud]` `tooltip_event_full`, `tooltip_map_entity`, `tooltip_map_hp` (IT: `PV`), `tooltip_map_owner`, `tooltip_map_coords`, `entity_na`. Le altre lingue ereditano dal default EN.
- [UI-MASTER-02b] `soundrts/tests/unittests/test_ui_master_02b.py`: 17 test per BUG-T4 (riserva spazio ACTIVITY), T7-EVENTI (rect + tooltip full text), T7-MAPPA (delay 400 ms, attributi difensivi, sovrapposizione HUD), wiring MOUSEMOTION in `clientgame.py`.
- [UI-MASTER-02b] `tools/_apply_t7_loc.py`: script idempotente per propagare i placeholder localizzati alle lingue secondarie.
- [UI-MASTER-02/T7] `soundrts/clientgamehud.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: tooltip visuali localizzati per controlli HUD cliccabili. Hover su header EVENTS mostra `Show events/Hide events` (IT: `Mostra eventi/Nascondi eventi`); hover sui tab ACTIVITY mostra `Switch to {tab}` (IT: `Vai a {tab}`).
- [UI-MASTER-02/FIX-T5] `soundrts/tests/unittests/test_ui_master_01.py`: test aggiunti per middle-click target assignment, wheel modifiers Ctrl/Shift, tooltip HUD, pattern evento localizzato e layout ACTIVITY in colonna destra.
- [UI-MASTER-01/T3] `soundrts/clientgamehud.py`, `soundrts/clientgame.py`: pannello EVENTS collassabile. Nuovo attributo `HudPanel.events_visible` (default False da UI-MASTER-02), nuovo metodo `cmd_toggle_events()` su `GameInterface` con voicing TTS, hit-test sul rect `events_header` in `HudPanel.handle_mouse_event()`. Header mostra il suffisso `(hidden)` quando collassato.
- [UI-MASTER-01/T4] `soundrts/clientgamehud.py`, `soundrts/clientgame.py`: pannello ACTIVITY con tab-switcher (`TUTTO / ADDESTR. / RICERCHE / COSTR.`). Nuovi attributi `HudPanel.activity_visible`, `HudPanel.activity_tab`. Metodi `_collect_activity()`, `_classify_order()`, `_draw_activity_panel()` aggiunti a `HudPanel`. Comandi `cmd_toggle_activity_panel`, `cmd_activity_tab_{all,training,research,build}` su `GameInterface`. Click sui tab gestito in `handle_mouse_event`. Mostrato contatore tra parentesi per ogni tab; placeholder localizzato quando nessuna produzione attiva.
- [UI-MASTER-01/T5] `soundrts/clientgame.py`: comandi mouse estesi in `_process_fullscreen_mode_mouse_event` — bottone 2 (middle) = `cmd_command_unit` sull'oggetto sotto al cursore; rotella su (`button==4`) = `cmd_select_unit(-1)`; rotella giù (`button==5`) = `cmd_select_unit(1)`. I modificatori Ctrl/Shift sui clic sinistro e destro restano funzionanti.
- [UI-MASTER-01] `res/ui/bindings.txt`: binding HUD aggiornati da UI-MASTER-02 per evitare collisioni con comandi storici: `b` → `toggle_events`, `m` → `toggle_activity_panel`, `COMMA/PERIOD/SLASH/CTRL SLASH` → tab selettori del pannello attività.
- [UI-MASTER-01] `soundrts/msgparts.py`: nuove costanti `EVENTS_SHOWN=[4376]`, `EVENTS_HIDDEN=[4377]`, `ACTIVITY_PANEL_SHOWN=[4378]`, `ACTIVITY_PANEL_HIDDEN=[4379]`, `ACTIVITY_TAB_ALL/TRAINING/RESEARCH/BUILD` (4380-4383).
- [UI-MASTER-01] `res/ui/tts.txt` + 12 file `res/ui-*/tts.txt`: aggiunte voci TTS 4376-4383 (italiano tradotto, EN baseline, restanti lingue con placeholder marcato `; TODO: tradurre`).
- [UI-MASTER-01] `res/ui/style.txt`, `res/ui-it/style.txt`, `res/ui-fr/style.txt`, `res/ui-pt-BR/style.txt`: chiavi `[hud]` `pause_label`, `panel_activity`, `tab_all`, `tab_training`, `tab_research`, `tab_build`, `events_collapsed`, `activity_empty`. Le altre lingue ereditano automaticamente dal default EN.
- [UI-MASTER-01] `soundrts/tests/unittests/test_ui_master_01.py`: 17 test per T1 (copertura TTS 4367-4383 su 13 file), T2 (offset y mappa), T3 (toggle events), T4 (toggle activity + selezione tab + classificazione ordini + raccolta unità), T6 (`display_is_active` con `config.visual_mode`).
- [UI-MASTER-01] `tools/_apply_t1_loc.py`, `tools/_apply_t3t4_loc.py`, `tools/_check_t1_loc.py`: script idempotenti per applicare le voci di localizzazione e verificarne la presenza in tutte le lingue.

### Changed

- [UI-MASTER-03/T8-BOTTOMBAR] `soundrts/clientgamehud.py`: rimosso il pannello `time` dalla colonna destra. Tempo e velocità ora vivono nella barra inferiore globale. La costante di compatibilità `HudPanel.time_height = 88` resta esposta per i consumer legacy ma non è più registrata in `_panel_rects`.
- [UI-MASTER-03] `soundrts/tests/unittests/test_hud_layout.py`, `soundrts/tests/unittests/test_ui_master_02b.py`: aggiornati test layout (PANEL_NAMES senza `time`, viewport mappa con `bottom_reserved`, test legacy TIME riconvertiti in test BOTTOM-BAR) e firma `set_map_hover(target, pos, square=None)` nella dispatch MOUSEMOTION.

### Fixed
- [UI-MASTER-05/T10-CANCEL-SERVER] Risolto il desync UI documentato in UI-MASTER-04: il click su una riga ACTIVITY ora propaga la cancellazione al server (per i kind training/research/build) invece di limitarsi al `pop(0)` client-only sovrascritto al prossimo snapshot.
- [UI-MASTER-02b] `soundrts/clientgamehud.py`: tooltip overlay (`_draw_tooltip`) spostato fuori dal ramo `else` di `if self.activity_visible`, dove era erroneamente confinato. Il popup ora si renderizza in tutti gli stati del pannello attività.
- [UI-MASTER-02/FIX-T3] `soundrts/clientgamehud.py`: `HudPanel.events_visible` ora parte da `False`; il pannello EVENTS è chiuso di default al primo frame e resta apribile via tasto o click header.
- [UI-MASTER-02/FIX-T4] `soundrts/clientgamehud.py`: pannello ACTIVITY riposizionato da bottom-left a colonna destra, subito sotto GROUP, con larghezza `col_right_width=295`. Il calcolo del gruppo riserva spazio verticale minimo quando ACTIVITY è visibile.
- [UI-MASTER-02/FIX-T5] `soundrts/clientgame.py`, `res/ui/bindings.txt`: corrette collisioni binding `ALT a`/`ALT e` con comandi storici (`order_shortcut`, worker idle). Middle-click ora assegna `self.target` prima di chiamare `cmd_command_unit`; rotella mouse supporta Shift=`local`, Ctrl=`idle`.
- [UI-MASTER-02/FIX-T1B] `soundrts/clientgamehud.py`, `res/ui/style.txt`, `res/ui-it/style.txt`: pattern eventi HUD localizzato tramite `event_fmt` e `event_with_place_fmt`, rimuovendo il frammento inglese hardcoded `at` da `_format_event`. Localizzati anche i prefissi visuali attività (`activity_prefix_*`).
- [UI-MASTER-02/Tests] `soundrts/tests/unittests/test_hud_layout.py`, `soundrts/tests/unittests/test_clientsprites.py`, `soundrts/tests/unittests/test_clientgamehud.py`: test legacy aggiornati al contratto T2 (`GridView._y_offset`), al default EVENTS chiuso e al pattern evento localizzato.
- [UI-MASTER-01/T1] `soundrts/clientgamehud.py`: rimossa stringa hardcoded italiana `"|| PAUSA"` nell'overlay pausa (violava LEGGE-4 — niente stringhe UI hardcoded). Sostituita da `self._hud_text("pause_label", "|| PAUSED")` che legge la chiave `pause_label` da `style.txt[hud]` con fallback inglese.
- [UI-MASTER-01/T1] `res/ui-*/tts.txt` (13 file): aggiunte le voci TTS 4367-4375 (SET_SPEED_1..7, PAUSE_ON, PAUSE_OFF) precedentemente presenti solo nel baseline EN. Il menù F10 e la pausa erano voicing in inglese in tutte le lingue diverse da EN; ora l'italiano è tradotto e le altre 11 lingue hanno placeholder EN con marker `; TODO: tradurre` per le traduzioni future.
- [UI-MASTER-01/T2] `soundrts/clientgamegridview.py`: la viewport mappa non rispettava lo spazio occupato dalla barra risorse HUD (top bar 40 px + margini). Aggiunto attributo `GridView._y_offset` calcolato dinamicamente in `_update_coefs` come `HudPanel.res_bar_height + 2*margin + HUD_MAP_MARGIN(=4)` (= 60 px) e applicato a `_get_view_coords_from_world_coords`, `_get_rect_from_map_coords`, `_display` (bordo mappa), `square_from_mousepos` (inverso per i click). `sh` effettivo ridotto di `_y_offset` per evitare compressione della mappa.
- [UI-MASTER-01/T6] `soundrts/clientgame.py`: `display_is_active` ora include `bool(config.visual_mode)`. Senza questo fix, abilitare `visual_mode=1` in `cfg/parameters.toml` creava la finestra in fullscreen ma il flag interno `fullscreen` restava False, e il rendering HUD/mappa veniva soppresso fino a quando l'utente premeva CTRL+F2.

- [Speed+Pause] `soundrts/clientgame.py`: sistema a 7 livelli di velocità graduali (0.25 / 0.5 / 1.0 / 2.0 / 3.0 / 4.0 / 5.0×) con metodi `gm_speed_1()` … `gm_speed_7()`. Rimossi i 4 metodi obsoleti `gm_slow_speed`, `gm_normal_speed`, `gm_fast_speed`, `gm_very_fast_speed`. `cmd_gamemenu()` aggiornato con 7 voci.
- [Speed+Pause] `soundrts/clientgame.py`: pausa stile Paradox — flag `is_paused`, metodo `cmd_toggle_pause()` che sospende il loop di aggiornamento server senza bloccare la coda ordini client. Alla ripresa `next_update` viene azzerato a `time.time()` per riprendere immediatamente. `_time_to_ask_for_next_update()` rispetta il flag.
- [Speed+Pause] `soundrts/clientgamehud.py`: overlay visivo "|| PAUSA" giallo centrato, attivo solo quando `is_paused` è True. Metodo `_draw_pause_overlay()` aggiunto; layout HUD esistente invariato.
- [Speed+Pause] `res/ui/bindings.txt`: doppio binding `PAUSE` e `ALT p` → `toggle_pause` (sezione miscellaneous). Nessun binding esistente rimosso.
- [Speed+Pause] `soundrts/msgparts.py`: costanti `SET_SPEED_1` … `SET_SPEED_7` (IDs 4367–4373), `PAUSE_ON` (4374), `PAUSE_OFF` (4375). Costanti precedenti mantenute per retrocompatibilità.
- [Speed+Pause] `res/ui/tts.txt`: voci TTS 4367–4375 per i 7 livelli velocità e pausa/ripresa.
- [Speed+Pause] `soundrts/tests/unittests/test_speed_and_pause.py`: 18 test (16 originali + 2 per `__setstate__` retrocompatibilità: save pre-Task1 senza `is_paused`, save-while-paused che viene reset).

### Fixed

- [Speed+Pause] `soundrts/clientgame.py`: `AttributeError: 'GameInterface' object has no attribute 'is_paused'` nel loop `_time_to_ask_for_next_update()` quando si carica un save file creato prima dell'introduzione della feature pause (il path di deserializzazione `cloudpickle.load → __setstate__` non passava da `__init__`). Fix duale: (1) `is_paused = False` aggiunto come attributo di classe come fallback universale; (2) `__setstate__` imposta esplicitamente `self.is_paused = False` per garantire stato neutro al caricamento, indipendentemente dall'età del save.

 nuovo modulo `SpriteCache` per la Visual UI. API pubblica: `get(category, name, size)` lazy con cache `dict[str, Surface | None]` chiavata su `"{cat}/{name}@{size}"`, `clear()` per invalidazione su resize, `category_of(o)` resolver statico (lookup hardcoded delle 54 entità rinderizzabili documentate in `tools/sprite_mapping.csv`). Errori file/pygame → `None` (fallback geometrico). I PNG completamente trasparenti generati da R15-B (`tools/normalize_sprites.py`) vengono rilevati via sampling alpha sui quattro angoli + centro e trattati come "sprite assente" per preservare il fallback.
- [R16] `soundrts/clientgamegridview.py`: integrazione additiva sprite in 3 punti — PR-1 in `_display()` (blit del terrain sprite sopra `draw_rect` di fondo, con `sq.type_name.lstrip("_")` per i terreni auto-applicati), PR-2 in `display_object()` ramo `shape == "square"` (buildings), PR-3 in `display_object()` ramo circle (units/resources). Tutti i fallback geometrici preesistenti restano invariati. Aggiunto metodo `GridView.invalidate_sprite_cache()` come hook per futuri cambi di risoluzione.
- [R16] `soundrts/tests/unittests/test_clientsprites.py`: 21 test (cache miss/hit/clear/reuse, placeholder trasparente → None, integrazione PR-1 con `_display`, fallback PR-2/PR-3 in `display_object`, `category_of` parametrizzato su 10 type_name più caso senza `type_name`, sentinel `_IMG_ROOT` coincide con `<repo>/res/img/`).

### Changed

- [R16] HUD: pannello risorse convertito da layout verticale a barra orizzontale stile Age of Empires (top bar). Le risorse sono ora visualizzate affiancate su una singola riga nella parte superiore dello schermo (`height=40px`, larghezza intera `screen_w - 2*margin`). Ogni risorsa occupa una cella proporzionale con testo centrato; l'ultima cella mostra `Pop/Food`. Separatori verticali `(70,110,120)` tra le celle. Tutti i pannelli sottostanti (TIME, EVENTS, PLAYER, GROUP) riposizionati di conseguenza tramite `res_bar_bottom = margin + res_bar_height + margin`. Aggiunta costante di classe `HudPanel.res_bar_height = 40`.
- [R16] `.gitignore`: esclusi `/res/img/` (54 PNG asset binari generati localmente da `tools/normalize_sprites.py`) e `/tools/sprite_validation_report.txt` (output volatile QA). Coerente con la decisione D2 di R15-B (no `git add` su binari).

### Notes

- [R16] Decisione architetturale: `_IMG_ROOT = Path(__file__).resolve().parent.parent / "res" / "img"`. Il piano R15 ipotizzava `Path(BASE_DIR) / "res" / "img"`, ma `BASE_DIR` non è esposto da `soundrts/paths.py`. Il path relativo al modulo è più robusto (segue il modulo se reinstallato come package).
- [R16] LEGGE-1 (audio-only invariant) e LEGGE-5 (visual_mode=0 mai chiama `clientsprites`) verificate: `clientgamegridview` è l'unico modulo che importa `clientsprites`, e viene istanziato solo in `visual_mode=1`.
- [R16] Suite finale: 322 passed / 1 skipped / 0 failed (era 301 baseline R15-B + 21 nuovi test). Nessuna regressione.
- [R16] Nessun bump di versione: funzionalità additiva, comportamento visivo identico al pre-R16 quando `res/img/` è assente (fallback geometrico totale). Eventuale bump `1.4.4` rimandato a un round che chiude più feature insieme.

### Added

- [R15-B] `res/img/{units,buildings,resources,terrain,ui}/`: nuova radice asset grafici 2D. 54 PNG RGBA obbligatori generati dal pack Kenney Medieval RTS (`PNG/Retina/`) o come placeholder trasparente quando non esiste una controparte semantica nel pack (zombie, skeleton, catapult, dragon, flyingmachine, naval units, goldmine, dragonslair, shipyard, buildingsite). Dimensioni: 32x32 per units/resources, 64x64 per buildings/terrain/ui. Pronto per la `SpriteCache` di Round 16.
- [R15-B] `tools/normalize_sprites.py`: dev-tool basato su Pillow che converte gli sprite sorgente in RGBA, ridimensiona con LANCZOS e li salva in `res/img/<categoria>/<type_name>.png`. Scrive `tools/sprite_mapping.csv` come audit trail (sorgente, dimensioni originali/finali, livello match, status).
- [R15-B] `tools/validate_sprites.py`: dev-tool QA che verifica presenza, modo RGBA, dimensioni esatte e classifica ogni sprite (OK / PLACEHOLDER / MANCANTE / ERRORE_FORMATO). Output testuale NVDA-friendly su stdout e su `tools/sprite_validation_report.txt`.
- [R15-B] `soundrts/tests/unittests/test_sprite_tools.py`: 9 test che proteggono il contratto della pipeline sprite (54 entry obbligatorie, categorie note, contratto placeholder trasparente, classificazione errori formato).

### Changed

- [R15-B] `doc_admin/round15_sprite_plan.md` e `doc_admin/round15_sprite_report.md`: corretto il percorso target degli sprite da `img/` (root del workspace) a `res/img/` (sottocartella di `res/`). Aggiornati anche gli snippet di codice (`_IMG_ROOT = Path(BASE_DIR) / "res" / "img"`) coerentemente con la convenzione resource del progetto.

### Notes

- [R15-B] Decisione operativa: i 54 PNG generati NON vengono committati automaticamente (LFS / `.gitignore` su `res/img/` resta una decisione operatore). Pillow è installata come dev-dependency nel venv ma NON è stata aggiunta a `requirements.txt` (tooling, non runtime).
- [R15-B] Tutte le 40 corrispondenze MATCH_MEDIO con il pack Kenney sono state assegnate per indice del file sorgente senza ispezione visiva sprite-per-sprite. Ogni riga di `tools/sprite_mapping.csv` riporta una nota esplicativa; si consiglia revisione visiva operatore prima del rendering definitivo in Round 16.

## [1.4.3] — 2026-05-25

> Round 13 + Round 14: chiusura sospesi R11 (cataloghi i18n hint visuali, allineamento `version.py`) e revisione/release prep (qualità i18n, fallback update-check, bump finale 1.4.3).

### Added

- [R13-T2] `res/ui-{be,cs,de,es,fr,pl,pt-BR,ru,sk,vi,zh}/tts.txt`: aggiunti i token `4365` (`VISUAL_MENU_HINT`) e `4366` (`VISUAL_DIALOG_HINT`) per coprire tutte le lingue rilasciate. Le traduzioni sono prodotte come adattamento meccanico della versione EN/IT e devono essere riviste da madrelingua.
- [R13-T2] `soundrts/tests/unittests/test_i18n_hints.py`: 27 test parametrizzati che verificano la presenza dei token `4365`/`4366` in ogni catalogo `res/ui*/tts.txt`.
- [R14-T2] `soundrts/tests/unittests/test_version_check.py`: 3 test che verificano il fallback silenzioso di `RevisionChecker.run()` per HTTP 404, `TimeoutError` e `URLError`, garantendo l'invariante audio-only anche quando l'endpoint `http://jlpo.free.fr/soundrts/<major.minor>version.txt` non è disponibile.

### Changed

- [R13-T3 / R14-T3] `soundrts/version.py`: `VERSION` allineata da `"1.3.8.1"` a `"1.4.3"` in coerenza con questa sezione del changelog. Il bump è sicuro perché `server_is_compatible()` confronta `SERVER_COMPATIBILITY="0"` e non la stringa `VERSION`; l'unico effetto pratico è l'URL del check "update available" che ora punta a `1.4version.txt`.

### Notes

- [R13-T1] SOSPESO-A (handler `WINDOWRESIZED`/`WINDOWSIZECHANGED`): SCARTATO-PREMATURO. `lib/screen.set_screen()` usa `pygame.FULLSCREEN` sia per gameplay sia per `visual_mode=1`; `RESIZABLE` non è mai impostato, quindi un handler resize sarebbe codice morto.
- [R14-T1] Revisione qualità delle traduzioni i18n 4365/4366: tutte le 11 lingue (`be, cs, de, es, fr, pl, pt-BR, ru, sk, vi, zh`) sono state classificate ACCETTABILI secondo il criterio struttura "tasto: azione" e tasti fisici universali in EN. Per `vi` e `zh` la revisione madrelingua resta consigliata e tracciata come TODO Round 15.
- [R14-T2] Endpoint `http://jlpo.free.fr/soundrts/1.4version.txt` non disponibile (HTTP 404). Il fallback è già silenzioso grazie al `try/except` esistente in `RevisionChecker.run()`; rischio residuo: nessuna notifica di nuove versioni per utenti 1.4.x, tracciato come TODO Round 15 a bassa priorità.

## [1.4.2] — 2026-05-26

> Ciclo Round 12: auto-detect lingua OS, conferma mouse gameplay, etichette HUD risorse localizzate.

### Added

- [R12-T1] `soundrts/lib/resource.py`: `_normalize_locale_code()` helper che converte il nome locale di sistema (formato Windows `"Italian_Italy"` o POSIX `"it_IT"`) in codice ISO-639-1 a 2 caratteri tramite `locale.normalize()` + fallback split.
- [R12-T1] `soundrts/lib/resource.py`: `_preferred_language()` ora rileva la lingua del SO tramite `locale.getlocale()` quando `cfg/language.txt` è assente o vuoto, invece di tornare immediatamente a `"en"`.
- [R12-T1] `soundrts/clientmain.py`: `_seed_language_file()` scrive il codice ISO-639-1 in `cfg/language.txt` al primo avvio se il file è assente o vuoto; non sovrascrive scelte esplicite dell'utente.
- [R12-T3] `soundrts/clientgamehud.py`: `_resource_name()` risolve i token numerici (`131`, `132`, …) tramite `sounds.translate_sound_number()` invece di scartarli; le etichette HUD mostrano ora i nomi localizzati ("oro"/"legno" in italiano, "gold"/"wood" in inglese) coerentemente con il sistema TTS.

### Fixed

- [R12-T1] BUG: `_preferred_language()` ignorava `locale.getlocale()` quando `cfg/language.txt` mancava, tornando sempre a `"en"` → UI Visual mostrava stringhe in inglese anche su sistemi configurati in un'altra lingua.
- [R12-T3] BUG: `_resource_name()` in `clientgamehud.py` scartava i token numerici di stile (`resource_0_title 131`) con un filtro `p.isdigit()`, producendo sempre le etichette fallback "Resource 1"/"Resource 2" anche quando il sistema TTS aveva la traduzione disponibile.

### Tests

- [R12-T1] `soundrts/tests/unittests/test_clientmain_lang.py`: 6 test — normalizzazione formato Windows/POSIX, seed file assente, nessuna sovrascrittura, locale None silenzioso.
- [R12-T2] `soundrts/tests/unittests/test_gameplay_mouse.py`: 7 test — verifica struttura handler mouse (già implementato in R11), guard `display_is_active`, comportamento click sx/dx/centrale.
- [R12-T3] `soundrts/tests/unittests/test_hud_resources.py`: 4 test — fallback senza stile, token IT "oro"/"legno", token EN "gold"/"wood", token non risolto → fallback.

## [1.4.1] — 2026-05-25

> Ciclo Visual UI menu Round 8→11 stabilizzato, localizzato e con suite verde.

<!-- Visual Mode Round 8 — 2026-05-25 -->

### Added

- [VIS-MODE-1] Nuova opzione `config.visual_mode` (int 0/1, default 0): commuta la UI dei menu da audio-only a fullscreen visuale. Persiste in `SoundRTS.ini` sezione `[general]`. Quando 0, comportamento legacy invariato (audio-first, NVDA-compatibile).
- [VIS-MODE-1] `soundrts/clientvisualui.py`: `ScreenManager` singleton con stack `push/pop/update_current/cleanup` e hit-test mouse (`handle_mouse_motion`, `handle_mouse_click`). Tutti i metodi gated da `config.visual_mode` (no-op se OFF).
- [VIS-MODE-1] `soundrts/clientmenuscreen.py`: `MenuScreen` (header/body/footer, finestra scroll auto-centrata, item rect per click), `DialogScreen` (pannello centrato con scrim per input). Helper `_label_to_str` mai solleva eccezioni (token sound/str/None tutti gestiti).
- [VIS-MODE-1] `clientmedia.toggle_visual_mode()` e `get_visual_mode()`: commutazione runtime con salvataggio config + annuncio TTS (`DISPLAY_ON`/`DISPLAY_OFF`).
- [VIS-MODE-1] Voce dinamica "Visivo ON/OFF" nel menu Opzioni (`clientmain.options_menu`). Scorciatoia `Ctrl+F2` nei menu commuta visual mode (in gameplay continua a commutare fullscreen del gioco, invariato).
- [VIS-MODE-1] Supporto mouse additivo nei menu (LEGGE-6): movimento sposta selezione + TTS, click conferma. Tastiera resta primaria e invariata.
- [VIS-MODE-1] `msgparts.VISUAL_MODE_ON`/`VISUAL_MODE_OFF` come alias di `DISPLAY_ON`/`DISPLAY_OFF`.
- [VIS-MODE-1] `lib/screen.set_screen`: quando `fullscreen=False` e `config.visual_mode=1`, usa `FULLSCREEN` desktop per i menu. Path gameplay (`fullscreen=True`) invariato.

### Added (Round 11)

- [R11-A] Aggiunte 2 stringhe Visual UI al sistema di localizzazione `tts.txt`:
  - `4365` / `msgparts.VISUAL_MENU_HINT`: EN `Arrow keys: navigate. Enter: confirm. Esc: back. Ctrl+F2: visual off`; IT `Frecce: naviga. Invio: conferma. Esc: indietro. Ctrl+F2: visivo off`.
  - `4366` / `msgparts.VISUAL_DIALOG_HINT`: EN `Enter: confirm. Esc: cancel. Ctrl+F2: visual off`; IT `Invio: conferma. Esc: annulla. Ctrl+F2: visivo off`.

### Fixed (Round 11)

- [R11-A] Rimosse stringhe visibili hardcoded dal Visual UI:
  - `clientvisualui.py`: i footer menu/dialogo usano ora token `msgparts` localizzati.
  - `clientmenuscreen.py`: il fallback titolo `Menu` usa `mp.MENU` invece di testo hardcoded.
- [R11-A] Aggiunto `test_visual_footer_hints_use_localized_msgparts` per garantire che i footer Visual UI passino dalla stessa pipeline di localizzazione audio (`SoundCache.translate_sound_number`).

### Changed (Round 11 — B1.6)

- [R11-B] `VIDEORESIZE`/`WINDOWRESIZED` documentato come non pratico nell'assetto attuale: `visual_mode=1` usa `pygame.FULLSCREEN` e non `RESIZABLE`, quindi il resize utente non e' raggiungibile nel flusso normale. Nessun handler aggiunto.

### Tests

- `test_visual_ui.py`: 13 test (9 Round 8 + 2 Round 9 audit + 1 Round 10 + 1 Round 11).
  Aggiunto `test_mouse_button_right_click_ignored` (B1.4): verifica che solo button=1 confermi la scelta.
  Aggiunto `test_visual_footer_hints_use_localized_msgparts` (Round 11): verifica footer Visual UI localizzati via `msgparts`.
- Suite globale Round 11: **245 passed / 0 failed / 0 errors**.

### Fixed (Round 10 — Obiettivo A: residuo suite)

- [R10-A] Rimossi `ResourceWarning` da file handle non chiusi (Round 9 residuo):
  - `soundrts/servermain.py`: `WHATISMYIP_URL` usa context manager.
  - `soundrts/metaserver.py`: `MAIN_METASERVER_URL` e `_default_servers()` usano context manager.
  - `soundrts/campaign.py`: 4 handle non chiusi in `CutSceneChapter._load()`,
    `Campaign._set_title_and_mods()`, `Campaign._set_mods_from_mods_txt()`, `Campaign._set_chapters()`.
  - `soundrts/mapfile.py`: `_load_from_package()` usa context manager.
  - `soundrts/lib/package.py`: `PackageStack.mod()` usa context manager.
  - `soundrts/tests/test_config.py`: 4 `open()` bare nel test sostituiti con `with`.
- [R10-A] Creati fixture dir mancanti per test package/resource:
  - `soundrts/tests/res2/mods/mod2/.gitkeep`
  - `soundrts/tests/res2/mods/sound1/.gitkeep`
  - Questo risolveva `test_subpackage_dirnames` e `test_update` (FAILED in Round 9).

### Changed (Round 10 — Obiettivo B: audit Visual UI)

- [R10-B1] `soundrts/clientmenu.py`: `_try_to_get_choice()` filtra `MOUSEBUTTONDOWN` a `button == 1`.
  Click destro (button 2/3) e scroll (button 4/5) non confermano piu la selezione del menu (GRAVITÀ MEDIA).
- [R10-B2] `soundrts/clientmenu.py`: `Menu.__init__` e `_execute_choice()` ora usano context manager per `open()` nel meccanismo `remember` (ResourceWarning prevenuto, GRAVITÀ BASSA).

### Fixed

- [R9-A] Rimossa chiamata deprecata `locale.getdefaultlocale()` in `soundrts/lib/resource.py`, sostituita con `locale.getlocale()` + fallback esplicito a `"en"`.
- [R9-A] Rimossi `ResourceWarning` da file handle non chiusi nel codice progetto:
	- `soundrts/config.py`: `save()` e `load()` ora usano context manager.
	- `soundrts/lib/resource.py`: stream map chiusi in `official_multiplayer_maps()` e `_add_custom_multi()`.
	- `soundrts/mapfile.py`: apertura mappe `.txt` via context manager.
- [R9-A] Rimosso filtro temporaneo `ignore:Use setlocale.*:DeprecationWarning` da `pytest.ini` (workaround Round 8 non piu necessario).

### Changed (Round 9 — audit Round 8)

- [R9-B] `soundrts/clientmenu.py`: `Menu.update_menu()` aggiorna ora lo stack visivo in-place tramite `ScreenManager.update_current(...)` quando `visual_mode=1`.
- [R9-B] `soundrts/clientmain.py`: `set_and_launch_mod()` e `set_and_launch_soundpack()` invocano `get_screen_manager().cleanup()` prima di `SystemExit`.

## [1.4.0] — 2026-05-24

> Ciclo UI visuale Round 1→7 completato. Confermato funzionante su partita reale (runtime test).

<!-- MAP Layout Round 7 — 2026-05-24 -->

### Changed

- [MAP-VIEWPORT-1] `GridView._update_coefs()`: la mappa usa `map_w = max(sw//2, sw-303)` invece della larghezza schermo intera. La colonna HUD destra da 295px piu margine non viene piu coperta dalla mappa.
- [MAP-SCALE-1] `UNIT_SCALE=2.0` (R7b): le unita sono disegnate con `R_vis = max(R_MIN, int(R * 2.0))`. La hit-detection usa ancora `R` (`R2 = R*R` invariato).
- [MAP-SCALE-1] `display_attack()` aggiornato con `R_vis` per il raggio visuale del bersaglio.

### Added

- [MAP-VIEWPORT-1] `GridView._hud_right_width()`: costante locale 303px coerente con `col_right_width` 295px + `margin` 8px di `HudPanel`.

### Tests

- `test_hud_layout.py`: 105 passed, 0 failed (+16 Round 7 tests/updates; R7b: UNIT_SCALE 1.5→2.0).

<!-- UI Fix Round 6 — 2026-05-24 -->

### Changed

- [HUD-1] Allineamento colonna destra HUD: `event_width` 260→295 unificato in `col_right_width=295`. Il bordo sinistro di EVENTS ora coincide con PLAYER e GROUP (tutti ancorati a `right - 295`).
- [MAP-1] `R_MIN = 4` introdotto in `clientgamegridview.py`: le unità sulla mappa hanno raggio minimo 4px garantito in qualsiasi configurazione di mappa.
- [MAP-2] Marker fazione: raggio `max(2, R // 2)` — visibile anche su mappe grandi con R basso.
- [MAP-3] Barra HP: `W = max(3, R - 2)` — larghezza minima 6px totali garantita.

### Tests

- `test_hud_layout.py`: 89 passed, 0 failed (+21 Round 6 tests).
- Aggiunto `test_events_aligned_with_group` (T_EVENTS_ALIGNED_WITH_GROUP, 6 risoluzioni).
- Aggiunto `test_faction_marker_min` (T_FACTION_MARKER_MIN, 7 valori R).
- Aggiunto `test_hp_bar_w_min` (T_HP_BAR_W_MIN, 7 valori R).
- Aggiunto `test_r_min_constant` (T_R_MIN_ENFORCED).

<!-- UI Fix Round 5 — 2026-05-24 -->

### Changed

- [R5] Pannelli PLAYER e GROUP spostati da basso-sinistra a basso-destra, right-anchored sotto EVENTS (`soundrts/clientgamehud.py`). La colonna sinistra è ora libera (solo RES rimane in top-left), restituendo spazio mappa.
- [R5] Strategia adattiva overflow GROUP: il numero di unità mostrate si adatta dinamicamente allo spazio verticale disponibile (`max_units_fit = available_h // line_height`), evitando che GROUP esca dallo schermo a basse risoluzioni.
- [R5] `min_height` mantenuto a 360px (minimo teorico ricalcolato 284px, margine confermato).

### Tests

- `test_hud_layout.py`: 68 passed, 0 failed (+5 Round 5 tests parametrizzati su 6 risoluzioni funzionali).
- Aggiunto `test_player_panel_is_right_anchored` (T_PLAYER_RIGHT_ANCHORED).
- Aggiunto `test_group_panel_is_right_anchored` (T_GROUP_RIGHT_ANCHORED).
- Aggiunto `test_group_panel_does_not_overflow` (T_GROUP_NO_OVERFLOW).
- Aggiunto `test_player_below_events` (T_PLAYER_BELOW_EVENTS).
- Aggiunto `test_adaptive_units_cap` (T_ADAPTIVE_UNITS, worst-case 8 unità).

<!-- UI Fix Round 4 — 2026-05-24 -->

### Fixed

- [FIX-1] `screen_render_subtitle()`: added `if not _subtitle: return` guard to skip rendering when the subtitle is empty, preventing a spurious black background rectangle from appearing on screen (`soundrts/lib/screen.py`).
- [FIX-1] Forensic analysis confirmed: `clientgamegridview.py` contains zero text rendering; the subtitle path has been correctly anchored to bottom-right since Round 2+3 via `_subtitle_position()`.

### Changed

- [FIX-2] `_parts_to_text()`: removed the `isdigit` filter — numeric string tokens are now preserved as-is, allowing HUD values such as "Pop: 0" or resource counts to display correctly (`soundrts/clientgamehud.py`).
- [FIX-2] `_resource_name()`: digit filter applied explicitly here only, before calling `_parts_to_text()` — pure-digit tokens in the `parameters` style section (type/sound IDs) are still discarded as before, preserving existing resource label behaviour.

### Tests

- `test_hud_layout.py`: 38 passed, 0 failed (+4 Round 4 tests).
- Added `test_parts_to_text_preserves_numbers` (T_PARTS_TO_TEXT_PRESERVES_NUMBERS).
- Added `test_parts_to_text_preserves_zero_in_list` (T_PARTS_TO_TEXT_ZERO).
- Added `test_resource_name_strips_digit_style_tokens` (T_RESOURCE_NAME_STRIPS_DIGITS).
- Added `test_infobar_subtitle_rendering_path_confirmed` (T_INFOBAR_POSITION, multi-resolution forensic).

<!-- UI Fix Round 3 + i18n IT — 2026-05-24 -->

### Fixed

- [FIX-1] Status bar: corrected the runtime fallback path in `screen_subtitle_set()` so non-game-mode subtitle rendering now uses the same bottom-right anchor as `screen_render_subtitle()` (`x = width - text_width - 16`, `y = height - text_height - 4`).

### Changed

- [FIX-2] Further upgraded HUD body font to Arial 20 bold (from 17), header font to 24 bold, and small font to 18 regular for improved fullscreen readability.
- Updated HUD geometry for the larger font: `line_height` 23 → 26 px, `min_height` 308 → 360 px, `time_height` 68 → 88 px, and dynamic panel header space to 36 px.
- Reduced EVENTS text fit length to 23 characters to keep long event labels within the 260 px panel after the font increase.

### Added

- [FIX-3] Added 18 localizable graphical HUD strings through the existing `style.get("hud", ...)` system, with Italian values in `res/ui-it/style.txt` and English base values in `res/ui/style.txt`.
- Added automated Round 3 layout tests for HUD font constants, subtitle bottom-right positioning, and Italian HUD i18n keys.

### Tests

- `test_hud_layout.py`: 34 passed, 0 failed.

<!-- UI Fix Round 2 — 2026-05-24 -->

### Fixed

- [FIX-C] TIME panel height raised from 60 to 68 px, eliminating the critical 1 px bottom margin that caused text descender clipping on some systems.
- [FIX-B] Status bar (`screen_render_subtitle`) repositioned from horizontal center to bottom-right anchor (`x = width - text_width - 16`, `y = height - text_height - 4`), eliminating overlap with the game map.
- Fixed a critical overlap between the RES and EVENTS HUD panels at 420×260 resolution by raising `HudPanel.min_width` from 420 to 460 and `HudPanel.min_height` from 260 to 280; the 420×260 resolution is now correctly excluded from the HUD rendering path.
- Fixed the RES panel height calculation that omitted the food row: `res_rect` height now uses `30 + (len(resources) + 1) * line_height` instead of `len(resources)`.

### Changed

- [FIX-A] Further upgraded HUD body font to Arial 17 bold (from 14) for improved readability on real fullscreen monitors; `HudPanel.line_height` updated from 19 to 23 px (font height 20 px + 3 px inter-line gap); `HudPanel.min_height` raised to 308 to maintain panel geometry with the larger font.
- [FIX-A] Scaled HUD font hierarchy: header font 18 → 21 bold, small font 12 → 15 regular (body+4 / body-2 rule).
- Upgraded HUD body font from Arial 12 bold to Arial 14 bold for improved readability at all resolutions; `HudPanel.line_height` updated from 15 to 19 px.
- Scaled HUD font hierarchy proportionally (session Round 1): header font 16 → 18 bold, small font 11 → 12 regular.
- Updated `test_hud_layout.py`: `FUNCTIONAL_RESOLUTIONS` now starts at 640×480 (420×260 moved to below-threshold bucket); T1 boundary test updated to 420×260.

### Tests

- Added `test_time_panel_has_minimum_height` (T_TIME_PADDING): asserts TIME panel height ≥ 68 px across all functional resolutions.
- `T_SUBTITLE_RIGHT` documented as a manual runtime test in `test_hud_layout.py` (requires a live pygame display).

### Added

- Added a Pygame HUD overlay for active visual displays, showing resources, population, selected group status, game time, speed, and recent gameplay events.
- Added unit tests for HUD snapshot collection and event buffering.
- Added technical planning and validation notes under `doc_admin/` for the HUD extension.
- Added a typographic hierarchy to `soundrts.lib.screen` (`screen_render_header`, `screen_render_small`) with safe SysFont fallbacks for systems without Arial.
- Added a `HudEvent` dataclass and severity classification (combat/info/alert) with colour-coded prefixes (`!`, `+`, `*`) in the HUD events panel.
- Added a HUD `PLAYER` panel showing the current player's name and faction when available.
- Added a `HudPanel.handle_mouse_event` no-op hook in `GameInterface._process_fullscreen_mode_mouse_event` to reserve a future hit-test path for clickable HUD widgets without altering current RTS mouse behaviour.
- Added new HUD tests for severity classification, the no-op mouse hook, and the player line fallbacks.
- Added technical planning documents `docs/ui-visual-plan.md`, `docs/ui-color-palette.md`, `docs/ui-hud-layout.md` describing the visual optimisation roadmap for sighted players.

### Changed

- Integrated the HUD into `GameInterface` without changing `GridView`, world simulation, networking, or audio behavior.
- Improved tactical grid readability for sighted players in `clientgamegridview`: differentiated fallback palette for `_meadows`/`_forest`/`_dense_forest`, lighter walls `(230,230,230)`, brighter neutral faction flag `(180,180,180)`, brighter own-faction flag `(60,140,60)`, thicker active-zone border (width 2), and a more visible observer marker (yellow `(255,230,90)`, radius 4, width 2).
- Promoted HUD panel headers (`RES`, `TIME`, `EVENTS`, `GROUP`, `PLAYER`) to a dedicated Arial 16 bold font and highlighted resource values in bright yellow `(255,235,130)`; added a speed icon prefix (`>>`, `>`, `=`).

### Notes

- Full pytest validation on Python 3.12 is currently blocked by an existing `locale.getdefaultlocale()` deprecation warning treated as an error by `pytest.ini`; see `doc_admin/ANOMALIA-TEST-2026-05-23.md`.
