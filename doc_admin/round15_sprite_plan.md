# Round 15 — Piano Tecnico Integrazione Grafica

**Data:** 25 maggio 2026
**Tipo round:** ANALISI + PIANIFICAZIONE (zero implementazione)
**Baseline tecnica:** 292 passed / 0 failed / 0 errors / 1 skipped
**Pygame:** 2.6.1 (SDL 2.28.4, Python 3.12.0) — supporto pieno per
`pygame.image.load`, `convert_alpha`, `pygame.transform.scale`.

---

## 1. ANALISI RENDERING ATTUALE

### 1.1 Architettura del ciclo display

Il rendering del gameplay è gestito da `GridView`
([soundrts/clientgamegridview.py](soundrts/clientgamegridview.py)).
`GridView.display()` viene invocato dal client in 6 punti di
`clientgame.py` (linee 783, 864, 998, 1757, 2090) sempre tramite
l'interfaccia `Interface`, che è attiva soltanto in modalità Visual UI
(`config.visual_mode = 1`). In modalità audio-only nessuna funzione
visuale viene chiamata: la LEGGE-1 (audio invariante) è garantita
dall'architettura attuale.

Pseudocodice del ciclo:

```
GridView.display():
    _update_coefs()             # ricalcola square_view_*, R, R2 (globali)
    _display()                  # bordi mappa + sfondi terrain + walls
    display_objects()           # per ogni o in dobjets: display_object(o)
    _display_active_zone_border()  # rettangolo zona attiva + osservatore
    if collision_debug:
        _collision_display()
```

### 1.2 Punti di rendering identificati (PR-1..PR-5)

| ID | Metodo | Primitiva attuale | Sostituzione sprite prevista |
|----|--------|-------------------|------------------------------|
| PR-1 | `_display()` blocco "backgrounds" | `draw_rect(square_color(sq), rect)` per ogni square osservato | `blit` di `terrain/{type_name}.png` scalato a `(square_view_width, square_view_height)`; fallback al `draw_rect` esistente |
| PR-2 | `display_object()` shape="square" | `draw_rect(o.corrected_color(), rect, width)` | `blit` di `buildings/{type_name}.png` scalato a `(R_vis*2, R_vis*2)`; fallback al `draw_rect` |
| PR-3 | `display_object()` shape="circle" | `pygame.draw.circle(...)` o `screen.set_at(...)` se non `collision` | `blit` di `units/{type_name}.png` o `resources/{type_name}.png` centrato in `(x, y)`, dimensione `R_vis*2`; fallback al `pygame.draw.circle` |
| PR-4 | `display_object()` faction indicator + HP bar | `pygame.draw.circle` (faction) + `pygame.draw.line` (HP) | **INVARIATO**. Disegnati sopra lo sprite per leggibilità. Vedi nota PR-4 sotto. |
| PR-5 | `display_attack()` flash | `pygame.draw.line` + `pygame.draw.circle` | Opzionale: `blit` di `ui/attack_flash.png` semitrasparente sulla posizione target; fallback al rendering attuale. **Priorità BASSA**. |

Nota PR-4: l'indicatore di fazione (cerchio interno verde/rosso/blu/grigio)
e la barra HP sono già primitive piccole e leggibili sopra lo sprite.
Sostituirli con sprite richiederebbe una palette di anelli colorati e
una progress-bar 2D. Decisione: lasciarli come primitive — il costo
tecnico è basso e il risultato visivo è già adeguato. Anelli di
selezione e barre HP custom restano come sprite **opzionali** in
`img/ui/` per round futuri.

### 1.3 Dimensioni tile a varie risoluzioni

Formula in `_update_coefs()`:

```
map_w = max(sw // 2, sw - hud_right_width)   # hud_right_width = 303
sq    = min(map_w // (xcmax + 1), sh // (ycmax + 1))
```

Per una mappa media 8×8 squares (xcmax=ycmax=7) il tile è circa:

| Risoluzione | map_w | tile px (sq) | R (raggio unità) | R_vis (R*2.0) |
|-------------|-------|--------------|------------------|---------------|
| 640×480 | 337 | 42 | ≥4 (R_MIN) | 8 |
| 800×600 | 497 | 62 | ≥4 | 8–10 |
| 1024×768 | 721 | 90 | ~5 | 10 |
| 1920×1080 | 1617 | 135 | ~8 | 16 |

