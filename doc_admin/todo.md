# SoundRTS HUD Extension - Todo coordinatore

Data: 23 maggio 2026

## Stato fasi

### [x] Fase 0 - Analisi totale

Obiettivo: leggere proposta, moduli `soundrts/`, configurazione root e test disponibili.
File coinvolti: `doc_admin/proposta-soundrts-hud-strategy.md`, `soundrts/**`, `test_*.py`, `pytest.ini`, `mypy.ini`, `setup.py`, `.pre-commit-config.yaml`, `requirements.txt`.
Criterio di convalida: mappa tecnica prodotta e gap del primo passaggio colmati.

### [x] Fase 1 - Validazione e piano tecnico

Obiettivo: confrontare proposta e codice reale, definire architettura HUD.
File coinvolti: `doc_admin/piano-tecnico-hud.md`.
Criterio di convalida: piano tecnico creato con file creati/modificati/non toccati e fasi operative.

### [x] Fase 2 - TODO coordinatore

Obiettivo: creare e mantenere il coordinatore operativo.
File coinvolti: `doc_admin/todo.md`.
Criterio di convalida: file presente e aggiornato a ogni transizione.

### [x] Fase 3 - Implementazione HUD

Obiettivo: implementare HUD visuale separata e integrarla nel client visivo.
File coinvolti: `soundrts/clientgamehud.py`, `soundrts/clientgame.py`.
Criterio di convalida: import validi, nessun ciclo, HUD no-op senza display attivo, `clientgamegridview.py` invariato.

Esito: implementati `HudPanel`, hook in `GameInterface`, esclusione da pickle e test unitari mirati.

### [x] Fase 4 - Revisione finale

Obiettivo: revisione strutturale, funzionale e regressione audio.
File coinvolti: file modificati e test rilevanti.
Criterio di convalida: nessuna dipendenza circolare, nessun path audio alterato, test mirati superati.

Esito: nessun errore Pylance sui file modificati, compile completo del pacchetto riuscito, nessuna modifica a `clientgamegridview.py`.

### [x] Fase 5 - Test

Obiettivo: aggiungere test per i nuovi componenti ed eseguire suite disponibile.
File coinvolti: `soundrts/tests/unittests/test_clientgamehud.py` e test esistenti.
Criterio di convalida: test HUD e suite disponibile passano, oppure report diagnostico in `doc_admin/`.

Esito: test HUD passati; suite piu ampia bloccata da warning preesistente Python 3.12 documentato in `doc_admin/ANOMALIA-TEST-2026-05-23.md`.

### [x] Fase 6 - Documentazione e chiusura

Obiettivo: aggiornare documentazione, changelog e stato finale.
File coinvolti: `README.txt`, `CHANGELOG.md`, `doc_admin/todo.md`.
Criterio di convalida: documentazione aggiornata, changelog in `[Unreleased]`, tutte le fasi marcate completate.

Esito: aggiornati `README.txt`, `CHANGELOG.md` e questo coordinatore.

## Anomalie e fallback

- Suite pytest ampia bloccata in Python 3.12 da `locale.getdefaultlocale()` trattato come errore via `filterwarnings = error`; fallback documentato in `doc_admin/ANOMALIA-TEST-2026-05-23.md`.

## Log decisioni autonome

- 2026-05-23: confermata implementazione come overlay Pygame in `GameInterface.display()`, senza modificare `clientgamegridview.py`.
- 2026-05-23: scelto `srv_event(o, e)` come fonte del feed eventi per evitare hook nei sistemi audio o world.
- 2026-05-23: deciso di escludere `hud_panel` dalla serializzazione di `GameInterface` e ricrearlo in `__setstate__`.
- 2026-05-23: deciso di non modificare `.github/**` per documentazione Spark, perche `framework_edit_mode: false` blocca scritture framework.
- 2026-05-23: installati `pytest` e `pygame` nella `.venv` per eseguire i test dichiarati dal progetto.
- 2026-05-23: non eseguito bump release; la modifica resta documentata in `[Unreleased]`.
