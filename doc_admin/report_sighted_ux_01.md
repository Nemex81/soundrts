# SoundRTS Dualmode — Sighted Player UX Report

## Round UI-SIGHTED-01

### Executive Summary

SoundRTS dispone gia di un layer visivo maturo (HUD esteso, sprite,
tooltip, flash movimento, rect-highlight gruppo). L'analisi
del sorgente in `soundrts/clientgame.py` mostra che la selezione
left-click, il rubber-band drag e il movimento right-click sono
gia funzionanti (SI-02 e SI-03 risultano quindi **ALREADY-DONE**
parziali). Il gap UX residuo per il giocatore normovedente e
l'assenza di un **menu contestuale visivo** per impartire ordini
non banali (attack, patrol, stop, train, build) senza ricorrere
alle shortcut tastiera. L'obiettivo del round e introdurre questo
menu (SI-01) e un feedback visivo aggiuntivo per gli ordini
(SI-04), rispettando l'invariante audio (LEGGE-6, LEGGE-7).

### Inventario Funzionalita Visive

| # | Funzionalita | Stato | Qualita | Priorita |
|---|--------------|-------|---------|----------|
| 1  | Mappa renderizzata (sprite + terrain fallback) | implementata | sufficiente | BASSA |
| 2  | Identificazione visiva unita (sprite + cerchio colore) | implementata | sufficiente | BASSA |
| 3  | Highlight unita nel gruppo (UI-MASTER-07/P1 rect verde pastello) | implementata | sufficiente | BASSA |
| 4  | HUD risorse / food / tempo / velocita | implementata | sufficiente | BASSA |
| 5  | HUD pannello GROUP con lista unita | implementata | sufficiente | BASSA |
| 6  | HUD pannello ACTIVITY con ordini in corso | implementata | sufficiente | BASSA |
| 7  | HUD pannello EVENTS con log eventi | implementata | sufficiente | BASSA |
| 8  | Tooltip su hover (mappa, HUD, cella vuota) | implementata | sufficiente | BASSA |
| 9  | Feedback visivo movimento (flash verde) | implementata | sufficiente | BASSA |
| 10 | Selezione unita con left-click | implementata | sufficiente | BASSA |
| 11 | Ordine movimento con right-click (cmd_default) | implementata | sufficiente | BASSA |
| 12 | Context menu ordini su click | assente | critica | ALTA |
| 13 | Rubber-band selection (drag left-click) | implementata | sufficiente | BASSA |
| 14 | Minimap | assente | n/a | BASSA |
| 15 | Indicatore di pausa | implementata | sufficiente | BASSA |
| 16 | Feedback visivo attacco/morte (display_attack) | implementata parziale | migliorabile | MEDIA |
| 17 | Differenziazione visiva alleati/nemici/neutri | implementata | sufficiente | BASSA |
| 18 | Indicatore stack numerico unita per cella | assente | migliorabile | BASSA |

#### Note di verifica sorgente

- Funz. 10 e 13: vedi `soundrts/clientgame.py` linee 985-1051 (`MOUSEBUTTONDOWN` + `MOUSEBUTTONUP` button 1). Pattern: `mouse_select_origin = e.pos` al down, al up se pos uguale → `cmd_command_unit()`, se diversa → `units_from_mouserect` → `self.group = [...]` → `say_group()`.
- Funz. 11: `soundrts/clientgame.py` linee 997-1027 (`button == 3` → `cmd_default(*args)` + `flash_move_target`).
- Funz. 12: assente. La selezione di un ordine non banale richiede `cmd_select_order` (tastiera) o shortcut singolo carattere via `_execute_order_shortcut`. Nessun menu visivo (`grep "context_menu" soundrts/*.py` → 0 match).
- Funz. 3: `_SELECTION_HIGHLIGHT_COLOR` introdotto in UI-MASTER-07 P1.
- Funz. 16: `display_attack` (`soundrts/clientgamegridview.py` ~L378) disegna due linee transitorie attacker→target ma non un flash sull'unita bersaglio.

### Gap Analysis

#### GAP-01: Context Menu Ordini

**Problema:** il normovedente che gioca al solo mouse non puo
impartire ordini diversi dal "default" (movimento, attacco automatico
sul nemico sotto il cursore). Tutto il resto (attack esplicito,
patrol, stop, train, build, research) e raggiungibile solo via
hotkey o ciclo `cmd_select_order`.