Conclusione: **64×64 px** è la dimensione master ragionevole per gli
sprite di terreno e edifici. Per le unità è sufficiente **32×32 px**
master (verranno scalati a `R_vis*2` che spazia 8–16 px).
La `SpriteCache` scala via `pygame.transform.scale` alla dimensione
runtime calcolata.

### 1.4 Bug noto: `R` e `R2` globali a livello di modulo

`clientgamegridview.py` linee 168–177 (`global R, R2`) mutano due
variabili a livello di modulo. Effetti collaterali:
- `R` e `R2` non sono inizializzate prima della prima chiamata a
  `_update_coefs()` → `NameError` se `display_object` venisse chiamato
  prima.
- In presenza di più istanze di `GridView` (ipoteticamente) il valore
  sarebbe condiviso e racy.

Proposta: spostare `R`/`R2` come attributi di istanza (`self.R`,
`self.R2`) in un round dedicato. **Non in R16** per non mescolare
refactor con introduzione sprite. Tracciato come TODO Round 17+
(rischio attuale: BASSO — il codice funziona perché `_update_coefs()`
viene sempre chiamato come primo step di ogni metodo pubblico).

---

## 2. CATALOGO ENTITÀ DI GIOCO

Fonte: [res/ui/style.txt](res/ui/style.txt) (definitiva). Gerarchia
`is_a` analizzata. I tipi `def` di azioni (`go`, `attack`, ecc.) e
upgrade (`melee_weapon`, ecc.) sono **esclusi** dal catalogo sprite
perché non sono entità renderizzabili. Anche `thing`/`unit`/
`building`/`walking_unit`/`resource_deposit`/`buildingsite` sono **basi
astratte**: nessuno sprite dedicato.

### 2.1 UNITÀ MOBILI (shape circle)

| type_name | is_a | note gameplay |
|-----------|------|---------------|
| peasant | walking_unit | lavoratore base (gather, build, repair) |
| footman | walking_unit | fante melee base |
| zombie | footman | non-morto melee (necropolis) |
| archer | walking_unit | arciere base |
| darkarcher | archer | arciere oscuro (variante) |
| skeleton | archer | arciere non-morto |
| knight | unit | cavaliere veloce (stables) |
| catapult | unit | macchina d'assedio (workshop) |
| dragon | unit | volante d'élite (dragonslair) |
| mage | walking_unit | caster (magestower) |
| priest | walking_unit | caster di guarigione (temple) |
| necromancer | walking_unit | caster non-morti (necropolis) |
| new_flyingmachine | unit | macchina volante moderna |
| flyingmachine | new_flyingmachine | macchina volante (legacy) |
| boat | unit | trasporto navale |
| destroyer | unit | nave militare |
| battleship | unit | nave da guerra pesante |
| submarine | unit | sommergibile |

**Totale: 18 unità.**

### 2.2 STRUTTURE (shape square)

| type_name | is_a | note gameplay |
|-----------|------|---------------|
| buildingsite | building | cantiere in costruzione |
| farm | building | risorsa food |
| lumbermill | building | raccolta legno avanzata |
| barracks | building | addestra footman/archer |
| townhall | building | centro tier-1 |
| keep | townhall | tier-2 |
| castle | keep | tier-3 |
| blacksmith | building | upgrade armi/armature |
| stables | building | addestra knight |
| workshop | building | addestra catapult |
| dragonslair | building | addestra dragon |
| magestower | building | addestra mage |
| temple | building | addestra priest |
| necropolis | building | addestra zombie/skeleton/necromancer |
| scouttower | building | difesa visione |
| guardtower | building | difesa archer |
| cannontower | building | difesa cannone |
| wall | building | muro semplice |
| massive_wall | building | muro pesante |
| gate | building | cancello |
| massive_gate | building | cancello pesante |
| shipyard | building | costruisce navi |

**Totale: 22 strutture.**

### 2.3 RISORSE (shape circle, base resource_deposit)

| type_name | note gameplay |
|-----------|---------------|
| goldmine | risorsa oro |
| wood | bosco raccoglibile |

