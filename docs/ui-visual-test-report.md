# UI Visual Test Report — HudPanel Layout

## Data: 2026-05-24

## Risoluzioni testate: 400x300, 420x260, 640x480, 800x600, 1024x768, 1280x720, 1366x768, 1920x1080

## Layout analizzato

```text
┌─────────────────────────────────────────────┐
│ PANNELLO: RES                              │
│ X: margin                                  │
│ Y: margin                                  │
│ W: 180                                     │
│ H: 30 + len(resources) * 15                │
│ Max righe: len(resources) + 1 food line    │
│ Line height: 15 px                         │
│ Anchor: top-left                           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PANNELLO: TIME                             │
│ X: (width - margin) - 175                  │
│ Y: margin                                  │
│ W: 175                                     │
│ H: 60                                      │
│ Max righe: 2                               │
│ Line height: 15 px                         │
│ Anchor: top-right                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PANNELLO: EVENTS                           │
│ X: (width - margin) - 260                  │
│ Y: margin + 70                             │
│ W: 260                                     │
│ H: 30 + max(1, len(events)) * 15           │
│ Max righe: min(len(events), 8)             │
│ Line height: 15 px                         │
│ Anchor: top-right                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PANNELLO: PLAYER                           │
│ X: margin                                  │
│ Y: group_top - 30 - 4                      │
│ W: 295                                     │
│ H: 30                                      │
│ Max righe: 1                               │
│ Line height: 15 px                         │
│ Anchor: bottom-left                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PANNELLO: GROUP                            │
│ X: margin                                  │
│ Y: (height - margin) - group_height        │
│ W: 295                                     │
│ H: 30 + max(1, len(units)) * 15            │
│ Max righe: min(len(units), 8)              │
│ Line height: 15 px                         │
│ Anchor: bottom-left                        │
└─────────────────────────────────────────────┘
```

Relazioni di dipendenza tra pannelli:

- PLAYER dipende da GROUP: si posiziona a 4 px sopra il bordo superiore di GROUP.
- GROUP dipende da height e dal numero di unità: più unità, più sale verso l'alto.
- EVENTS dipende da width e dal numero di eventi: resta ancorato a destra ma cresce in altezza verso il basso.
- TIME dipende da width: resta ancorato in alto a destra.
- RES non dipende dalla risoluzione per dimensione, solo dal margine e dal numero di risorse.

⚠️ [ASSUNZIONE] Per T5 l'altezza header stimata è 20 px, coerente con la misura reale del font header (19 px).
⚠️ [ASSUNZIONE] Lo snapshot usato nel test rappresenta il caso realistico richiesto: 3 risorse, 2 unità, 5 eventi, player con nome e razza.

## Risultati per risoluzione

| Risoluzione | T1 | T2 | T3 | T4 | T5 | Esito |
| ----------- | -- | -- | -- | -- | -- | ----- |
| 400x300 | ✅ | n/a | n/a | n/a | n/a | SKIP ✅ |
| 420x260 | n/a | ❌ | ✅ | ✅ | ❌ | FAIL |
| 640x480 | n/a | ✅ | ✅ | ✅ | ❌ | FAIL |
| 800x600 | n/a | ✅ | ✅ | ✅ | ❌ | FAIL |
| 1024x768 | n/a | ✅ | ✅ | ✅ | ❌ | FAIL |
| 1280x720 | n/a | ✅ | ✅ | ✅ | ❌ | FAIL |
| 1366x768 | n/a | ✅ | ✅ | ✅ | ❌ | FAIL |
| 1920x1080 | n/a | ✅ | ✅ | ✅ | ❌ | FAIL |

Note per risoluzione:

- 400x300: display() ritorna prima di _draw_snapshot() per width < 420. Comportamento corretto sotto soglia.
- 420x260: overlap tra RES ed EVENTS. Rect misurati: RES = (8, 8, 180, 75), EVENTS = (152, 78, 260, 105).
- 640x480 e superiori: nessuna collisione tra pannelli e nessun overflow del contenitore HUD; resta pero insufficiente l'altezza del pannello RES.

## Misure font reali

Output misurato con pygame.font.SysFont:

```text
body: height=14px  sample_width=200px  sample_height=14px
header: height=19px  sample_width=271px  sample_height=19px
small: height=13px  sample_width=185px  sample_height=13px
```