**Impatto:** funzionalita core RTS preclusa al mouse user. UX-GAP
critico per onboarding di nuovi giocatori normovedenti.

**Strategia proposta:** introdurre un menu floating su right-click
con un'entita propria sotto il cursore. Il menu riutilizza
`self.orders()` (gia presente in `clientgame.py` L1788) che restituisce
una lista di `OrderTypeView` con `.title`, `.encode`, `.nb_args`.
Click su voce con `nb_args == 0` → `send_order(o.encode, None, [])`.
Click su voce con `nb_args > 0` → `_select_order(o)` (segnaposto, poi
left-click per confermare il target — flusso identico alla UI esistente).

**Complessita:** MEDIA — circa 220 righe in `clientgamehud.py`
(dataclass + show/hide/draw/handle context menu), 40 righe in
`clientgame.py` (hook in handler button==3), 25 righe in
`clientgamegridview.py` (nuovo `entity_at_mousepos`).

**File impattati:** `soundrts/clientgame.py`, `soundrts/clientgamehud.py`,
`soundrts/clientgamegridview.py`, `res/ui/style.txt`,
`res/ui-it/style.txt`, `soundrts/tests/unittests/test_ui_sighted_01.py`.

**Risk assessment:**
- Rischio engine audio: BASSO — il menu invoca `send_order` esistente,
  stessa pipeline di `cmd_validate`. Nessun tocco a `worldorders.py`,
  `worldunit.py` o `voice`.
- Rischio NVDA / screen reader: BASSO — nessun `print()`; eventuali
  errori finiscono in `[SOUNDRTS-VISUAL][ERROR]` su `sys.stderr`.
- Reversibilita: ✅ — il menu si auto-disattiva con
  `display_is_active == False` (vedi `display()` L397) e con
  `is_paused`.

#### GAP-02: Selezione Unita a Mouse — ALREADY-DONE

**Problema:** voce del prompt che si ipotizzava aperta.

**Impatto:** nessuno — feature gia presente.

**Strategia proposta:** SKIP. La verifica sul sorgente
(`soundrts/clientgame.py` L985-1051) mostra che:
- `MOUSEBUTTONDOWN button==1` salva `mouse_select_origin = e.pos`.
- `MOUSEBUTTONUP button==1`:
  - se `mouse_select_origin == e.pos` e c'e un oggetto sotto il
    cursore → `cmd_command_unit()` (seleziona singola unita).
  - se diverso → `units_from_mouserect()` → `self.group = [...]` →
    `say_group()`.

Il TTS audio viene gia notificato via `say_group()` / `command_unit()`,
quindi nessuna regressione audio possibile.

**Complessita:** n/a — non viene implementato.

**Risk assessment:** n/a.

#### GAP-03: Rubber-band Selection — ALREADY-DONE

**Problema:** voce del prompt che si ipotizzava aperta.

**Impatto:** nessuno — feature gia presente come parte del flusso
`mouse_select_origin` descritto in GAP-02. NOTA: il rendering del
rettangolo durante il drag non e presente (drag "cieco"); il
giocatore vede solo l'esito finale. Questo e un **miglioramento UX
incrementale** ma non un gap critico (l'azione resta funzionante e
verbalizzata via TTS).

**Strategia proposta:** SKIP del task implementativo. Documentato
come gap minore in "Strategie NON implementate". Sara ripreso in
UI-SIGHTED-02 se l'utenza riportera che il drag senza outline e
poco scopribile.

#### GAP-04: Feedback Visivo Ordini Aggiuntivi

**Problema:** solo il `cmd_default` produce un flash visivo
(verde, `flash_move_target` L1126). Gli ordini eseguiti dal nuovo
context menu (SI-01) non hanno alcun feedback visivo immediato,
solo conferma audio.

**Impatto:** UX-GAP medio. Il normovedente clicca "attack" nel menu
e non ha conferma istantanea che l'ordine sia partito.

**Strategia proposta:** estendere `HudPanel` con dizionario
`_order_flashes: Dict[str, OrderFlash]` (analogo a `_move_flash_*`)
e metodo pubblico `flash_order(kind, pos)` con colori per kind:
- attack → (200, 80, 80)
- stop → (220, 220, 220)
- patrol → (220, 200, 80)
- altri → nessun flash (gestito da ACTIVITY panel).