**Totale: 2 risorse.**

`meadow` e `corpse` sono `is_a thing` (non `resource_deposit`):
prati decorativi e cadaveri post-morte. Sprite opzionali, vedi 2.5.

### 2.4 TERRENI (cella mappa)

| type_name | note |
|-----------|------|
| _meadows | prato (auto-applicato) |
| _forest | bosco (auto-applicato) |
| _dense_forest | bosco denso (auto-applicato) |
| river | fiume |
| lake | lago |
| sea | mare |
| ocean | oceano |
| mountain | montagna impassabile |
| mountain_pass | passo montano |
| big_bridge | grande ponte |
| ford | guado |
| marsh | palude |

**Totale: 12 terreni.**

Note naming: i tre auto-applicati hanno underscore iniziale
(`_meadows`, `_forest`, `_dense_forest`). La `SpriteCache` in R16
risolverà il filename strippando l'underscore: `meadows.png`,
`forest.png`, `dense_forest.png`.

### 2.5 ELEMENTI MISCELLANEI (shape thing, decorativi)

| type_name | note |
|-----------|------|
| meadow | prato non-raccoglibile (decorativo) |
| corpse | cadavere dopo morte unità |
| path | sentiero (overlay) |
| bridge | ponte (overlay) |

Sprite di priorità BASSA: gameplay funziona senza.

### 2.6 ENTITÀ SPELL / EFFECT (esclusi)

`holy_vision`, `meteors`, `exorcism`: effetti spell. Non
renderizzati come unità statiche. Esclusi dal rapporto sprite.

### 2.7 Meccanismo di categorizzazione runtime

Domanda T4: come distinguere unità/strutture/risorse dal codice in
`display_object(o)` per scegliere la sottocartella corretta?

Analisi: l'oggetto `o` proviene da `interface.dobjets` ed espone:
- `o.type_name` — nome canonico (es. `"peasant"`, `"farm"`, `"goldmine"`).
- `o.shape()` — restituisce `"square"` (buildings) o `"circle"` (resto).
- `o.model.player` — `None` per terreni/risorse/decorativi, popolato
  per unità e strutture appartenenti a un player.

**Strategia proposta** (statica, costruita da `style.txt` a startup):

```python
# soundrts/clientsprites.py (R16, BOZZA)
_CATEGORY: dict[str, str] = {}

def _build_category_map():
    """Risolve type_name → 'units'|'buildings'|'resources'|'terrain'
    risalendo la catena is_a in style.txt."""
    UNIT_ROOTS = {"unit", "walking_unit"}
    BUILDING_ROOTS = {"building"}
    RESOURCE_ROOTS = {"resource_deposit"}
    TERRAIN = {"_meadows", "_forest", "_dense_forest",
               "river", "lake", "sea", "ocean", "mountain",
               "mountain_pass", "big_bridge", "ford", "marsh"}
    # itera ogni type_name in style.dict_index, segui is_a
    ...
```

In alternativa: lookup statico hardcoded delle 54 entità (dato che il
file `style.txt` è stabile). Decisione in R16 a seconda dell'API
effettiva di `definitions.style`.

---

## 3. ARCHITETTURA SPRITECACHE (TASK-4)

### 3.1 Bozza di classe (da implementare in R16)

