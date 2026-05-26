# Round 15 — Rapporto Sprite per Operatore

**Data:** 25 maggio 2026
**Destinatario:** operatore (creazione sprite manuale)
**Output atteso:** cartella `res/img/` (sottocartella di `res/`)
**Formato master:** PNG con canale alpha
**Stile suggerito:** top-down medieval flat, palette coerente
**Tool consigliati:** Aseprite, Krita, Piskel, Inkscape

---

## 1. Convenzioni generali

- **Estensione:** `.png` obbligatorio (case-sensitive minuscolo).
- **Trasparenza:** canale alpha (PNG RGBA). Sfondo trasparente.
- **Master size:**
  - Unità: **32×32 px** (verranno scalate a 8–16 px runtime).
  - Edifici e terreni: **64×64 px** (verranno scalati a 8–135 px).
  - Risorse: **32×32 px** (centrate nella tile).
  - UI opzionali: **64×64 px**.
- **Nome file:** identico al `type_name` di `res/ui/style.txt`,
  minuscolo, senza spazi. Esempio: `peasant.png`, non `Peasant.PNG`.
- **Eccezione terreni auto-applicati:** strippare l'underscore iniziale.
  - `_meadows` → `meadows.png`
  - `_forest` → `forest.png`
  - `_dense_forest` → `dense_forest.png`