**Complessita:** BASSA — circa 60 righe in `clientgamehud.py`,
hook in SI-01 `handle_context_menu_event`.

**File impattati:** `soundrts/clientgamehud.py`,
`soundrts/tests/unittests/test_ui_sighted_01.py`.

**Risk assessment:** BASSO. Stessa pipeline di `_draw_move_flash`,
nessuna allocazione persistente, decadimento temporale.

#### GAP-05: Differenziazione Alleati/Nemici — PARZIALE

**Problema:** verificato in `soundrts/clientgamegridview.py` L198-208:
il cerchio centrale colora per relazione (verde gruppo, verde scuro
proprio, blu alleato, rosso nemico, grigio neutro). Funziona ma il
canale e fine (12-15 px di diametro): difficile distinguere a colpo
d'occhio su mappe affollate.

**Impatto:** UX-GAP basso. La differenziazione esiste ma e poco
prominente.

**Strategia proposta:** rimandato a UI-SIGHTED-02. Possibile soluzione:
bordo colorato attorno allo sprite (analogo al P1-UNIT-SELECTION) con
palette per relazione.

#### GAP-06: Stack Indicator Unita per Cella

**Problema:** se in una cella ci sono N unita sovrapposte, il
giocatore non sa quante sono.

**Impatto:** UX-GAP basso. La conta e accessibile via TTS gruppo
ma non visivamente.

**Strategia proposta:** rimandato a UI-SIGHTED-02.

#### GAP-07: Legenda Hotkey Visiva

**Problema:** nessun overlay visivo che mostra le hotkey
disponibili.

**Impatto:** UX-GAP medio in onboarding.

**Strategia proposta:** rimandato a UI-SIGHTED-02. Possibile
soluzione: overlay attivabile con tasto F1 leggendo
`res/ui/bindings`.

#### GAP-08: Cursor Contestuale

**Problema:** verifica sorgente — `set_cursor("target"|"square"|"diamond"|"tri_left")`
gia presente in `clientgame.py` L971-984. Il cursore cambia in base
a target/ordine. Quindi **PARZIALE** non ASSENTE.

**Impatto:** copertura completa per ordini con target. Nessuna
azione necessaria in questo round.

### Roadmap di Implementazione

| Priorita | Gap | Task | File | Righe stimate |
|----------|-----|------|------|---------------|
| ALTA | GAP-01 | SI-01 Context menu | clientgame.py + clientgamehud.py + clientgamegridview.py | ~285 |
| MEDIA | GAP-04 | SI-04 Flash ordini | clientgamehud.py | ~60 |
| n/a | GAP-02 | SI-02 ALREADY-DONE | — | 0 |
| n/a | GAP-03 | SI-03 SKIP (parziale) | — | 0 |

### Architettura Context Menu (GAP-01 — Dettaglio)

**Struttura dati definitiva** (verificata su sorgente):

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

@dataclass
class ContextMenuItem:
    label_key: str        # chiave in style.txt [hud], es. "ctx_attack"
    label_default: str    # fallback inglese, es. "Attack"
    keyword: str          # OrderTypeView.encode
    needs_target: bool    # True se nb_args > 0
    args: list = field(default_factory=list)
    enabled: bool = True

@dataclass
class ContextMenu:
    pos: tuple            # (x, y) schermo
    items: List[ContextMenuItem]
    unit: Any = None
    selected_idx: int = 0
```

**Flusso eventi**

```
1. MOUSEBUTTONDOWN button==3 su pos
   |- gridview.entity_at_mousepos(pos) -> entity
   |- if entity != None and entity.player is interface.player:
   |     hud.show_context_menu(entity, pos)
   |     return  (NON eseguire cmd_default)
   |- else:
         cmd_default(*args)            (comportamento esistente)
         flash_move_target(...)

2. handle_mouse_event(event) (HUD-side)
   |- if _context_menu is not None:
   |     consumed = handle_context_menu_event(event)
   |     if consumed: return True
   |- (logica esistente HUD)

