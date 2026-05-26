# Round 10 — Residuo Suite + Audit Visual UI

Data: 2026-05-25
Stato: COMPLETATO

---

## Baseline ingresso

| Metrica | Valore |
|---------|--------|
| Suite ingresso (R9 finale) | 238 passed / 3 failed / 2 errors |
| Log ingresso | `suite_r10_pre.log` |

---

## Obiettivo A — Eliminazione residuo suite

### Classificazione

| Categoria | Descrizione | Conteggio |
|-----------|-------------|-----------|
| CAT-1 | Errori reali, logica sbagliata | 0 |
| CAT-2 | ResourceWarning / deprecazioni | 3 (=5 test affetti) |
| CAT-3 | Fixture di test mancanti | 2 |
| CAT-4 | Residuo irreducibile | 0 |

### Problemi e soluzioni

#### P1 — ResourceWarning in test_autorepair.py (2 ERRORS)

**Causa**: `ExceptionGroup` di `ResourceWarning` (file handle non chiusi) sollevato
come errore da `filterwarnings = error` in `pytest.ini`.
File coinvolti:
- `soundrts/servermain.py`: `WHATISMYIP_URL = open(...).read().strip()`
- `soundrts/metaserver.py`: `MAIN_METASERVER_URL = open(...).read().strip()`
- `soundrts/metaserver.py`: `_default_servers()`: `lines = open(...).readlines()`
- `soundrts/campaign.py`: 4 `open()` bare in `CutSceneChapter._load()`,
  `Campaign._set_title_and_mods()`, `Campaign._set_mods_from_mods_txt()`,
  `Campaign._set_chapters()`
- `soundrts/mapfile.py`: `_load_from_package()`: stream non chiuso
- `soundrts/lib/package.py`: `PackageStack.mod()`: `open_text` non chiuso

**Soluzione**: sostituito ogni `open().read()` / `open().readlines()` con
`with open(...) as _f: ...` pattern.

#### P2 — test_config.py::test_load_defaults_if_file_with_errors (FAILED)

**Causa**: 4 `open()` bare nel codice test stesso.
**Soluzione**: context manager applicati nelle righe 57-63 di `test_config.py`.

#### P3 — test_package.py::test_subpackage_dirnames (FAILED)

**Causa**: `FolderPackage.dirnames()` scansiona cartelle reali. `res2/mods/` aveva
solo `mod1/` come directory reale, mentre il test si aspettava anche `mod2/` e
`sound1/` (presenti in `res2.zip` ma non nel filesystem).
**Soluzione**: creati `res2/mods/mod2/.gitkeep` e `res2/mods/sound1/.gitkeep`.

#### P4 — test_resource.py::test_update (FAILED)

**Causa radice**: stessa causa di P3 (mancanza delle cartelle fixture).
**Soluzione**: stessa di P3.

### Suite post-A

| Metrica | Valore |
|---------|--------|
| Suite post-A | **243 passed / 0 failed / 0 errors** |
| Log post-A | `suite_r10_postA.log` |

---

## Obiettivo B — Audit sistema Visual UI (Round 8+9)

### Scope file auditati

- `soundrts/clientvisualui.py`
- `soundrts/clientmenuscreen.py`
- `soundrts/clientmenu.py`
- `soundrts/clientmedia.py`
- `soundrts/clientmain.py`
- `soundrts/lib/screen.py`
- `soundrts/config.py`
- `soundrts/msgparts.py`
- `soundrts/tests/unittests/test_visual_ui.py`

### Checklist B1 (9 punti)