Confronto con le assunzioni del codice:

- line_height = 15 px: sufficiente per il font body da 14 px.
- header stimato ~20 px: confermato dal valore reale 19 px.
- 180 px RES e 175 px TIME non contengono una riga body lunga circa 40 caratteri senza troncamento.
- 260 px EVENTS e 295 px GROUP/PLAYER sono compatibili con la stringa campione misurata.

## Problemi rilevati

- [CRITICO] [420x260] [RES/EVENTS]: sovrapposizione tra pannelli in alto. Il layout fisso non rispetta la soglia minima dichiarata di 420 px.
  → Correzione proposta: rendere EVENTS responsive in larghezza a risoluzioni strette, oppure alzare min_width ad almeno 456 px se le larghezze fisse restano invariate.
- [MEDIO] [420x260, 640x480, 800x600, 1024x768, 1280x720, 1366x768, 1920x1080] [RES]: altezza pannello insufficiente per header + 3 righe risorsa + riga food. Stima misurata: 80 px necessari contro 75 px disponibili.
  → Correzione proposta: includere la riga food nel calcolo di res_rect.height, ad esempio 30 + (len(resources) + 1) * line_height.
- [BASSO] [Tutte le risoluzioni funzionali] [RES/TIME]: la larghezza body misurata per una riga lunga (~200 px) supera i pannelli da 180 px e 175 px.
  → Correzione proposta: usare limiti testo basati su misura font reale, o ridurre il budget testuale per i pannelli stretti.

## Raccomandazioni

1. Correggere per primo il conflitto 420x260, scegliendo tra layout responsive o aumento esplicito della soglia minima supportata.
2. Correggere poi la formula di altezza del pannello RES, che oggi omette la riga food e produce clipping stimato a tutte le risoluzioni operative.
3. Introdurre in HudPanel un calcolo basato su metriche font reali per le larghezze testo, invece di affidarsi solo a budget per numero di caratteri.
4. Mantenere il nuovo test_hud_layout.py come guardia regressiva dopo il fix del layout.

## Vincoli rispettati

- [x] Legge IA #8: modalità audio non impattata
- [x] Nessun file sorgente esistente modificato
- [x] Tutti i problemi emersi dai test e dalle misure font sono documentati

## Esito validazione artefatti

- test_hud_layout.py: VALIDATO sintatticamente con py_compile; pytest mirato eseguito con 21 test PASS e 8 FAIL diagnostici reali.
- ui-visual-test-report.md: contenuto allineato ai risultati T1-T5 e alle misure font raccolte.

---

## Stato post-fix — 2026-05-24

### Modifiche applicate

| File | Modifica | Bug risolto |
|------|----------|-------------|
| `soundrts/lib/screen.py` | body 12→14 bold, header 16→18, small 11→12 | [BASSO] leggibilità, [NUOVO] upgrade richiesto |
| `soundrts/clientgamehud.py` | `min_width` 420→460, `min_height` 260→280 | [CRITICO] overlap RES/EVENTS a 420×260 |
| `soundrts/clientgamehud.py` | `line_height` 15→19 | consistenza con font aggiornato |
| `soundrts/clientgamehud.py` | formula `res_rect.height` aggiunge `+1` food row | [MEDIO] altezza RES insufficiente |
| `soundrts/tests/unittests/test_hud_layout.py` | `FUNCTIONAL_RESOLUTIONS` da indice 1 a indice 2; T1 usa 420×260 | allineamento soglie al codice aggiornato |

### Misure font post-upgrade

```text
14 bold (body):   height=17px  w_short=84px  w_long=165px
18 bold (header): height=21px  (stimato proporzionalmente da 19px a 16 bold)
12 reg  (small):  height=14px  (stimato)
```

*Nota: `w_short` = "Resource 1: 999" (15 char); `w_long` = "Resource 1: 999  food test long" (31 char).*

### Tabella risoluzioni post-fix

| Risoluzione | T1 | T2 | T3 | T4 | T5 | Esito |
| ----------- | -- | -- | -- | -- | -- | ----- |
| 400×300 | ✅ | n/a | n/a | n/a | n/a | SKIP ✅ |
| 420×260 | ✅ | n/a | n/a | n/a | n/a | SKIP ✅ |
| 640×480 | n/a | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 800×600 | n/a | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1024×768 | n/a | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1280×720 | n/a | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1366×768 | n/a | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1920×1080 | n/a | ✅ | ✅ | ✅ | ✅ | PASS ✅ |

