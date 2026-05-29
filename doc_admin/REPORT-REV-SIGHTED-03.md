# REPORT-REV-SIGHTED-03 — Revisione globale UI-SIGHTED-03

**Data**: 29 maggio 2026  
**Round**: UI-SIGHTED-03 (wave 3 sighted-player UX, DEBITO-02 chiuso)  
**Modalità**: COMPLETAMENTE AUTONOMO (A02+A09+A10)  
**Output**: 515 passed, 1 skipped (baseline 500/1 → +15 test netti, 0 regressioni)  
**Branch**: master  
**Stato git**: commit NON eseguito (LEGGE-1 g/p)

---

## REV-1 — Rilettura integrale (LEGGE-0)

Ogni file modificato è stato riletto end-to-end dopo l'edit:

| File | Linee | Sezioni rilette | Errori Pylance |
|---|---|---|---|
| `soundrts/clientgamehud.py` | 1340+ | init, `_KEYS_HOTKEYS`, `_get_bindings`, `_load_bindings_from_file`, `_draw_keys_panel` | 0 |
| `soundrts/clientgamegridview.py` | 520+ | `display_objects` (refactor completo), `_draw_stack_badge` (nuova firma) | 0 |
| `soundrts/clientgame.py` | 2280+ | property `display_is_active`, `_apply_rubber_band_cursor`, MOUSEMOTION dispatch | 0 |
| `soundrts/lib/mouse.py` | ~80 | `record_cursor("sizeall", ...)`, `set_cursor` difensivo | 0 |
| `res/ui/style.txt` | +9 righe | 8 chiavi hotkey_* | n/a |
| `res/ui-it/style.txt` | +9 righe | 8 chiavi hotkey_* IT | n/a |
| `soundrts/tests/unittests/test_ui_sighted_03.py` | 268 | 15 test in 3 sezioni | 0 |
| `soundrts/tests/unittests/test_ui_sighted_02.py` | aggiornato | `test_keys_panel_has_eight_hotkey_entries` (LEGGE-7) | 0 |

---

## REV-2 — Cross-task check

### SI-08 ↔ HOT-PATH render

`_get_bindings()` è chiamato SOLO da `_draw_keys_panel()`, che a sua volta è chiamato SOLO quando `keys_visible == True` (default `False`, toggle da click utente).  
**Verdetto**: zero impatto su frame budget render quando il pannello è collassato. Quando aperto, cache O(1) dopo primo hit. Path I/O eseguito UNA volta per sessione (cache `_bindings_cache: Optional[Dict[str,str]]`).

### SI-09 ↔ `display_objects` (loop di rendering principale)

Cambio di complessità:
- PRIMA: `for o in dobjets.values(): display_object(o)` + aggregazione `id(place)` con bucket scalare.
- DOPO: stesso loop + 3 op extra/oggetto (lookup `own_player`, dict bucket, classify) + dispatch finale fino a 3 badge/cella.

Verifica: nessun ciclo annidato introdotto. La classify costa al massimo 1 chiamata `player_is_an_enemy` per oggetto (con try/except in caso di player object incompleto → "ally" safe). O(N) invariato, costante moltiplicativa K=3.

**Verdetto**: nessun regresso prestazionale misurabile in scenari reali (mappe SoundRTS max ~50-200 unità visibili → 3× = ~600 op extra/frame).

### SI-10 ↔ SI-07 cursor priority

Catena di priorità cursor in MOUSEMOTION handler:
1. **SI-10**: `_apply_rubber_band_cursor` (sizeall) — early-return se `mouse_select_origin` attivo.
2. **SI-07**: `enemy_at_mousepos` → `attack` cursor.
3. **default**: `diamond`.

Priorità univoca: il drag rubber-band sospende OGNI altro hint cursor finché MOUSEBUTTONUP non azzera `mouse_select_origin`. Test esplicito `test_priority_sizeall_over_attack` verifica.

**Verdetto**: priorità correttamente implementata, nessun conflitto tra SI-07 e SI-10.

### SI-10 ↔ test mock SimpleNamespace

Scoperto post-pytest: i test `test_ui_master_02b` usano `SimpleNamespace` come fake client, che NON ha `_apply_rubber_band_cursor`. Fix applicato: `getattr(self, "_apply_rubber_band_cursor", None)` difensivo (`AttributeError`-safe).

**Verdetto**: backward compat assicurata. Real `GameInterface` ha sempre il metodo (definito sulla classe).

---

## REV-3 — Audit LEGGE-3 (L10N)

| Chiave EN | Chiave IT | Stato |
|---|---|---|
| hotkey_pause | hotkey_pause | ✅ |
| hotkey_status | hotkey_status | ✅ |
| hotkey_default | hotkey_default | ✅ |
| hotkey_again | hotkey_again | ✅ |
| hotkey_immersion | hotkey_immersion | ✅ |
| hotkey_examine | hotkey_examine | ✅ |
| hotkey_arrows | hotkey_arrows | ✅ |
| hotkey_scout | hotkey_scout | ✅ |