| Punto | Descrizione | Esito |
|-------|-------------|-------|
| B1.1 | Guard completezza: tutti i metodi visual output hanno `if not config.visual_mode: return` | PASS |
| B1.2 | Stack integrità: push in `run()`, pop nel `finally`, nessun leak | PASS (nota: `_render_current()` chiamata direttamente da clientmenu — accettabile) |
| B1.3 | Cleanup completezza: `cleanup()` prima di SystemExit (clientmain lines 286, 307) | PASS |
| B1.4 | Mouse robustezza: MOUSEBUTTONDOWN filtra `button == 1` | FAIL → **CORRETTO** |
| B1.5 | Persistenza config: `toggle_visual_mode()` chiama `config.save()` | PASS |
| B1.6 | Screen resize: VIDEORESIZE non gestito | BASSA — rimandato Round 11 |
| B1.7 | Font fallback: `_safe_font()` ritorna None su errore; render lo controlla | PASS |
| B1.8 | Thread safety: nessun threading nel contesto menu | PASS (N/A) |
| B1.9 | Msgparts alias: `VISUAL_MODE_ON = DISPLAY_ON = [4206]`, `VISUAL_MODE_OFF = DISPLAY_OFF = [4207]` | PASS |

### Revisioni applicate (B3)

| Fix | Gravità | File | Descrizione |
|-----|---------|------|-------------|
| button==1 filter | MEDIA | `clientmenu.py:~323` | `elif e.type == MOUSEBUTTONDOWN:` → `and e.button == 1` |
| open() remember read | BASSA | `clientmenu.py:~140` | Bare `open()` → `with open() as _f:` |
| open() remember write | BASSA | `clientmenu.py:~298` | Bare `open()` → `with open() as _f:` |

### Test aggiunti (B2)

- `test_mouse_button_right_click_ignored` in `test_visual_ui.py`
  - Verifica: button=2 e button=4 NON confermano; button=1 conferma
  - Dipendenze: `visual_on` fixture, monkeypatch `_confirm_choice` e `get_screen_manager`

### Suite post-B

| Metrica | Valore |
|---------|--------|
| Suite post-B | **244 passed / 0 failed / 0 errors** |
| test_visual_ui.py | 12/12 |
| Log post-B | `suite_r10_postB.log` |

---

## Compliance LEGGI

| Legge | Verifica |
|-------|---------|
| LEGGE-0 READ-BEFORE-WRITE | Tutti i file letti prima della modifica |
| LEGGE-1 Audio invariant | Nessuna modifica a voice.*, psounds.*, sounds.* |
| LEGGE-2 Visual gate | Guard preservati in tutti i metodi visual output |
| LEGGE-3 Backward compat | `visual_mode` default 0 invariato |
| LEGGE-4 pytest.ini clean | Nessun nuovo filtro workaround aggiunto |
| LEGGE-5 Max 10 retries | Non raggiunto |
| LEGGE-6 Suite ≥ 238 | 244 > 238 ✓ |
| LEGGE-7 Release gate | Suite 0/0/0 ✓; bump versione rimandato a operatore umano |
| LEGGE-8 No git | Nessun comando git eseguito |

---

## File prodotti

| File | Tipo | Descrizione |
|------|------|-------------|
| `soundrts/servermain.py` | Modificato | Context manager A1 |
| `soundrts/metaserver.py` | Modificato | Context manager A1 |
| `soundrts/campaign.py` | Modificato | Context manager A1 (×4) |
| `soundrts/mapfile.py` | Modificato | Context manager A1 |
| `soundrts/lib/package.py` | Modificato | Context manager A1 |
| `soundrts/tests/test_config.py` | Modificato | Context manager in test A1 |
| `soundrts/tests/res2/mods/mod2/.gitkeep` | Creato | Fixture A2 |
| `soundrts/tests/res2/mods/sound1/.gitkeep` | Creato | Fixture A2 |
| `soundrts/clientmenu.py` | Modificato | button filter B3 + open() B3 |
| `soundrts/tests/unittests/test_visual_ui.py` | Modificato | Nuovo test B2 |
| `doc_admin/round10_residuo_plan.md` | Creato | Questo file |
| `doc_admin/todo.md` | Modificato | Sezione Round 10 aggiunta |
| `CHANGELOG.md` | Modificato | Voci Fixed+Changed Round 10 |
