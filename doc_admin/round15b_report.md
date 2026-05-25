# Round 15-B — Sprite Pipeline (res/img/ + tooling)

Data: 25 maggio 2026
Branch: master
Esito globale: COMPLETATO

---

## 1. Riepilogo Esecutivo

Round 15-B ha portato a termine due obiettivi:

1. **Correzione documentale**: i due documenti R15
   (`doc_admin/round15_sprite_plan.md`,
   `doc_admin/round15_sprite_report.md`) usavano `img/` come root degli
   asset grafici, incoerente con la convenzione resource del progetto.
   Sostituito ovunque con `res/img/`, incluso lo snippet di codice
   `_IMG_ROOT = Path(BASE_DIR) / "res" / "img"`.

2. **Popolamento `res/img/`**: creata la struttura a 5 sottocartelle e
   popolata con 54 PNG RGBA obbligatori (32x32 per
   `units`/`resources`, 64x64 per `buildings`/`terrain`). 40 file
   derivano dal pack Kenney Medieval RTS (`PNG/Retina/`) tramite il
   tool `tools/normalize_sprites.py` (Pillow, LANCZOS resampling); i
   restanti 14 sono placeholder RGBA completamente trasparenti per
   entità senza controparte semantica nel pack (zombie, skeleton,
   catapult, dragon, flyingmachine x2, naval x4, goldmine,
   dragonslair, shipyard, buildingsite).

La pipeline è pronta per essere consumata dalla `SpriteCache` di
Round 16. La suite test non regredisce: 301 passed / 1 skipped /
0 failed (era 292 + 9 nuovi test sprite tools).

---

## 2. Mapping Finale

Riepilogo per categoria. Dettaglio completo in
`tools/sprite_mapping.csv`.

| Categoria | OK | PLACEHOLDER | Totale |
|-----------|----|----|---|
| units | 8 | 10 | 18 |
| buildings | 19 | 3 | 22 |
| resources | 1 | 1 | 2 |
| terrain | 12 | 0 | 12 |
| **TOTALE** | **40** | **14** | **54** |

Estratto tabellare (prime righe; tabella completa nel CSV):

| type_name | categoria | sorgente Kenney | size finale | livello | status |
|-----------|-----------|-----------------|-------------|---------|--------|
| peasant | units | medievalUnit_01.png | 32x32 | MEDIO | OK |
| footman | units | medievalUnit_02.png | 32x32 | MEDIO | OK |
| zombie | units | (nessuno) | 32x32 | NO_MATCH | PLACEHOLDER |
| townhall | buildings | medievalStructure_02.png | 64x64 | MEDIO | OK |
| shipyard | buildings | (nessuno) | 64x64 | NO_MATCH | PLACEHOLDER |
| wood | resources | medievalEnvironment_12.png | 32x32 | MEDIO | OK |
| goldmine | resources | (nessuno) | 32x32 | NO_MATCH | PLACEHOLDER |
| meadows | terrain | medievalTile_03.png | 64x64 | MEDIO | OK |
| ... | ... | ... | ... | ... | ... |

Tutti i 40 MATCH sono di livello **MEDIO**: l'assegnazione è stata
fatta per indice numerico del file Kenney + dimensioni del bounding
box dichiarate nel `medievalRTS_spritesheet.xml`, **senza** ispezione
visiva sprite-per-sprite. Ogni riga del CSV riporta una nota
esplicativa che documenta il criterio usato.

---

## 3. Statistiche Sprite

- TOTALE_TARGET: 54
- PRESENTI: 54 (di cui 40 OK + 14 PLACEHOLDER)
- MANCANTI: 0
- ERRORI_FORMATO: 0
- STATO_GENERALE: OK

Modo RGBA: 54/54 (100%). Dimensioni esatte: 54/54 (100%).
Tutti i file sono leggibili da Pillow (validato in
`tools/sprite_validation_report.txt`).

Spazio disco occupato da `res/img/`: trascurabile (PNG ottimizzati
Pillow, target 32x32 e 64x64).

---

## 4. Decisioni Autonome

| ID | Decisione | Motivazione |
|----|-----------|-------------|
| D1 | Installare Pillow nel `.venv` ma NON aggiungerla a `requirements.txt`. | Pillow è tooling dev-only per la pipeline sprite. Il runtime (pygame) non la richiede. Aggiungerla a requirements aumenterebbe la superficie di dipendenze del prodotto senza beneficio. |
| D2 | Non committare automaticamente i 54 PNG binari (no `git add res/img/`). | LFS / `.gitignore` su asset binari è scelta strutturale dell'operatore. La policy Round 15-B vieta esplicitamente git add su binari. |
| D3 | Usare `PNG/Retina/` del pack Kenney come sorgente (non `Default size` né lo spritesheet). | I file Retina sono i più dettagliati (~2x) e già divisi per categoria (Unit/Structure/Environment/Tile). Downscale LANCZOS produce qualità migliore di upscale da Default. |
| D4 | Assegnare MATCH_MEDIO ai 40 sprite mappati anziché ALTO. | Le assegnazioni sono state fatte per indice e dimensione dal XML, senza ispezione visiva file-per-file. ALTO sarebbe stato fuorviante. Operatore avvisato in CSV + report e TODO Round 17+. |
| D5 | Placeholder RGBA totalmente trasparente (alpha=0) per i NO_MATCH. | Garantisce dimensioni e mode corretti per la `SpriteCache` senza imporre artwork errato. Il render mostrerà semplicemente il fallback geometrico esistente. |
| D6 | Generare l'output con dimensione quadrata uniforme per categoria (32 o 64) anche per sorgenti non quadrate. | Semplifica la `SpriteCache` (un solo `transform.scale` per categoria) e si allinea al contratto del piano R15. |

