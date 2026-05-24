# Round 9 - Debito Tecnico (Obiettivo A)

Data: 2026-05-25

## A0.1 Occorrenze deprecate locale.* in resource.py

File analizzato: soundrts/lib/resource.py

- Linea 83: `locale.getdefaultlocale()[0]`
  - Stato: DEPRECATO su Python 3.12
  - Impatto: con `DeprecationWarning` trattato come errore, interrompe la collection test

Non risultano altre chiamate deprecate `locale.*` nello stesso file.

## A0.2 Filtri in pytest.ini (stato iniziale)

File analizzato: pytest.ini

- `error`
  - Motivazione: policy progetto (tutti i warning come errori)
- `ignore:.*importlib.*:DeprecationWarning`
  - Motivazione: compatibilita con warning di importlib (dipendenza/runtime esterno)
- `ignore:Use setlocale.*:DeprecationWarning`
  - Motivazione: workaround temporaneo Round 8 per mascherare `locale.getdefaultlocale()`
  - Azione prevista: RIMUOVERE in A2 dopo fix sorgente

## A0.3 Baseline-A (suite completa)

Comando:

`.venv\Scripts\python.exe -m pytest > suite_pre_A.log 2>&1`

Risultato baseline-A:

- passed: 187
- failed: 45
- errors: 9

Riferimento: `suite_pre_A.log` (tail confermato)

## A0.4 Test impattati dal DeprecationWarning di getdefaultlocale

Quando il filtro temporaneo e rimosso, la suite si interrompe in collection con 17 errori (storico run strict locale).

Moduli test impattati:

- soundrts/tests/test_autorepair.py
- soundrts/tests/test_cache.py
- soundrts/tests/test_clientserver.py
- soundrts/tests/test_clientservermenu.py
- soundrts/tests/test_cyclic_map.py
- soundrts/tests/test_map.py
- soundrts/tests/test_order.py
- soundrts/tests/test_perception.py
- soundrts/tests/test_serverclient.py
- soundrts/tests/test_serverroom.py
- soundrts/tests/test_world.py
- soundrts/tests/test_worldclient.py
- soundrts/tests/test_worldplayer.py
- soundrts/tests/test_worldplayercomputer.py
- soundrts/tests/unittests/test_clientmenu.py
- soundrts/tests/unittests/test_resource.py
- soundrts/tests/unittests/test_world.py

Tipo errore: `DeprecationWarning: Use setlocale(), getencoding() and getlocale() instead` durante import di `soundrts/lib/resource.py`.

## A0.5 Altri warning di progetto rilevati

Dai log strict emergono warning nel codice progetto non esterno:

- `ResourceWarning` in `soundrts/config.py`:
  - linea 72: `c.write(open(name, "w"))` (file non chiuso)
  - linea 106: `c.read_file(open(name))` (file non chiuso)
- `ResourceWarning` in `soundrts/lib/resource.py`:
  - linea 297: `Map.load(official.open_binary(n), n)` (stream non chiuso)
  - linea 309: `Map.load(multi.open_binary(n), n)` (stream non chiuso)
- Potenziale ulteriore warning in `soundrts/mapfile.py`:
  - linea 55: `f = open(path, ...)` senza context manager

Decisione: correggere anche questi warning nel codice progetto durante A1/A2 (no workaround in pytest.ini).

## A0.6 Strategia di correzione

1. Sostituire in `resource.py`:
   - `locale.getdefaultlocale()[0]`
   - con `lang, _ = locale.getlocale()` + fallback esplicito `"en"` quando `lang` e nullo/errore.
2. Correggere chiusura file nel codice progetto:
   - `config.py`: usare `with open(...)` in `save()` e `load()`
   - `resource.py`: usare `with ...open_binary(...) as f` nei punti map loading
   - `mapfile.py`: usare `with open(...) as f` in `_init_from_path`.
3. Rimuovere filtro temporaneo in `pytest.ini`:
   - `ignore:Use setlocale.*:DeprecationWarning`
4. Mantenere solo filtri giustificati esterni (importlib) con commento inline.

## A0.7 Stima impatto sulla suite

- Effetto certo: eliminazione dei 17 errori di collection legati a deprecazione locale quando il workaround viene rimosso.
- Effetto probabile: riduzione di una quota dei 45 failed/9 errors causati da `ResourceWarning`/`PytestUnraisableExceptionWarning` (dipende dalla copertura dei path corretti).
- Vincolo hard: `passed` non deve scendere sotto 187 (LEGGE-6).

## Criteri di convalida fase A

- `py_compile` OK sui file toccati.
- Import di `soundrts.lib.resource` con `DeprecationWarning` trattati come errore: PASS.
- `pytest.ini` senza filtro locale temporaneo.
- Suite post-A (`suite_post_A.log`):
  - passed >= 187
  - nessun nuovo errore di collection
  - failed non aumentati rispetto a baseline-A
  - preferibile riduzione failed/errors grazie alla correzione warning file handle.