### Esito pytest

```
25 passed, 0 failed  (pytest 9.0.3, Python 3.12.0, pygame 2.6.1)
```

### Vincoli rispettati post-fix

- [x] Legge IA #8: `screen_render`, `screen_render_header`, `screen_render_small` non sono mai chiamate da path audio.
- [x] `clientgamegridview.py` invariato.
- [x] Tutte le modifiche sono additive o di costanti: nessuna logica audio/world alterata.

---

## Stato post-fix Round 2 — 2026-05-24

### Fix applicati

| File | Modifica | Fix |
|------|----------|-----|
| `soundrts/lib/screen.py` | body 14→**17** bold, header 18→**21** bold, small 12→**15** reg | FIX-A font upgrade |
| `soundrts/lib/screen.py` | `screen_render_subtitle()` ancorata bottom-right | FIX-B status bar |
| `soundrts/clientgamehud.py` | `time_rect` height 60→**68** px | FIX-C TIME clipping |
| `soundrts/clientgamehud.py` | `line_height` 19→**23**, `min_height` 280→**308** | FIX-A2 geometria |
| `soundrts/tests/unittests/test_hud_layout.py` | aggiunto `test_time_panel_has_minimum_height` | T_TIME_PADDING |

### Misure font Round 2

```
=== Arial 17 bold ===
  short  ("Resource 1: 999"):  110x20px
  medium ("Speed: x1.5"):       80x20px
  long40 ("X"*40):             361x20px

=== Arial 21 bold (header) ===  [stimato: body+4]
=== Arial 15 reg  (small)  ===  [stimato: body-2]
```

### Status bar — posizione aggiornata

| Versione | Formula x | Formula y | Zona |
|----------|-----------|-----------|------|
| Prima | `(width - ren_width) // 2` | `height - ren_height` | Centro schermo, su mappa |
| Dopo  | `width - ren_width - 16`   | `height - ren_height - 4` | Bottom-right, fuori mappa |

### Tabella risoluzioni post-fix Round 2

| Risoluzione | T1 | T2 | T3 | T4 | T5 | T_TIME | Esito |
| ----------- | -- | -- | -- | -- | -- | ------ | ----- |
| 400×300 | ✅ | n/a | n/a | n/a | n/a | n/a | SKIP ✅ |
| 420×260 | ✅ | n/a | n/a | n/a | n/a | n/a | SKIP ✅ |
| 640×480 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 800×600 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1024×768 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1280×720 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1366×768 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1920×1080 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |

### Esito pytest Round 2

```
31 passed, 0 failed  (pytest 9.0.3, Python 3.12.0, pygame 2.6.1)
```

### Nota runtime Round 2

- La leggibilità del font 17px e la posizione della status bar richiedono conferma visiva su partita reale (T_SUBTITLE_RIGHT documentato come test manuale in `test_hud_layout.py`).

### Vincoli rispettati Round 2

- [x] Legge IA #8: `screen_render_subtitle()` e `_font` non sono mai chiamate da path audio.
- [x] `clientgamegridview.py` invariato.
- [x] `display_is_active` gate non modificato.

---

## Stato post-fix Round 3 — 2026-05-24

### Fix applicati

| File | Modifica | Fix |
|------|----------|-----|
| `soundrts/lib/screen.py` | `screen_subtitle_set()` ora usa `screen_render_subtitle()` nel fallback non-game-mode | FIX-1 percorso runtime status bar |
| `soundrts/lib/screen.py` | body 17→**20** bold, header 21→**24** bold, small 15→**18** reg | FIX-2 font scale |
| `soundrts/clientgamehud.py` | `line_height=26`, `min_height=360`, `time_height=88`, `panel_header_height=36` | FIX-2 geometria |
| `soundrts/clientgamehud.py` | stringhe HUD lette da `style.get("hud", ...)` con fallback EN | FIX-3 i18n |
| `res/ui/style.txt` / `res/ui-it/style.txt` | 18 chiavi HUD EN/IT aggiunte | FIX-3 localizzazione |
| `soundrts/tests/unittests/test_hud_layout.py` | aggiunti T_FONT_SIZE, T_I18N_KEYS, T_SUBTITLE_POSITION | test Round 3 |

