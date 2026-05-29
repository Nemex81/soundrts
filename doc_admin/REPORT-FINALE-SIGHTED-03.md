# REPORT-FINALE — UI-SIGHTED-03

**Data**: 29 maggio 2026  
**Round**: UI-SIGHTED-03 (wave 3 sighted UX, DEBITO-02 chiuso)  
**Modalità**: COMPLETAMENTE AUTONOMO (A02+A09+A10)  
**Output finale**: **515 passed, 1 skipped** (baseline 500/1 → +15 test, 0 regressioni)

---

## Task completati

### SI-08 (ALTA, 🔁 DEBITO-02) — Hotkey dinamiche da bindings.txt

- `HudPanel._load_bindings_from_file(path)` + `_get_bindings()` con cache lazy infinita.
- Parser robusto: skip commenti `;`/`#`, gestione `KEY[ MOD ...]: action [args]`, prima associazione vince.
- `_KEYS_HOTKEYS` esteso a 4-tuple `(default_key_label, l10n_key, default_desc, bindings_action_name)`.
- 8 voci mappate alle azioni reali SoundRTS (non più S/A/P hardcoded).
- L10N EN+IT (16 chiavi totali nuove).
- Pannello allargato 240→280 px, formato `{:<12} {}` per hotkey lunghe (PAGEUP/DN, CTRL+SPACE).

### SI-09 (MEDIA, 🔁 DEBITO-02) — Badge stack per categoria proprietario

- `GridView.display_objects()` rifattorizzato: bucket per cella E per categoria (`own`/`enemy`/`ally`).
- Classify via `obj.player is interface.player` + `player_is_an_enemy()` con safe-fallback `ally`.
- `_draw_stack_badge()` esteso con parametri opzionali `color` e `border_color` (retrocompat firma legacy).
- Palette: verde `(60,166,60)` own / rosso `(166,60,60)` enemy / grigio `(100,100,120)` ally.
- O(N) invariato, K=3 op/oggetto.

### SI-10 (BASSA, 🔁 DEBITO-02) — Cursore SIZEALL durante rubber-band drag

- Cursore `sizeall` (pattern 8×8 4-frecce, hotspot 4,4) registrato in `lib/mouse.py`.
- `GameInterface._apply_rubber_band_cursor(pos)` helper testabile in isolamento.
- Iniezione in MOUSEMOTION handler con `getattr` difensivo (compat SimpleNamespace).
- Priorità: sizeall > attack > diamond. Guardia `display_is_active`.

---

## Test introdotti

| Test | Sezione | Numero |
|---|---|---|
| `test_load_bindings_*` (5 test) | SI-08 | 5 |
| `test_badge_*_color`, `test_display_objects_groups_by_owner` (4 test) | SI-09 | 4 |
| `test_*_rubber_band_*`, `test_sizeall_cursor_registered_in_mouse_lib`, `test_priority_sizeall_over_attack` (6 test) | SI-10 | 6 |
| **TOTALE** | | **15** |

Aggiornato (LEGGE-7): `test_ui_sighted_02.py::test_keys_panel_has_eight_hotkey_entries` adattato al nuovo 4-tuple `_KEYS_HOTKEYS`.

---

## File modificati

| File | Tipo | LOC delta |
|---|---|---|
| `soundrts/clientgamehud.py` | core | +60 -8 |
| `soundrts/clientgamegridview.py` | core | +52 -15 |
| `soundrts/clientgame.py` | core | +28 -0 |
| `soundrts/lib/mouse.py` | core | +10 -0 |
| `res/ui/style.txt` | L10N EN | +9 -0 |
| `res/ui-it/style.txt` | L10N IT | +9 -0 |
| `soundrts/tests/unittests/test_ui_sighted_03.py` | test (nuovo) | +268 |
| `soundrts/tests/unittests/test_ui_sighted_02.py` | test (LEGGE-7) | +7 -4 |
| `CHANGELOG.md` | docs | +25 -0 |
| `doc_admin/todo.md` | docs | +14 -0 |
| `doc_admin/report_sighted_ux_01.md` | docs | +32 -0 |
| `doc_admin/REPORT-REV-SIGHTED-03.md` | docs (nuovo) | +160 |
| `doc_admin/REPORT-FINALE-SIGHTED-03.md` | docs (nuovo) | questo file |

