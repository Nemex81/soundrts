# ANOMALIA TEST - 2026-05-23

## Contesto

Durante la validazione della SoundRTS HUD Extension, i test mirati del nuovo componente HUD passano, ma alcuni test client esistenti falliscono gia in fase di collection nell'ambiente Python 3.12 configurato nella `.venv`.

## Comando fallito

```powershell
c:/Users/nemex/OneDrive/Documenti/GitHub/soundrts/.venv/Scripts/python.exe -m pytest soundrts/tests/test_clientserver.py
```

## Errore osservato

`pytest.ini` configura `filterwarnings = error`. Su Python 3.12, l'import di `soundrts.lib.resource` chiama `locale.getdefaultlocale()`, che genera un `DeprecationWarning`:

```text
DeprecationWarning: Use setlocale(), getencoding() and getlocale() instead
```

Poiche i warning sono trattati come errori, la suite si interrompe durante la collection prima di eseguire i test.

## Valutazione

L'anomalia non e introdotta dalla HUD:

- il fallimento avviene importando `soundrts.clientserver` / `soundrts.lib.resource`;
- il nuovo file `soundrts/clientgamehud.py` non importa `resource`, `options`, networking o audio;
- i test specifici della HUD passano;
- la compilazione di tutti i moduli Python sotto `soundrts/` passa.

## Validazioni superate

```powershell
c:/Users/nemex/OneDrive/Documenti/GitHub/soundrts/.venv/Scripts/python.exe -m py_compile <tutti i file .py sotto soundrts>
c:/Users/nemex/OneDrive/Documenti/GitHub/soundrts/.venv/Scripts/python.exe -m pytest soundrts/tests/unittests/test_clientgamehud.py
```

Esito test HUD:

```text
3 passed
```

## Fallback applicato

La suite completa non viene considerata bloccante per questa modifica perche il failure e un problema preesistente di compatibilita Python 3.12 + policy warning-as-error. La correzione corretta andrebbe gestita in un task separato, aggiornando `soundrts/lib/resource.py` o la matrice Python supportata.