### Misure font aggiornate

```text
Arial 19 bold: h=22px | short=122px | long36=361px
Arial 20 bold: h=23px | short=125px | long36=396px
Arial 21 bold: h=25px | short=137px | long36=397px
Arial 22 bold: h=26px | short=138px | long36=433px
Arial 23 bold: h=27px | short=141px | long36=468px
Arial 24 bold: h=28px | short=151px | long36=469px
```

## Stato post-fix Round 6 — 2026-05-24

### HUD-1: Allineamento colonna destra

- `event_width`: 260 → 295 (unificato in `col_right_width = 295`)
- EVENTS, PLAYER, GROUP partono tutti da `x = width - margin - 295`
- TIME rimane invariato (`width = 175`, right-anchored)
- Bordo sinistro colonna destra completamente allineato

### MAP-1/2/3: Visibilità elementi mappa

- `R_MIN = 4`: raggio minimo unità garantito in `_update_coefs()` — diametro minimo 8px
- Marker fazione: `max(2, R // 2)` — cerchio sempre visibile
- Barra HP: `W = max(3, R - 2)` — larghezza minima 6px totali

### Risultati test

- `pytest soundrts/tests/unittests/test_hud_layout.py`: **89 passed, 0 failed**
- Nuovi test Round 6: T_EVENTS_ALIGNED_WITH_GROUP (6 risoluzioni), T_FACTION_MARKER_MIN (7 valori R), T_HP_BAR_W_MIN (7 valori R), T_R_MIN_ENFORCED.

### Stato todo

- CHIUSO: tutti i punti residui `[ ]` marcati `[x]` — nessun punto aperto.

Tradeoff documentato: nessun candidato 19-24 rispetta `long36 <= 254`; è stato scelto Arial 20 bold perché è la massima dimensione con `height <= 24px`. L'overflow EVENTS viene mitigato riducendo `event_text_max_length` a 23 caratteri.

### Tabella risoluzioni post-fix Round 3

| Risoluzione | T1 | T2 | T3 | T4 | T5 | T_TIME | T_FONT | T_I18N | T_SUBTITLE | Esito |
| ----------- | -- | -- | -- | -- | -- | ------ | ------ | ------ | ---------- | ----- |
| 400×300 | ✅ | n/a | n/a | n/a | n/a | n/a | ✅ | ✅ | ✅ | SKIP ✅ |
| 420×260 | ✅ | n/a | n/a | n/a | n/a | n/a | ✅ | ✅ | ✅ | SKIP ✅ |
| 640×480 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 800×600 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1024×768 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1280×720 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1366×768 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |
| 1920×1080 | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS ✅ |

### Risultati test post-fix Round 3

```text
py_compile: OK
imports: IMPORTS OK
i18n: I18N OK
pytest test_hud_layout.py: 34 passed, 0 failed
```

### Note runtime

- Status bar, font 20px e stringhe HUD IT richiedono conferma visiva su partita reale fullscreen.

### Vincoli rispettati Round 3

- [x] Legge IA #8: nessun import verso voice/sound/world* e `display_is_active` invariato.
- [x] Nessuna stringa italiana hardcoded in Python.
- [x] Localizzazione integrata nel sistema `style.get(...)` già usato da SoundRTS.

---

## Stato post-fix Round 4 — 2026-05-24

### Fix applicati

| File | Modifica | Fix |
|------|----------|-----|
| `soundrts/lib/screen.py` | `screen_render_subtitle()`: aggiunto guard `if not _subtitle: return` | FIX-1 difensivo |
| `soundrts/clientgamehud.py` | `_parts_to_text()`: rimosso filtro `isdigit` — valori numerici HUD preservati | FIX-2 safety |
| `soundrts/clientgamehud.py` | `_resource_name()`: filtro `isdigit` applicato esplicitamente prima di `_parts_to_text()` | FIX-2 scoping |
| `soundrts/tests/unittests/test_hud_layout.py` | aggiunti 4 test Round 4 | test |

### Analisi forense FIX-1