```python
# soundrts/clientsprites.py — NUOVO MODULO IN R16
"""Cache di sprite PNG per la Visual UI.

Audio-only invariante: la cache è inizializzata in modo lazy.
La prima chiamata a get() carica il PNG; le successive
restituiscono la Surface scalata cached.
Se il PNG non esiste o non è caricabile → None (fallback geometrico).
"""

from __future__ import annotations
from pathlib import Path

import pygame

from .lib.log import warning
from .paths import BASE_DIR  # path della root progetto


_IMG_ROOT = Path(BASE_DIR) / "img"
_cache: dict[str, pygame.Surface | None] = {}


def get(category: str, name: str, size: int) -> pygame.Surface | None:
    """Restituisce lo sprite scalato a (size, size) px, o None.

    `category`  -> "units" | "buildings" | "resources" | "terrain" | "ui"
    `name`      -> filename senza estensione (es. "peasant")
    `size`      -> lato in px del Surface scalato
    """
    key = f"{category}/{name}@{size}"
    if key in _cache:
        return _cache[key]
    path = _IMG_ROOT / category / f"{name}.png"
    try:
        surf = pygame.image.load(str(path)).convert_alpha()
        scaled = pygame.transform.scale(surf, (size, size))
        _cache[key] = scaled
    except (FileNotFoundError, pygame.error, OSError) as exc:
        warning("SpriteCache miss for %s: %s", path, exc)
        _cache[key] = None
    return _cache[key]


def clear() -> None:
    """Invalida la cache (chiamare a cambio risoluzione)."""
    _cache.clear()


def category_of(o) -> str | None:
    """Risolve la categoria sprite di un oggetto di gameplay.
    Restituisce None per entità non renderizzabili come sprite."""
    # Implementazione in R16 — vedi sezione 2.7
    ...
```

### 3.2 Vincoli di compatibilità

- `pygame.image.load(...).convert_alpha()` richiede che il display sia
  già inizializzato (`pygame.display.set_mode`). Per i test headless
  → strategia mock in 3.4.
- `pygame.transform.scale` è disponibile in pygame 2.x. OK.
- `pygame.error` è già usata in `sound_cache.py` linea 139 → stesso
  pattern di error handling.

### 3.3 Integrazione nei punti PR-1..PR-5

```python
# In _display() — PR-1 (terrain)
sprite = clientsprites.get(
    "terrain", sq.type_name.lstrip("_"), self.square_view_width
)
if sprite is not None:
    get_screen().blit(sprite, (left, top))
else:
    draw_rect(color, rect)  # fallback corrente

# In display_object() — PR-2 (square = building)
category = clientsprites.category_of(o)  # "buildings"
sprite = clientsprites.get(category, o.type_name, R_vis * 2)
if sprite is not None:
    get_screen().blit(sprite, (x - R_vis, y - R_vis))
else:
    draw_rect(o.corrected_color(), rect, width)  # fallback corrente

# In display_object() — PR-3 (circle = unit/resource)
category = clientsprites.category_of(o)  # "units" | "resources"
sprite = clientsprites.get(category, o.type_name, R_vis * 2)
if sprite is not None:
    get_screen().blit(sprite, (x - R_vis, y - R_vis))
else:
    pygame.draw.circle(get_screen(), o.corrected_color(), (x, y), R_vis, width)
```

### 3.4 Strategia mock test (headless pytest)

I test esistenti girano in ambiente senza display (`pygame.display`
non inizializzato in pytest). La `SpriteCache` deve essere
**iniettabile/mockabile** per evitare crash:

```python
# In test:
import pygame
import soundrts.clientsprites as sc

def test_sprite_cache_miss_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_IMG_ROOT", tmp_path)
    assert sc.get("units", "nonexistent", 32) is None

def test_sprite_cache_hit(tmp_path, monkeypatch):
    pygame.init()
    pygame.display.set_mode((1, 1))   # display headless
    img = pygame.Surface((64, 64), pygame.SRCALPHA)
    img.fill((255, 0, 0, 255))
    (tmp_path / "units").mkdir()
    pygame.image.save(img, str(tmp_path / "units" / "u.png"))
    monkeypatch.setattr(sc, "_IMG_ROOT", tmp_path)
    sc.clear()
    surf = sc.get("units", "u", 32)
    assert surf is not None
    assert surf.get_size() == (32, 32)
```

I test per `display_object` con sprite NULL useranno monkeypatch su
`clientsprites.get` → restituisce sempre None, verifica che il
fallback geometrico viene chiamato.

### 3.5 Struttura cartella `img/` attesa (operatore)

```
img/
├── units/        18 PNG (uno per type_name unità)
├── buildings/    22 PNG
├── resources/    2  PNG (goldmine, wood)
├── terrain/      12 PNG (NB: senza underscore per i 3 auto-applicati)
└── ui/           5  PNG opzionali (selection_ring, hp_bar_*, attack_flash)
```

Totale obbligatorio per copertura completa: **54 PNG**.
Sprite UI: **5 PNG opzionali** (priorità MEDIA/BASSA per R16+).