---

## Audit gates pre-commit

| Gate | Risultato |
|---|---|
| `py_compile` su src/ | ✅ |
| Pylance `get_errors` su 4 file Python | ✅ 0 errori |
| `pytest` suite completa | ✅ **515 passed, 1 skipped** |
| Print check src/ | ✅ zero `print(`, log via `sys.stderr` |
| LEGGE-3 L10N EN+IT | ✅ 8/8 chiavi |
| LEGGE-7 mai cancellare | ✅ test obsoleti aggiornati, non rimossi |
| LEGGE-9 no-touch zones | ✅ logica audio / SI-03b / enemy_at_mousepos intatti |
| LEGGE-10 test self-contained | ✅ zero import cross-test |

---

## Comandi git proposti (NON ESEGUITI — LEGGE-1 git-policy)

```bash
git add res/ui/style.txt res/ui-it/style.txt \
        soundrts/clientgame.py \
        soundrts/clientgamegridview.py \
        soundrts/clientgamehud.py \
        soundrts/lib/mouse.py \
        soundrts/tests/unittests/test_ui_sighted_02.py \
        soundrts/tests/unittests/test_ui_sighted_03.py \
        CHANGELOG.md \
        doc_admin/todo.md \
        doc_admin/report_sighted_ux_01.md \
        doc_admin/REPORT-REV-SIGHTED-03.md \
        doc_admin/REPORT-FINALE-SIGHTED-03.md

git commit -m "feat(ui-sighted-03): SI-08 dynamic hotkeys + SI-09 owner-tinted badges + SI-10 sizeall drag cursor

SI-08 (DEBITO-02): KEYS panel ora alimentato da res/ui/bindings.txt con
cache lazy. _KEYS_HOTKEYS esteso a 4-tuple, 8 azioni reali SoundRTS,
8 chiavi L10N EN+IT, pannello allargato 240->280 px.

SI-09 (DEBITO-02): badge stack differenziato per owner (verde own / rosso
enemy / grigio ally). display_objects refactor: bucket per cella e
categoria, O(N) invariato. _draw_stack_badge esteso con parametri color
opzionali retrocompatibili.

SI-10 (DEBITO-02): cursore sizeall registrato in lib/mouse.py,
GameInterface._apply_rubber_band_cursor(pos) iniettato in MOUSEMOTION
handler con getattr difensivo. Priorita su attack (SI-07). Guardia
display_is_active.

Tests: +15 nuovi (test_ui_sighted_03.py), test_ui_sighted_02.py
adattato al nuovo 4-tuple (LEGGE-7).

Suite: 515 passed, 1 skipped (baseline 500/1, +15, 0 regressioni)."
```

**Eseguire manualmente nel terminale quando pronto.** Poi:

```bash
git push origin master   # opzionale; richiede conferma esplicita PUSH
```

---

## Aperture per UI-SIGHTED-04

- GAP-05 minimap radar (radar panel basso-destra o overlay toggleabile).
- GAP-08-ext indicatore di range (visibility/attack/sight) come overlay circolare on-hover su unità propria.
- KEYS panel: live-refresh quando l'utente modifica `bindings.txt` durante una sessione (al momento cache infinita).
- Cursore `sizeall`: migrazione a `pygame.SYSTEM_CURSOR_SIZEALL` quando il min-pygame supporto sarà garantito.
- Badge stack alleato (grigio): valutare se aggregare alleati e nemici sotto un unico badge "non-own".
- L10N: tradurre 8 nuove chiavi `hotkey_*` in FR, PT-BR, DE, ES, RU, PL, SK, VI, ZH, BE, CS.

---

**Round UI-SIGHTED-03 chiuso.** DEBITO-02 risolto interamente.