- **Orientamento:** top-down (vista dall'alto). Le unità non hanno
  varianti di direzione in R16 (sprite singolo statico).
- **Colore di fazione:** NON dipingerlo nello sprite. L'anello di
  fazione viene già renderizzato dal motore sopra lo sprite.

---

## 2. Struttura cartelle attesa

```
res/img/
├── units/        ← 18 file
├── buildings/    ← 22 file
├── resources/    ← 2  file
├── terrain/      ← 12 file
└── ui/           ← 5  file (opzionali)
```

Totale obbligatorio: **54 PNG**. Totale completo con UI: **59 PNG**.

---

## 3. UNITÀ (`res/img/units/`, 32×32 px)

Priorità ALTA: gameplay core, sempre visibili sul campo.

| Filename | Descrizione visiva | Note |
|----------|--------------------|------|
| `peasant.png` | Contadino con cappuccio marrone, attrezzo (martello/falce) in mano. | Lavoratore base. |
| `footman.png` | Soldato con spada e scudo, armatura grigio-acciaio. | Fante melee. |
| `zombie.png` | Soldato in armatura strappata, pelle verde-marrone. | Variante non-morta di footman. |
| `archer.png` | Arciere con cappuccio verde, arco in mano. | Tiratore base. |
| `darkarcher.png` | Arciere con mantello nero, arco scuro. | Variante "dark" di archer. |
| `skeleton.png` | Scheletro con arco, ossa bianche. | Arciere non-morto. |
| `knight.png` | Cavaliere a cavallo, armatura lucida, lancia. | Unità veloce élite. |
| `catapult.png` | Catapulta di legno con braccio sollevato. | Macchina d'assedio. |
| `dragon.png` | Drago rosso/verde con ali aperte vista dall'alto. | Volante d'élite. |
| `mage.png` | Mago con tunica blu, cappello a punta, bastone. | Caster arcano. |
| `priest.png` | Sacerdote in tunica bianca, croce/simbolo dorato. | Caster guarigione. |
| `necromancer.png` | Negromante in tunica viola scuro, teschio in mano. | Caster non-morti. |
| `new_flyingmachine.png` | Macchina volante con eliche/ali tipo dirigibile. | Aerea moderna. |
| `flyingmachine.png` | Macchina volante tipo elicottero rudimentale. | Aerea legacy. |
| `boat.png` | Barca a vela piccola. | Trasporto navale. |
| `destroyer.png` | Nave a vela media con cannoni laterali. | Nave militare. |
| `battleship.png` | Galeone pesante con multi-ponti. | Nave da guerra. |
| `submarine.png` | Sommergibile metallico vista periscopio. | Unità acquatica nascosta. |

**Subtotale:** 18 file.

---

## 4. STRUTTURE (`res/img/buildings/`, 64×64 px)

Priorità ALTA: definiscono visivamente le basi del giocatore.

| Filename | Descrizione visiva | Note |
|----------|--------------------|------|
| `buildingsite.png` | Impalcatura di legno con assi e attrezzi. | Cantiere in costruzione. |
| `farm.png` | Casetta agricola con tetto di paglia e campo. | Produzione food. |
| `lumbermill.png` | Capanno con segheria e tronchi accatastati. | Raccolta legno. |
| `barracks.png` | Edificio rettangolare in pietra con bandiera. | Addestra footman/archer. |
| `townhall.png` | Edificio centrale con tetto rosso e camino. | Tier-1. |
| `keep.png` | Mastio in pietra grigia, una torre. | Tier-2, evoluzione townhall. |
| `castle.png` | Castello con 4 torri e merlature. | Tier-3, evoluzione keep. |
| `blacksmith.png` | Fucina con enclume, fumo dal camino. | Upgrade armi/armature. |
| `stables.png` | Stalla in legno con cavalli visibili. | Addestra knight. |
| `workshop.png` | Capannone di legno con ingranaggi/ruote. | Costruisce catapult. |
| `dragonslair.png` | Caverna scura con uovo di drago/fiamme. | Addestra dragon. |
| `magestower.png` | Torre alta blu/viola con cristallo magico. | Addestra mage. |
| `temple.png` | Tempio bianco con croce/simbolo divino. | Addestra priest. |
| `necropolis.png` | Edificio gotico nero con teschi/ossa. | Addestra unità non-morte. |
| `scouttower.png` | Torre di guardia in legno, alta e stretta. | Visione. |
| `guardtower.png` | Torre in pietra con feritoie per arcieri. | Difesa archer. |
| `cannontower.png` | Torre con cannone metallico in cima. | Difesa cannone. |
| `wall.png` | Sezione di muro in pietra grigia. | Muro semplice. |
| `massive_wall.png` | Muro più spesso, pietra scura/nera. | Muro pesante. |
| `gate.png` | Cancello in legno con cornice in pietra. | Cancello. |
| `massive_gate.png` | Cancello rinforzato in ferro. | Cancello pesante. |
| `shipyard.png` | Molo con scafo in costruzione. | Costruisce navi. |

**Subtotale:** 22 file.

---

## 5. RISORSE (`res/img/resources/`, 32×32 px)

Priorità ALTA: visibili in ogni mappa.

| Filename | Descrizione visiva | Note |
|----------|--------------------|------|
| `goldmine.png` | Ingresso miniera con pepite d'oro/luccichio giallo. | Risorsa oro. |
| `wood.png` | Cluster di 3 alberi verdi vista dall'alto. | Bosco raccoglibile. |

**Subtotale:** 2 file.

---

## 6. TERRENI (`res/img/terrain/`, 64×64 px, tileable)

Priorità ALTA: coprono l'intera mappa, tile-friendly (i bordi devono
combaciare se ripetuti).

| Filename | Descrizione visiva | Note |
|----------|--------------------|------|
| `meadows.png` | Prato verde brillante con ciuffi d'erba sparsi. | Auto-applicato. Mappato da `_meadows`. |
| `forest.png` | Verde scuro con alcuni alberi sparsi. | Auto-applicato. Mappato da `_forest`. |
| `dense_forest.png` | Verde molto scuro, fitto di alberi. | Auto-applicato. Mappato da `_dense_forest`. |
| `river.png` | Acqua azzurra con correnti lineari. | Fiume passabile in punti. |
| `lake.png` | Acqua azzurro-blu, increspature concentriche. | Lago. |
| `sea.png` | Acqua blu medio con onde. | Mare. |
| `ocean.png` | Blu profondo, onde marcate. | Oceano (più scuro di sea). |
| `mountain.png` | Roccia grigia con picco bianco/neve. | Impassabile. |
| `mountain_pass.png` | Sentiero stretto tra rocce grigie. | Passo. |
| `big_bridge.png` | Grande ponte in pietra su acqua. | Attraversamento maggiore. |
| `ford.png` | Acqua bassa con pietre affioranti. | Guado. |
| `marsh.png` | Verde-marrone fangoso con pozze. | Palude. |