### 3.6 Piano test R16

| ID | Nome | Cosa verifica |
|----|------|---------------|
| T1 | `test_sprite_cache_miss_returns_none` | File assente → None, no crash |
| T2 | `test_sprite_cache_hit_returns_surface` | File presente → Surface scalata |
| T3 | `test_sprite_cache_clear` | Dopo `clear()` la cache è vuota |
| T4 | `test_display_object_fallback_when_no_sprite` | mock `get` → None, verifica `pygame.draw.circle` chiamato |
| T5 | `test_display_terrain_fallback_when_no_sprite` | mock `get` → None, verifica `draw_rect` chiamato |
| T6 | `test_category_of_unit` / `_building` / `_resource` | resolver ritorna stringa categoria corretta |
| T7 | `test_visual_mode_off_does_not_load_sprites` | con `visual_mode=0`, nessuna chiamata a `SpriteCache.get` |

Suite attesa post-R16: **292 + ~7 = ~299 passed**, 0 fail.

### 3.7 Cosa cambia in `clientgamegridview.py` (R16)

Modifiche previste, tutte additive e con fallback geometrico:

- import: `from . import clientsprites`
- `_display()`: dopo `draw_rect(color, rect)` aggiungere blit terreno.
- `display_object()`: blit sprite prima del cerchio/rettangolo, con
  guardia `sprite is not None`.
- Nessuna rimozione di codice esistente.
- Nessuna modifica a path `voice.*`, `sounds.*`, `world*` (LEGGE-1).
- Nessuna modifica al meccanismo del guard `if not config.visual_mode`
  (LEGGE-2) — è già implicito nell'invocazione di `Interface.display()`.

---

## 4. DIPENDENZE E COMPATIBILITÀ

- **pygame 2.6.1**: tutte le API necessarie presenti (`image.load`,
  `convert_alpha`, `transform.scale`, `blit`, `SRCALPHA`).
- **Path della root progetto**: `soundrts.paths.BASE_DIR` viene già
  esposto e usato per `STATS_PATH`. La `SpriteCache` userà la stessa
  costante per costruire `_IMG_ROOT`.
- **Encoding immagini**: PNG con alpha. pygame li gestisce nativamente.

---

## 5. TODO Round 16 (post-img/)

1. **ALTA** — Creare `soundrts/clientsprites.py` (SpriteCache + category_of).
2. **ALTA** — Modificare `clientgamegridview.py` per integrare sprite
   nei punti PR-1, PR-2, PR-3 con fallback geometrico.
3. **ALTA** — Aggiungere 7 test in `test_clientsprites.py`.
4. **MEDIA** — Verificare suite ≥ 292 passed / 0 fail / 0 err.
5. **MEDIA** — Aggiornare `CHANGELOG.md` con sezione `[1.4.4]`.
6. **BASSA** — Sprite UI opzionali (selection_ring, hp_bar_*,
   attack_flash) → PR-4 / PR-5.

## 6. TODO Round 17+

1. **BASSA** — Refactor `R`/`R2` da globali di modulo a attributi
   `self.R`/`self.R2` di `GridView` (vedi 1.4).

---

## 7. Decisioni autonome registrate

- **R/R2 globali**: NON correggere in R16. Round dedicato futuro.
- **PR-4 indicatore fazione e HP bar**: NON sostituire con sprite in
  R16. Restano primitive. Sprite UI opzionali per round futuri.
- **PR-5 attack flash**: sprite OPZIONALE in R16 (BASSA priorità).
- **Risoluzione categoria**: lookup costruito da `style.txt` con
  fallback a mapping statico hardcoded. Decisione finale in R16.
- **Terrain naming**: i tre auto-applicati (`_meadows`, `_forest`,
  `_dense_forest`) verranno mappati a filename senza underscore.
- **`meadow`/`corpse`/`path`/`bridge`**: sprite opzionali (BASSA),
  decorativi non bloccanti per il gameplay.
- **Spell/effect** (`holy_vision`, `meteors`, `exorcism`): esclusi.

---

## 8. Stato suite

Nessun codice di produzione modificato in R15. Suite invariata:
**292 passed / 0 failed / 0 errors / 1 skipped**.
