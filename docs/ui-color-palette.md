# SoundRTS — Palette colori UI (stato attuale + proposta)

Versione: 2026-05-23
Stato: VALIDATO
Riferimento: `docs/ui-visual-plan.md`

## Convenzioni

- Tutti i colori sono RGB 0–255 (RGBA per HUD).
- I valori "ATTUALE" sono estratti dai sorgenti Python e da
  `res/ui/style.txt`. Le citazioni di linea si riferiscono ai file di
  produzione.
- I valori "PROPOSTO" applicano i task A1–A5 e B1–B6 del piano.

## Sfondo e cornici

| Elemento | Attuale | Proposto | File |
|---|---|---|---|
| Sfondo schermo | (0,0,0) | (0,0,0) invariato | [soundrts/clientgame.py](../soundrts/clientgame.py) |
| Bordo mappa | (100,100,100) | (140,140,140) | [soundrts/clientgamegridview.py](../soundrts/clientgamegridview.py) |
| Muro celle | (0,0,0) | (230,230,230) | [soundrts/clientgamegridview.py](../soundrts/clientgamegridview.py) |
| Bordo zona attiva (default) | (255,255,255) width 1 | (255,255,255) width 2 | [soundrts/clientgamegridview.py](../soundrts/clientgamegridview.py) |
| Bordo zona attiva (con target) | (150,150,150) width 1 | (200,200,200) width 2 | [soundrts/clientgamegridview.py](../soundrts/clientgamegridview.py) |
| Osservatore (camera) | (0,55,0) raggio 1 | (255,230,90) raggio 4 width 2 | [soundrts/clientgamegridview.py](../soundrts/clientgamegridview.py) |

## Terreni

| Terreno | style.txt | Attuale RGB | Proposto |
|---|---|---|---|
| `_meadows` | `color` vuoto | (0,25,0) fallback | (35,80,35) |
| `_forest` | `color` vuoto | (0,25,0) fallback | (25,65,30) |
| `_dense_forest` | `color` vuoto | (0,25,0) fallback | (15,50,25) |
| `river` | `blue4` | (0,0,139) | invariato |
| `lake` | `blue4` | (0,0,139) | invariato |
| `sea` | `blue` | (0,0,255) | invariato |
| `ocean` | `blue` | (0,0,255) | invariato |
| `mountain` | `dimgray` | (105,105,105) | invariato |
| `big_bridge` | `brown` | (165,42,42) | invariato |
| `ford` | `blue2` | (0,0,238) | invariato |
| `marsh` | `brown` | (165,42,42) | invariato |

## Faction flags (cerchio interno unità)

| Stato | Attuale | Proposto |
|---|---|---|
| Gruppo selezionato | (0,255,0) | invariato |
| Alleato proprio | (0,55,0) | (60,140,60) |
| Alleato altro | (0,0,155) | invariato |
| Nemico | (155,0,0) | invariato |
| Neutro | (0,0,0) | (180,180,180) |

## Barre HP

| Stato | Attuale | Proposto |
|---|---|---|
| Sopra 80% hp | (0,255,0) | invariato |
| Sotto 80% hp | (255,0,0) | invariato |

## HUD pannelli

| Elemento | Attuale | Proposto |
|---|---|---|
| Sfondo pannello | (0,0,0,165) | invariato |
| Bordo pannello | (70,110,120) | invariato |
| Label RES | (120,220,190) | invariato |
| Valore numerico RES | (220,220,210) | (255,235,130) |
| Label TIME | (160,210,255) | invariato |
| Label EVENTS | (255,190,120) | invariato |
| Label GROUP | (180,220,255) | invariato |
| Label PLAYER (nuovo B3) | — | (200,230,255) |
| Testo generico | (220,220,210) / (230,220,205) / (220,235,245) | invariato |
| Evento severity combat (B4) | — | (255,110,110) prefisso `!` |
| Evento severity info (B4) | — | (140,220,140) prefisso `+` |
| Evento severity alert (B4) | — | (255,200,110) prefisso `*` |

## Debug overlay (`display_metrics`)

Lasciato invariato (non target del piano normo-vedente,
è utility sviluppo).

| Elemento | Colore |
|---|---|
| Warn | (255,0,0) |
| Normal | (0,200,0) |

## Verifica accessibilità

- I nuovi colori mantengono rapporto di contrasto ≥ 4.5:1 vs sfondo nero
  per i pannelli HUD principali (header e valori numerici).
- I colori delle severity eventi sono distinti anche in scala di grigi
  perché differenziati da prefisso `!`, `+`, `*` (ridondanza
  testo+colore).
- Le coordinate audio non sono mai sostituite da segnali visivi:
  ogni cambiamento qui è additivo per il giocatore normo-vedente.
