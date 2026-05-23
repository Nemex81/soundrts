# SoundRTS — Layout HUD (stato attuale + proposta)

Versione: 2026-05-23
Stato: VALIDATO
Riferimento: `docs/ui-visual-plan.md`

## Coordinate e ancore

L'HUD copre la finestra a partire da risoluzioni ≥ 420×260
(`HudPanel.MIN_WIDTH`, `MIN_HEIGHT`). Le coordinate qui sotto sono
espresse come margini relativi.

## Layout attuale (`HudPanel._draw_snapshot`)

```
+-----------------------------------------------------+
| [RES]                                  [TIME]       |
|  gold 120                               turn 482    |
|  wood 45                                speed x1.0  |
|                                                     |
|                                       [EVENTS]      |
|                                        attack:...   |
|                                        complete:..  |
| [GROUP]                                             |
|  knight x3                                          |
|  peasant x2                                         |
+-----------------------------------------------------+
```

- 4 pannelli rettangolari con sfondo `(0,0,0,165)` e bordo
  `(70,110,120)`.
- Header e testo usano lo stesso font Arial 12 bold.

## Layout proposto (post B1–B6, C1 invisibile)

```
+-----------------------------------------------------+
| ## RES ##                            ## TIME ##     |
|  gold:    120 (giallo brillante)      turn 482      |
|  wood:     45                         > x1.0        |
|                                                     |
|                                      ## EVENTS ##   |
|                                       ! attack:..   |
|                                       + complete:.  |
|                                       * discovered: |
| ## GROUP ##                                         |
|  knight x3                                          |
|  peasant x2                                         |
|                                                     |
| ## PLAYER ## (nuovo B3)                             |
|  Alice (red faction)                                |
+-----------------------------------------------------+
```

### Cambiamenti chiave

1. **Header** (`##  ##`) renderizzati con `screen_render_header`
   (Arial 16 bold) invece di font 12.
2. **Valori RES** evidenziati in giallo brillante `(255,235,130)`.
3. **Icona velocità** prefisso `>`, `>>`, `=` davanti a `x1.0`.
4. **Eventi** prefissi `!`, `+`, `*` con colori dedicati per severity.
5. **Pannello PLAYER** in basso a sinistra sotto GROUP, altezza 30 px,
   nome giocatore.

## Hit-zones (C1 prep)

`HudPanel.handle_mouse_event(event)` ritorna sempre `False` nella
versione iniziale. Le aree dei pannelli sono già conosciute dal HUD
(`self._panel_rects` dict di Rect), quindi un futuro task C2 potrà:

```python
def handle_mouse_event(self, event):
    if event.type != pygame.MOUSEBUTTONDOWN:
        return False
    for name, rect in self._panel_rects.items():
        if rect.collidepoint(event.pos):
            self._on_panel_click(name, event)
            return True
    return False
```

Per ora **non** registriamo callback né popup: il metodo esiste solo per
preparare l'integrazione futura senza richiedere refactoring di
`_process_fullscreen_mode_mouse_event` quando arriverà il momento.

## Vincoli render

- `HudPanel.display()` non deve creare nuove Surface ogni frame.
  Le surface alpha dei pannelli sono già cache-friendly (rect ricalcolato
  solo quando la finestra cambia dimensione).
- Font header e small devono essere creati una sola volta in
  `lib/screen.py` a livello modulo, esattamente come `_font`.
- Tutti i prefissi (`!`, `+`, `*`, `>`, `>>`, `=`) sono ASCII, evitando
  problemi font/codepage.

## Dualità audio/grafico

- `HudPanel.display()` viene chiamato **solo se** `display_is_active`
  è True (cfr `clientgame.display()`).
- In modalità audio (`display_is_active is False`) viene mostrata solo la
  stringa "[Ctrl + F2] display": nessuna nuova allocazione HUD.
- Tutti i nuovi colori sono additivi: il giocatore audio-only non sente
  alcuna differenza perché non c'è hook ai canali sonori.

## Test coverage attesa

| Aspetto | Test esistente | Aggiunta |
|---|---|---|
| Snapshot risorse | `test_hud_snapshot_*` | aggiunta assert su prefisso `>`/`>>` |
| Buffer eventi | `test_hud_event_buffer` | nuova severity classification |
| Player line | — | nuovo test `test_hud_player_line` |
| handle_mouse_event no-op | — | nuovo test `test_hud_handle_mouse_noop` |
