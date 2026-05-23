# SoundRTS HUD Extension - Piano tecnico

Data: 23 maggio 2026
Stato: VALIDATO

## Validazione della proposta

La proposta strategica e confermata con ottimizzazioni implementative.

Il codice reale mostra che il client visivo e gia centralizzato in `GameInterface.display()` e che `GridView` disegna sul canvas Pygame condiviso. Non serve creare un nuovo client, ne un bus dati separato: la HUD puo leggere in sola lettura lo stato gia esposto da `GameInterface`, nello stesso modo in cui lo fa la griglia tattica.

Ottimizzazioni rispetto alla proposta:

- La HUD sara un overlay sul canvas Pygame esistente, non un layer o layout separato.
- Il punto di innesto e `GameInterface.display()`, dopo `grid_view.display()` e prima di `pygame.display.flip()`.
- Il feed eventi usera `GameInterface.srv_event(o, e)`, che riceve gia gli eventi gameplay locali.
- Il pannello HUD sara escluso dalla serializzazione di `GameInterface` e ricreato al restore.
- La HUD non renderizzera su display troppo piccoli, per non interferire con la finestra dev 200x200.

## Architettura tecnica

### Nuovo componente

` soundrts/clientgamehud.py ` contiene un componente autonomo `HudPanel`.

Responsabilita:

- raccogliere uno snapshot leggibile dei dati esposti da `GameInterface`;
- mantenere un buffer limitato degli eventi recenti;
- disegnare pannelli testuali minimali su Pygame;
- restare silente se il display non e attivo o se la superficie e troppo piccola.

Dipendenze ammesse:

- `pygame`, gia presente nel progetto;
- `soundrts.lib.screen` per il rendering testuale esistente;
- tipi standard (`dataclasses`, `collections.deque`, typing).

Dipendenze vietate:

- nessun import da `clientgame.py`;
- nessun import o chiamata a `voice.*`, `tts.*`, `sound.*`;
- nessuna dipendenza da moduli world/server/network.

### Modifiche a `soundrts/clientgame.py`

Interventi minimi:

1. importare `HudPanel`;
2. creare `self.hud_panel` in `GameInterface.__init__`;
3. escludere `hud_panel` da `__getstate__`;
4. ricreare `hud_panel` in `__setstate__`;
5. notificare gli eventi a `hud_panel` in `srv_event()`;
6. disegnare `hud_panel` in `display()` dopo `grid_view.display()`.

### Dati visualizzati

- Risorse: `GameInterface.resources`.
- Popolazione: `used_food / available_food`.
- Tempo: `last_virtual_time`.
- Velocita: `_get_relative_speed()` se disponibile.
- Gruppo selezionato: `group` + `dobjets`.
- Unita selezionate: titolo breve, HP, ordine o attivita corrente.
- Eventi recenti: eventi ricevuti da `srv_event()`.

## File creati

- `soundrts/clientgamehud.py`: componente HUD.
- `soundrts/tests/unittests/test_clientgamehud.py`: test unitari dello snapshot e del buffer eventi.
- `doc_admin/piano-tecnico-hud.md`: questo piano.
- `doc_admin/todo.md`: coordinatore operativo.
- `CHANGELOG.md`: creato se assente, con voce [Unreleased].

## File modificati

- `soundrts/clientgame.py`: integrazione minima della HUD nel client visivo.
- `README.txt`: nota documentale sintetica sulla nuova HUD visuale, se necessaria.
- `doc_admin/todo.md`: aggiornato a ogni fase.

## File non toccati

- `soundrts/clientgamegridview.py`: la griglia resta invariata; la HUD e overlay.
- `soundrts/world.py`: world state e tick deterministico fuori perimetro.
- `soundrts/worldunit.py`: simulazione core unita fuori perimetro.
- `soundrts/worldorders.py`: sistema ordini deterministico fuori perimetro.
- `soundrts/worldclient.py`, `clientserver.py`, `serverclient.py`, `serverroom.py`: networking/sincronizzazione fuori perimetro.
- `soundrts/lib/voice.py`, `voicechannel.py`, `tts.py`, `sound.py`: audio e sintesi vocale invariati.
- `.github/**`: framework SPARK protetto da `framework_edit_mode: false`.

## Piano di implementazione

### Fase 1 - Documenti operativi

Obiettivo: creare piano tecnico e todo coordinatore.
Convalida: file presenti, coerenti con analisi Fase 0.

### Fase 2 - Componente HUD isolato

Obiettivo: implementare `HudPanel` e snapshot testabile.
Convalida: import isolato, nessuna dipendenza circolare, test unitari su snapshot/eventi.

### Fase 3 - Integrazione minima nel client

Obiettivo: collegare la HUD a `GameInterface` senza alterare audio, world o GridView.
Convalida: compile/import, test client/HUD, nessuna modifica a file vietati.

### Fase 4 - Test e regressione

Obiettivo: eseguire test mirati e suite disponibile.
Convalida: pytest passa o report diagnostico in `doc_admin/`.

### Fase 5 - Documentazione e changelog

Obiettivo: aggiornare documentazione utente e changelog.
Convalida: todo completato e note operative aggiornate.

## Anomalie note

- I tool MCP SPARK non sono esposti in questa sessione; la documentazione SPARK sotto `.github/**` non sara modificata perche `framework_edit_mode: false`.
- Non esisteva un `CHANGELOG.md` nel workspace al momento della pianificazione; verra creato un changelog minimale se confermato assente in fase docs.