**Subtotale:** 12 file.

**Nota tileability:** terreni "naturali" (meadows, forest, dense_forest,
sea, ocean, marsh) devono essere ripetibili senza giunture visibili
(seamless). I "feature" (river, big_bridge, mountain_pass, ford)
possono avere un disegno centrato non tileable.

---

## 7. UI OPZIONALI (`res/img/ui/`, 64×64 px) — PRIORITÀ BASSA

Non richiesti per R16. Possono migliorare il feedback visivo nei round
successivi.

| Filename | Descrizione visiva | Note |
|----------|--------------------|------|
| `selection_ring.png` | Anello verde brillante con alpha. | Sostituisce cerchio selezione. |
| `hp_bar_full.png` | Barra HP verde piena. | Stato HP > 66%. |
| `hp_bar_mid.png` | Barra HP gialla a metà. | Stato HP 33–66%. |
| `hp_bar_low.png` | Barra HP rossa quasi vuota. | Stato HP < 33%. |
| `attack_flash.png` | Sprite circolare grigio semitrasparente. | Sostituisce flash attacco PR-5. |

**Subtotale opzionale:** 5 file.

---

## 8. Statistiche complessive

| Categoria | File obbligatori | Priorità |
|-----------|------------------|----------|
| Unità | 18 | ALTA |
| Strutture | 22 | ALTA |
| Risorse | 2 | ALTA |
| Terreni | 12 | ALTA |
| UI opzionali | 5 | BASSA |
| **TOTALE OBBLIGATORIO** | **54** | — |
| **TOTALE CON UI** | **59** | — |

---

## 9. Priorità di lavorazione consigliata

### Gruppo 1 — MVP gameplay base (priorità ALTA-1, ~12 sprite)

Permette di giocare una partita minimal vedibile:

- `peasant.png`, `footman.png`, `archer.png`, `knight.png` (4 unità core)
- `townhall.png`, `farm.png`, `barracks.png`, `lumbermill.png` (4 edifici core)
- `goldmine.png`, `wood.png` (risorse)
- `meadows.png`, `forest.png` (terreni base)

### Gruppo 2 — Completamento gameplay (ALTA-2, ~25 sprite)

Tutti gli altri edifici, unità avanzate (mage, priest, dragon),
terreni rimanenti.

### Gruppo 3 — Variant e factions speciali (ALTA-3, ~17 sprite)

Necromancer, zombie, skeleton, darkarcher, submarine, flyingmachine,
muri/cancelli, ecc.

### Gruppo 4 — UI polish (BASSA, 5 sprite)

selection_ring, hp_bar_*, attack_flash.

---

## 10. Cosa succede se uno sprite manca

La `SpriteCache` in R16 gestisce il fallback automaticamente:

- Sprite presente → blit dell'immagine PNG.
- Sprite mancante o corrotto → fallback alla primitiva geometrica
  attuale (cerchio colorato per unità, rettangolo per edifici/terreni).

Quindi puoi creare sprite **in modo incrementale** seguendo le priorità
del paragrafo 9. Il gioco resta giocabile in ogni momento.

---

## 11. Posizione di consegna

Crea la cartella `res/img/` (dentro `res/` del workspace):

```
c:\Users\nemex\OneDrive\Documenti\GitHub\soundrts\res\img\
```

NON committare file binari grossi: prima di pushare, valutare git LFS o
escludere `res/img/` da `.gitignore` (decisione operatore).