- **Ipotesi smentita**: `clientgamegridview.py` NON contiene alcun rendering testuale (nessuna chiamata a `screen_render*`, nessuna `font.render`).
- **Percorso runtime reale**: `lib/message.py:53` → `screen_subtitle_set()` → `_subtitle = txt` → `clientgame.py:2114 display()` → `screen_render_subtitle()` → `_subtitle_position()` → bottom-right.
- **Stato pre-Round 4**: Già corretto da Round 2+3. Nessun percorso basso-sinistra residuo.
- **Testo basso-sinistra visibile**: solo i pannelli HUD GROUP/PLAYER (by design, intenzionale).

### Risultati test post-fix Round 4

```text
py_compile: OK (soundrts/lib/screen.py, soundrts/clientgamehud.py)
pytest test_hud_layout.py: 38 passed, 0 failed
```

### Nuovi test aggiunti

| ID | Descrizione |
|----|-------------|
| T_PARTS_TO_TEXT_PRESERVES_NUMBERS | Verifica che token digit in lista siano preservati |
| T_PARTS_TO_TEXT_ZERO | Verifica che "0" come elemento lista non sia rimosso |
| T_RESOURCE_NAME_STRIPS_DIGITS | Verifica che il filtro digit in `_resource_name()` funzioni correttamente |
| T_INFOBAR_POSITION | Test forense su 3 risoluzioni (640×480, 1024×768, 1920×1080) |

### Note runtime

- Conferma visiva necessaria: assenza rettangolo nero quando subtitle è vuoto.
- Conferma visiva necessaria: valori numerici HUD (contatori risorse, pop) visualizzati correttamente.

### Vincoli rispettati Round 4

- [x] Legge IA #8: nessun import verso voice/sound/world* e `display_is_active` invariato.
- [x] Nessuna stringa italiana hardcoded in Python.
- [x] Nessuna funzionalità esistente rimossa.

---

## MAP Layout Round 7 — 2026-05-24

### MAP-VIEWPORT-1: viewport ridotto

Costante: `hud_right_width = 303px`.
Formula: `map_w = max(screen_w // 2, screen_w - 303)`.
Mappa tipica verificata: `xcmax=9`, `ycmax=7` (10x8 celle).

| Risoluzione | screen_w | map_w | sq_old | sq_new | Nota |
|-------------|----------|-------|--------|--------|------|
| 640x480     | 640      | 337   | 60px   | 33px   | width-limited |
| 800x600     | 800      | 497   | 75px   | 49px   | width-limited |
| 1024x768    | 1024     | 721   | 96px   | 72px   | width-limited |
| 1280x720    | 1280     | 977   | 90px   | 90px   | height-limited |
| 1920x1080   | 1920     | 1617  | 135px  | 135px  | height-limited |

Nota: a 640x480, 800x600 e 1024x768 la cella si riduce per liberare la colonna HUD destra. A 1280x720 e 1920x1080 la mappa 10x8 resta limitata dall'altezza, quindi la cella non cambia ma il limite orizzontale resta esplicito.

### MAP-SCALE-1: scala visiva unita

`UNIT_SCALE = 2.0` (aggiornato in Round 7b dopo conferma runtime test).
`R_vis = max(4, int(R * 2.0))`.

| R fisica | R_vis display | Marker | HP_W |
|----------|---------------|--------|------|
| 4        | 8             | 4      | 6    |
| 6        | 12            | 6      | 10   |
| 8        | 16            | 8      | 14   |
| 10       | 20            | 10     | 18   |

### Hit-test e zoom

- `square_from_mousepos()`, `object_from_mousepos()` e `units_from_mouserect()` restano in coordinate schermo non traslate (`map_x=0`, `map_y=0`).
- `R2 = R * R` resta invariato e non usa `R_vis`.
- `zoom_mode` resta compatibile: `_display_active_zone_border()` usa le stesse coordinate mappa scalate da `square_view_width`/`square_view_height`.

### Risultati test

- `py_compile`: OK (`clientgamegridview.py`, `test_hud_layout.py`).
- `pytest soundrts/tests/unittests/test_hud_layout.py -v --tb=short`: 105 passed, 0 failed.
- Nuovi/aggiornati Round 7: T_MAP_VIEWPORT_CLIP, T_UNIT_SCALE_APPLIED, T_R2_NOT_SCALED, T_HUD_RIGHT_WIDTH, T_HIT_TEST_INVARIANT, marker/HP bar su `R_vis`.