---

## 5. Problemi Aperti

- **OP-1 (MEDIA)**: tutti i 40 sprite con stato OK sono MATCH_MEDIO
  per indice; nessuna verifica visiva. È molto probabile che alcune
  associazioni siano errate (es. team rosso/blu invertito,
  building errato). Mitigazione: il CSV è esaustivo, il rerun del
  tool è istantaneo dopo aver aggiornato la `MAPPING` in
  `tools/normalize_sprites.py`.
- **OP-2 (BASSA)**: 14 entità SoundRTS non hanno alcun corrispettivo
  nel pack Kenney Medieval RTS base (undead, dragon, naval,
  flyingmachine, goldmine, dragonslair, shipyard, buildingsite). Per
  rimuovere i placeholder serve un pack aggiuntivo o asset custom.
- **OP-3 (BASSA)**: il pack Kenney include anche un foglio
  `Spritesheet/medievalRTS_spritesheet@2.png` con coordinate per uno
  spritesheet unico; la pipeline corrente NON lo usa, preferendo i
  file PNG già divisi. Cambio fonte richiederebbe riscrittura del
  tool.
- **OP-4 (INFO)**: la commitabilità della cartella `res/img/`
  (volume binari + LFS) resta scelta operatore. Vedi anche
  D2 in §4.

---

## 6. Report Diagnostici

Nessuna fase ha raggiunto il limite di 10 tentativi di validazione.
Tutte le 7 fasi sono completate in primo tentativo o con un singolo
retry tecnico (terminale PowerShell stuck su here-string ereditato
da R15, sbloccato chiudendo il blocco con `'@`).

Eventi notevoli:

- E1: prereq Pillow assente nel venv → installato (`pip install
  Pillow` → PIL 12.2.0).
- E2: pytest invocato con `--tb=line` ha innescato il noto
  `_parse_options()` -> `SystemExit:2` da `soundrts/options.py`.
  Risolto eseguendo `pytest` senza extra args.

Nessun REPORT-DIAGNOSTICO-Fx generato.

---

## 7. Stato Suite

Baseline R15: 292 passed / 0 failed / 0 errors / 1 skipped.

Suite finale R15-B (`.venv\Scripts\python.exe -m pytest`):

- **301 passed**
- **1 skipped** (test_visual_resize, sospeso documentato R13)
- **0 failed**
- **0 errors**
- Durata: 6.52 s

Delta: +9 test (tutti i 9 di
`soundrts/tests/unittests/test_sprite_tools.py`). Nessuna
regressione su test pre-esistenti.

---

## 8. Radar Autovalutazione

Legenda: ✅ completato pienamente, 🔶 completato con riserva, ❌ non completato.

| Sezione | Esito | Note |
|---------|-------|------|
| Fase 0 — Prereq (Pillow, pack Kenney) | ✅ | Pillow installata; pack presente. |
| Fase 1 — Correzione doc R15 (img/ → res/img/) | ✅ | 13 occorrenze sostituite su 2 file; grep di verifica = 0. |
| Fase 2 — Catalogo Kenney + mapping 54 entità | 🔶 | Catalogo completo (XML 530 SubTexture), mapping prodotto ma di livello MEDIO senza ispezione visiva. |
| Fase 3 — Struttura `res/img/{units,buildings,resources,terrain,ui}/` | ✅ | 5 cartelle create. |
| Fase 4 — `tools/normalize_sprites.py` + 54 PNG + CSV | ✅ | 40 OK + 14 PLACEHOLDER. CSV `tools/sprite_mapping.csv` con 9 colonne. |
| Fase 5 — `tools/validate_sprites.py` + report TXT | ✅ | STATO_GENERALE: OK. Output NVDA-friendly. |
| Fase 6 — Revisione (no pygame in tooling, no git add binari) | ✅ | Tooling pure Pillow+stdlib; nessun commit binari. |
| Fase 7 — Test minimi + suite + CHANGELOG + TODO + report | ✅ | 9 nuovi test ok; suite 301/1/0; CHANGELOG `[Unreleased]` esteso; TODO aggiornato; questo report. |

Conformità Leggi operative: LEGGE-0 ✅, LEGGE-1 ✅ (zero tocchi a
voice/sound/world*/test esistenti), LEGGE-2 ✅, LEGGE-3 ✅,
LEGGE-4 ✅ (MATCH_MEDIO scelto su MATCH_ALTO per onestà),
LEGGE-5 ✅ (nessuna azione irreversibile).

---

## Allegati

- `tools/sprite_mapping.csv` — audit mapping completo
- `tools/sprite_validation_report.txt` — report validator
- `tools/normalize_sprites.py` — tool generazione
- `tools/validate_sprites.py` — tool QA
- `soundrts/tests/unittests/test_sprite_tools.py` — test contratto
- `res/img/{units,buildings,resources,terrain,ui}/` — 54 PNG RGBA