3. handle_context_menu_event(event)
   |- MOUSEMOTION su voce -> selected_idx update -> False
   |- MOUSEBUTTONDOWN button==1 su voce:
   |     if needs_target:
   |        interface._select_order(view)    (utente conferma con click)
   |     else:
   |        interface.send_order(keyword, None, [])
   |        hud.flash_order(keyword, pos)     (hook SI-04)
   |     hide_context_menu(); return True
   |- MOUSEBUTTONDOWN button==1 fuori menu -> hide; return False
   |- KEYDOWN ESC -> hide; return True

4. display() (HUD)
   |- _draw_snapshot(...)
   |- _draw_move_flash(...)
   |- _draw_order_flashes(...)     (nuovo SI-04)
   |- _draw_tooltip(...)
   |- if _context_menu is not None: _draw_context_menu(screen)
```

**Punto di inserimento nel codice**

- `soundrts/clientgame.py` linea 997 (handler `button == 3`):
  prima di `cmd_default`, probe `entity_at_mousepos` e bivio menu/move.
- `soundrts/clientgamehud.py` (nuovo blocco dopo `_draw_move_flash`):
  dataclass `ContextMenuItem` + `ContextMenu`, attributo
  `self._context_menu`, metodi `show_context_menu`,
  `hide_context_menu`, `_draw_context_menu`,
  `handle_context_menu_event`. Hook in `handle_mouse_event`
  (early-return) e in `display()` (draw finale).
- `soundrts/clientgamegridview.py` (nuovo metodo dopo
  `object_from_mousepos` L352): `entity_at_mousepos(pos)`.

**Ordini esposti nel menu** (filtrati da `interface.orders()`):

Il menu mostra tutti gli `OrderTypeView` restituiti da
`self.orders()` per il gruppo selezionato. Il filtro per voce
abilitata/disabilitata e nativo: `self.orders()` restituisce gia
solo gli ordini validi per il `strict_menu` dell'unita.

Lista keyword tipiche derivate da `soundrts/worldorders.py` (lettura
intestazioni):
`move`, `attack`, `stop`, `patrol`, `build`, `train`, `research`,
`cancel_training`, `cancel_upgrading`, `cancel_building`,
`join_group`, `reset_group`.

### Strategie NON Implementate in Questo Round

- **GAP-03 (rubber-band outline visivo durante drag):** la
  funzionalita base e gia presente; manca solo il feedback visivo
  durante il trascinamento. Rimandato a UI-SIGHTED-02.
  → **STATUS UI-SIGHTED-02: ✅ COMPLETATO (SI-03b)** — overlay verde
  semi-trasparente via `GridView.draw_rubber_band`.
- **GAP-05 (bordo colorato per relazione):** rimandato.
- **GAP-06 (stack indicator):** rimandato.
  → **STATUS UI-SIGHTED-02: ✅ COMPLETATO (SI-05)** — badge numerico
  18×14 px via `GridView._draw_stack_badge`, mostrato per celle con
  > 1 unità.
- **GAP-07 (legenda hotkey overlay):** rimandato.
  → **STATUS UI-SIGHTED-02: ✅ COMPLETATO (SI-06)** — pannello HUD
  `KEYS` collassabile (default chiuso), 8 hotkey RTS canoniche,
  header cliccabile per toggle.
- **GAP-08 (cursor contestuale esteso):** copertura attuale gia
  sufficiente.
  → **STATUS UI-SIGHTED-02: ✅ COMPLETATO (SI-07)** — nuovo cursore
  custom `attack` (crosshair) attivato su hover di entità nemiche
  via `GridView.enemy_at_mousepos`.

### Criteri di Accettazione per Release

- [ ] SI-01: right-click su unita propria apre menu; click su voce
  esegue / seleziona ordine; ESC chiude; click fuori chiude.
- [ ] SI-01: right-click su cella vuota o nemico mantiene
  `cmd_default` (regressione zero).
- [ ] SI-04: flash ordini attack/stop/patrol visibili dopo
  esecuzione da menu.
- [ ] SI-01: menu non appare con `display_is_active == False` o
  `is_paused == True`.
- [ ] LEGGE-4: tutte le label del menu via `_hud_text(key, default)`.
- [ ] LEGGE-5: graceful degradation con try/except + log stderr.
- [ ] Suite pytest: 0 failed, baseline preservato (473+).
- [ ] Almeno 4 test SI-01 + 2 test SI-04 in
  `soundrts/tests/unittests/test_ui_sighted_01.py`.
- [ ] `CHANGELOG.md` e `doc_admin/todo.md` aggiornati.
