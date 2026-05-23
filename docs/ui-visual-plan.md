# SoundRTS — Piano tecnico UI grafica per normo vedenti

Versione: 2026-05-23
Stato: VALIDATO (pronto per implementazione Fase 5)
Autore: DUSU Autonomous UI Design Engineer
Riferimento coordinatore: `doc_admin/todo.md` sezione "UI Grafica"

## Executive summary

La modalità grafica di SoundRTS è oggi un layer di debug minimale sopra il
core audio. Questo piano introduce miglioramenti estetici non invasivi su tre
aree: griglia tattica (palette differenziata terreni e flag faction), pannello
HUD (gerarchia tipografica e contrasto), interazione mouse (solo
infrastruttura per hit-zone futura). Tutte le modifiche rispettano la dualità
audio/grafico (Legge IA #8): la modalità audio-only e gli screen reader non
sono toccati.

## 1. Analisi stato attuale (sintesi Fase 1)

### Pipeline grafica esistente

1. `GameInterface.display()` in [soundrts/clientgame.py](../soundrts/clientgame.py)
   riempie lo schermo di nero a ogni frame, quindi chiama
   `grid_view.display()` e `hud_panel.display()` solo se
   `display_is_active` è True.
2. `GridView` disegna terreni, muri, unità, bordo zona attiva.
3. `HudPanel` disegna quattro pannelli (resources, time/speed, events,
   group) usando `screen_render` con font Arial 12 bold unico.
4. La modalità audio rimane indipendente: la voce e gli eventi sonori
   passano per `voice.item(...)` e `psounds`, mai per il rendering.

### Palette colori attuale (estratto)

| Elemento | Colore RGB | Sorgente |
|---|---|---|
| Sfondo schermo | (0,0,0) | `screen.fill` in `display()` |
| Bordo mappa | (100,100,100) | `_display()` GridView |
| Terreno default (no `color` in style) | (0,25,0) | `terrain_color()` fallback |
| Acqua river/lake | `blue4` ≈ (0,0,139) | style.txt |
| Acqua sea | `blue` ≈ (0,0,255) | style.txt |
| Montagna | `dimgray` ≈ (105,105,105) | style.txt |
| Ponte legno | `brown` ≈ (165,42,42) | style.txt |
| Guado | `blue2` ≈ (0,0,238) | style.txt |
| Muro celle | (0,0,0) | hardcoded GridView |
| Flag gruppo selezionato | (0,255,0) | hardcoded GridView |
| Flag alleato proprio | (0,55,0) | hardcoded GridView |
| Flag alleato altro | (0,0,155) | hardcoded GridView |
| Flag nemico | (155,0,0) | hardcoded GridView |
| Flag neutro | (0,0,0) | hardcoded GridView |
| Barra HP ok | (0,255,0) | hardcoded GridView |
| Barra HP danneggiata | (255,0,0) | hardcoded GridView |
| HUD sfondo pannello | (0,0,0,165) | HudPanel `_draw_panel` |
| HUD bordo pannello | (70,110,120) | HudPanel `_draw_panel` |
| HUD label RES | (120,220,190) | HudPanel display |
| HUD label EVENTS | (255,190,120) | HudPanel display |
| HUD label GROUP | (180,220,255) | HudPanel display |
| HUD label TIME | (160,210,255) | HudPanel display |
| HUD testo generico | (220,220,210) ~ (230,220,205) | HudPanel display |

### Criticità identificate (UX normo vedente)

| ID | Criticità | Riferimento | Severità |
|---|---|---|---|
| C1 | Terreni `_meadows`, `_forest`, `_dense_forest` rendono fallback `(0,25,0)` quasi nero, indistinguibili tra loro e dallo sfondo. | `style.txt` linee 326-344, `GridView.terrain_color` | alta |
| C2 | Flag faction neutro `(0,0,0)` invisibile su sfondo nero. | `GridView.display_object` | alta |
| C3 | Muri celle `(0,0,0)` invisibili su sfondo nero quando il terreno è scuro. | `GridView._display` | media |
| C4 | Osservatore disegnato con cerchio raggio 1 e width 1: praticamente puntino isolato, difficile da seguire. | `GridView._display_active_zone_border` | media |
| C5 | HUD usa singolo font Arial 12 bold senza gerarchia: header e testo identici per dimensione. | `lib/screen.py` font unico | media |
| C6 | HUD non mostra il nome del giocatore corrente né l'host della partita. | `HudPanel` | bassa |
| C7 | Nessuna indicazione visiva della cella attualmente selezionata se l'utente la cambia via tastiera con cursore non visibile. | `GridView._display_active_zone_border` | bassa |
| C8 | Eventi recenti scrollano in coda fissa senza distinzione visiva tra tipi (alert, combat, info). | `HudPanel.on_event` | bassa |

### Vincoli e limiti strutturali

- Modalità audio: nessun riferimento a renderer in `voice`, `sound`,
  `worldclient`, `worldorders`. Il vincolo è rispettato per costruzione se
  tutte le modifiche restano in `clientgame.py`, `clientgamegridview.py`,
  `clientgamehud.py`, `lib/screen.py`, `clientgameentity.py`.
- Pickling: `GameInterface.__getstate__/__setstate__` esclude `hud_panel` e
  lo ricrea. Nessun nuovo attributo non serializzabile può essere aggiunto
  senza aggiornare lo stesso meccanismo.
- Font: `pygame.font.SysFont("arial", 12, bold=True)` è creato a livello
  modulo. Aggiungere font extra deve essere fatto in modo difensivo
  (try/except, fallback alla SysFont attuale) per non rompere installazioni
  senza Arial.
- Test: `pytest.ini` ha `filterwarnings = error`. Nessuna nuova chiamata
  a deprecazioni o `getdefaultlocale`.

## 2. Piano Area A — Griglia tattica

Obiettivo: il giocatore normo vedente deve distinguere terreno, faction,
posizione corrente in meno di 1 secondo di osservazione.

### A1 — Palette terreni di fallback differenziata

- **File**: `soundrts/clientgamegridview.py` funzione `terrain_color`.
- **Modifica**: introdurre dizionario di fallback per i terreni
  automatici quando `style.get(terrain, "color")` ritorna vuoto.
  Mapping proposto:
  - `_meadows`  → `(35, 80, 35)` verde tenue
  - `_forest`   → `(25, 65, 30)` verde foresta
  - `_dense_forest` → `(15, 50, 25)` verde scuro più saturo
  - `_default`  → mantiene `(0, 25, 0)` esistente per retro-compat.
- **Impatto modalità audio**: nessuno (terrain_color usato solo in
  GridView).
- **Complessità**: BASSA. ~10 righe.
- **Rischio regressione**: BASSO. Style.txt continua a sovrascrivere se
  presente `color`.

### A2 — Flag faction neutra visibile

- **File**: `soundrts/clientgamegridview.py` `display_object`.
- **Modifica**: sostituire colore neutro `(0,0,0)` con grigio chiaro
  `(180, 180, 180)`. Aggiornare anche alleato proprio da `(0,55,0)` a
  `(60, 140, 60)` per migliorare leggibilità su sfondo scuro.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA. 3 righe.

### A3 — Muri celle più contrastati

- **File**: `soundrts/clientgamegridview.py` `_display` (loop walls).
- **Modifica**: tupla `((0,0,0), walls)` → `((230, 230, 230), walls)`.
  I muri restano visibili su terreni di ogni saturazione.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA. 1 riga.

### A4 — Osservatore (camera) più visibile

- **File**: `soundrts/clientgamegridview.py` `_display_active_zone_border`.
- **Modifica**: cerchio osservatore disegnato con raggio 4 e width 2,
  colore `(255, 230, 90)` (giallo brillante) indipendente dalla presenza
  del target.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA. 1 riga.

### A5 — Bordo zona attiva più marcato

- **File**: `soundrts/clientgamegridview.py` `_display_active_zone_border`.
- **Modifica**: `draw_rect(color, rect, 1)` → width 2. Il bordo attivo
  resta bianco/grigio ma raddoppia in spessore per essere localizzato
  rapidamente con periferia visiva.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA.

## 3. Piano Area B — Pannello HUD

Obiettivo: gerarchia visiva chiara, contrasto adeguato, supporto a
schermi con larghezza ≥ 480 px (downgrade silenzioso per finestre
piccole).

### B1 — Font tipografico gerarchico

- **File**: `soundrts/lib/screen.py`.
- **Modifica**: aggiungere `_font_header` (Arial 16 bold) e `_font_small`
  (Arial 11) accanto a `_font`. Esportare nuove funzioni
  `screen_render_header(text, dest, color)` e
  `screen_render_small(text, dest, color)` riusabili dal HUD. Comporre
  via try/except con fallback al `_font` esistente.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA. ~20 righe.
- **Test**: snapshot del HUD non richiede pygame; rendering reale non
  testato in CI.

### B2 — Header pannelli con font dedicato

- **File**: `soundrts/clientgamehud.py` `_draw_snapshot`.
- **Modifica**: sostituire `screen_render("RES", ...)` ecc. con
  `screen_render_header(...)`. Allargare il pannello in altezza di
  `+5 px` per ospitare header più grande.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA.

### B3 — Pannello PLAYER (nome giocatore + faction)

- **File**: `soundrts/clientgamehud.py` (aggiungi metodo
  `_player_line`) e `HudSnapshot` dataclass (campo `player: str`).
- **Modifica**: nuovo pannello compatto sopra HUD GROUP (bottom-left,
  altezza 30 px) con etichetta `PLAYER` e nome `self.interface.player.name`.
  Se non disponibile → "Player".
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA.

### B4 — Differenziazione visiva eventi

- **File**: `soundrts/clientgamehud.py` `on_event`, `_format_event`,
  `_draw_snapshot`.
- **Modifica**:
  - Estendere il buffer eventi salvando una tupla
    `(severity, text)` invece della sola stringa. `HudUnitSnapshot`
    non viene toccato; introdurre nuova dataclass `HudEvent`.
  - `severity` ∈ `{"info", "alert", "combat"}` derivata dal tipo evento
    (`death`, `attack` → combat; `complete`, `discovered` → info; altro →
    alert).
  - Render: prefisso `!` per combat in `(255, 110, 110)`, `+` per info in
    `(140, 220, 140)`, `*` per alert in `(255, 200, 110)`.
- **Impatto modalità audio**: nessuno (push_event resta sincrono).
- **Complessità**: MEDIA. Aggiornare anche test esistenti
  `test_clientgamehud.py`.

### B5 — Barre risorse con valore numerico evidenziato

- **File**: `soundrts/clientgamehud.py` `_draw_snapshot`.
- **Modifica**: nella sezione RES disegnare il valore numerico a destra
  della label con `screen_render` color `(255, 235, 130)` per dare
  immediato fuoco visivo al numero.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA.

### B6 — Indicatore di velocità di gioco con icona testuale

- **File**: `soundrts/clientgamehud.py` `_draw_snapshot`.
- **Modifica**: prefisso `>>` se speed >= 1.5, `>` se 1.0–1.49, `=` se
  < 1.0. Mantenere stringa esistente come fallback.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA.

## 4. Piano Area C — Pulsanti / Interazione mouse

### Decisione: [PULSANTI: PARZIALE]

L'architettura esistente non ha widget system. `_process_fullscreen_mode_mouse_event`
risponde a hover/click come comandi RTS. Aggiungere pulsanti completi
(rendering + hit test + popup) richiederebbe:

1. Un mini-framework di widget (Rect → callback) in `clientgame.py` o
   nuovo modulo `clientgameui.py`.
2. Cambio del flusso eventi mouse per filtrare click su widget prima di
   trattarli come comandi mappa.
3. Sistema di focus/popup compatibile con la modalità audio (deve
   essere ignorato quando NVDA è attivo).

Costo complessivo: ALTO, rischio MEDIO-ALTO di regressioni di selezione.

### C1 — Pre-fix architetturale (solo questa iterazione)

- **File**: `soundrts/clientgame.py` `_process_fullscreen_mode_mouse_event`
  e `soundrts/clientgamehud.py`.
- **Modifica**: aggiungere all'inizio del metodo un guard
  `if self.hud_panel.handle_mouse_event(e): return`. `HudPanel.handle_mouse_event`
  oggi ritorna sempre `False` (no-op). Questo introduce il punto di
  estensione per pulsanti futuri senza alterare il comportamento attuale.
- **Impatto modalità audio**: nessuno.
- **Complessità**: BASSA.
- **Rischio regressione**: BASSO (no-op iniziale).

### C2 — Pulsanti veri e finestre popup

Rimandato a successivo ciclo. Documentato come task aperto in
`doc_admin/todo.md` ma fuori dal perimetro di questa iterazione.

## 5. Roadmap implementativa prioritizzata

| Ordine | Task | Impatto visivo | Complessità | Rischio |
|--:|---|:--:|:--:|:--:|
| 1 | A2 — Flag faction neutra visibile | alto | bassa | basso |
| 2 | A1 — Palette terreni fallback | alto | bassa | basso |
| 3 | A3 — Muri contrastati | medio | bassa | basso |
| 4 | A4 — Osservatore visibile | medio | bassa | basso |
| 5 | A5 — Bordo zona attiva più marcato | medio | bassa | basso |
| 6 | B1 — Font gerarchico in `screen.py` | medio | bassa | basso |
| 7 | B2 — Header HUD con font dedicato | medio | bassa | basso |
| 8 | B5 — Valori risorse evidenziati | medio | bassa | basso |
| 9 | B6 — Icona velocità | basso | bassa | basso |
| 10 | B3 — Pannello PLAYER | medio | bassa | basso |
| 11 | B4 — Eventi colorati per severity | medio | media | basso |
| 12 | C1 — Hook handle_mouse_event no-op | basso | bassa | basso |

I task A2/A1/A3 sono fixie indipendenti e possono essere implementati in
qualsiasi ordine; vengono raggruppati nell'ordine indicato.

## 6. Vincoli e rischi

- **R1**: introducendo nuovi font in `screen.py` la prima
  inizializzazione pygame deve essere già avvenuta. È garantito dal fatto
  che `pygame.font.init()` è chiamato a top-level del modulo.
- **R2**: `HudPanel.handle_mouse_event` deve essere chiamato anche dopo
  `__setstate__` (HUD ricreato). Verificare che il metodo esista
  sull'istanza ricreata.
- **R3**: i test in `soundrts/tests/unittests/test_clientgamehud.py`
  vanno aggiornati se cambia `HudSnapshot` (B3/B4).
- **R4**: nessuna modifica a `bindings.txt`, `voice.py`, `sound.py`,
  `world*` per garantire Legge IA #8.

## 7. Criteri di validazione per ogni modifica

Per ogni task della roadmap:

1. **Lettura preliminare** del file target (Legge IA #1).
2. **py_compile** del file modificato dopo la modifica.
3. **Pylance/get_errors** = 0 errori.
4. **Test unitari**:
   - `pytest soundrts/tests/unittests/test_clientgamehud.py -q` PASS.
   - eventuali nuovi test aggiunti per il task → PASS.
5. **Snapshot regressione audio**: nessun import di
   `voice`/`sound`/`world*` aggiunto al di fuori di quanto già presente.
6. **Verifica dualità**: `display_is_active` continua a determinare il
   render. Nessun side-effect nei rami `not display_is_active`.

## 8. File creati / modificati previsti

### Modificati

- `soundrts/clientgamegridview.py` (A1, A2, A3, A4, A5)
- `soundrts/lib/screen.py` (B1)
- `soundrts/clientgamehud.py` (B2, B3, B4, B5, B6, C1)
- `soundrts/clientgame.py` (C1 hook chiamata)
- `soundrts/tests/unittests/test_clientgamehud.py` (estensione test B3/B4)

### Creati

- `docs/ui-visual-plan.md` (questo file)
- `docs/ui-color-palette.md`
- `docs/ui-hud-layout.md`

### Non toccati (vincolo Legge IA #8)

- `soundrts/lib/voice.py`, `soundrts/lib/sound.py`, `soundrts/lib/msgs.py`
- `soundrts/world*.py`, `soundrts/server*.py`
- `res/ui/bindings.txt`, `res/ui/style.txt` (palette del progetto resta
  intatta; il fix terreno è in codice, non in dati)
- `soundrts/clientmedia.py` (no toggle behavior change)

## 9. Verdetto

**VALIDATO**: il piano rispetta la dualità audio/grafico, è incrementale,
ogni task è isolato e testabile separatamente.