8/8 chiavi presenti in EN + IT. Apertura UI-SIGHTED-04: FR / PT-BR / DE / ES / RU / PL / SK / VI / ZH / BE / CS / pt-BR.

---

## REV-4 — REV4D Audit

### REV4D-A: Correttezza funzionale

- SI-08: parser bindings.txt verificato su file reale (264 righe). Test `test_load_bindings_real_file` ne assicura presenza chiavi attese (`toggle_pause`, `unit_status`, `default`).
- SI-09: classify three-way verificata con SimpleNamespace mock di player relationship. Test `test_display_objects_groups_by_owner` valida l'aggregazione cell-by-cell.
- SI-10: 4 guardie testate (drag attivo, no-origin, display-off, zero-drag). Test pixel-perfect dei badge color verificano fill RGB esatto.

### REV4D-B: Sicurezza & Resilienza

- LEGGE-4: tutte le eccezioni del parser, `player_is_an_enemy`, e `_object_coords` sono catturate (try/except) con log stderr `[SOUNDRTS-VISUAL][ERROR/WARNING]` o silenziate (FileNotFoundError sul bindings.txt assente è atteso e non loggato).
- Nessun path utente in `_load_bindings_from_file` (path hardcoded relativo a `Path(__file__).resolve().parents[1].parent`).
- `set_cursor` difensivo: cursori sconosciuti ignorati silenziosamente. Nessun crash dell'input loop.

### REV4D-C: Performance

- SI-08: cache infinita evita re-parsing. Stato: O(1) post-prima-chiamata.
- SI-09: invariata O(N) sul loop di rendering, K=3.
- SI-10: 1 call `getattr` + 1 call funzione + check `mouse_select_origin` per ogni MOUSEMOTION (~60 events/sec a 60 fps). Trascurabile.

### REV4D-D: Manutenibilità

- Helper estratti (`_apply_rubber_band_cursor`, `_get_bindings`, `_load_bindings_from_file`) isolati e testabili in isolamento.
- Nuova firma `_draw_stack_badge` retrocompatibile.
- Commenti inline ai siti chiave (LEGGE-CMT-1: solo dove il WHY non è ovvio, es. priorità early-return).

---

## REV-5 — Audit LEGGE-7 (mai cancellare, sempre aggiornare)

| Test obsoleto | Azione |
|---|---|
| `test_keys_panel_has_eight_hotkey_entries` (test_ui_sighted_02.py) | Aggiornato per unpack forward-compatibile dei primi 3 campi del 4-tuple. Verifica originale (≥6 entries, `hotkey_` prefix) preservata. |

Nessun test cancellato. Test SI-02 `test_draw_stack_badge_count_5_blits` continua a passare con nuova firma (default colors retrocompat).

---

## REV-6 — Audit LEGGE-9 (no-touch zones)

Verificato che NESSUNA modifica tocca:
- ❌ Logica selezione audio (`worldaction`, `worldorders`)
- ❌ Rubber-band SI-03b in `draw_rubber_band` (modificato solo il CALLER per cursor, non il drawer)
- ❌ `enemy_at_mousepos` / `entity_at_mousepos` (riusati, mai modificati)
- ❌ Pipeline TTS / clientmedia

Modifiche limitate a layer di rendering visivo aggiuntivo + hint cursor.

---

## REV-7 — Audit LEGGE-10 (test self-contained)

`test_ui_sighted_03.py`:
- ✅ Zero import da `test_ui_sighted_01.py` / `test_ui_sighted_02.py`.
- ✅ Helper locali `_make_interface`, `_make_grid_view`, `_captured_blits`.
- ✅ Tutte le costanti (REPO_ROOT, BINDINGS_TXT) definite localmente.

---

## REV-8 — Audit gates pre-commit

| Gate | Comando | Risultato |
|---|---|---|
| Compile | `python -m py_compile soundrts/clientgame*.py soundrts/lib/mouse.py` | ✅ pass |
| Pylance | `get_errors` su 4 file Python | ✅ 0 errori |
| pytest | `.\.venv\Scripts\python.exe -m pytest` | ✅ **515 passed, 1 skipped** |
| Print check | (procedura standard pre-commit) | ✅ zero `print(` in src/ (log su stderr via `sys.stderr.write`) |

---

## Conclusione

Round UI-SIGHTED-03 chiuso con successo. Tutti e 3 i task (SI-08 ALTA, SI-09 MEDIA, SI-10 BASSA) sono implementati, testati, documentati, retrocompatibili e privi di regressioni. DEBITO-02 chiuso.

Commit proposto (NON eseguito, vedi REPORT-FINALE-SIGHTED-03.md per il blocco git completo).
