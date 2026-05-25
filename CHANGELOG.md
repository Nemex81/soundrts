# Changelog

## [Unreleased]

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
