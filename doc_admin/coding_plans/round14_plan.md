# Round 14 — Plan & Evidence

**Data:** 25 maggio 2026
**Baseline ingresso:** 289 passed / 0 failed / 0 errors / 1 skipped
**Stato finale:** COMPLETATO — 292 passed / 0 failed / 0 errors / 1 skipped

---

## TASK-1 — Revisione madrelingua i18n 4365/4366

### Criterio applicato

- **Struttura attesa:** `chiave: azione. chiave: azione.`
- **Tasti fisici** (`Enter`, `Esc`, `Ctrl+F2`, `Arrow keys`): accettati in
  EN o adattati nella lingua target — entrambi standard internazionale.
- **Azioni** (navigate, confirm, back, cancel, visual off): devono essere
  nella lingua target per alfabeti latini/cirillici.
- **vi/zh:** traduzione automatica accettata come base, revisione nativa
  rimandata a R15.

### Tabella revisione

| Lingua | Token 4365 (estratto) | Token 4366 (estratto) | Stato |
|--------|-----------------------|-----------------------|-------|
| be (Belarusian) | Стрэлкі: навігацыя. Увод: пацвердзіць. Esc: назад. Ctrl+F2: візуальны выкл | Увод: пацвердзіць. Esc: адмена. Ctrl+F2: візуальны выкл | ACCETTABILE |
| cs (Czech) | Šipky: navigace. Enter: potvrdit. Esc: zpět. Ctrl+F2: vizuální vyp | Enter: potvrdit. Esc: zrušit. Ctrl+F2: vizuální vyp | ACCETTABILE |
| de (German) | Pfeiltasten: navigieren. Eingabe: bestätigen. Esc: zurück. Ctrl+F2: visuell aus | Eingabe: bestätigen. Esc: abbrechen. Ctrl+F2: visuell aus | ACCETTABILE |
| es (Spanish) | Flechas: navegar. Intro: confirmar. Esc: volver. Ctrl+F2: visual desactivado | Intro: confirmar. Esc: cancelar. Ctrl+F2: visual desactivado | ACCETTABILE |
| fr (French) | Flèches : naviguer. Entrée : confirmer. Échap : retour. Ctrl+F2 : visuel désactivé | Entrée : confirmer. Échap : annuler. Ctrl+F2 : visuel désactivé | ACCETTABILE |
| pl (Polish) | Strzałki: nawiguj. Enter: potwierdź. Esc: wstecz. Ctrl+F2: wizualny wył | Enter: potwierdź. Esc: anuluj. Ctrl+F2: wizualny wył | ACCETTABILE |
| pt-BR (Portuguese) | Setas: navegar. Enter: confirmar. Esc: voltar. Ctrl+F2: visual desligado | Enter: confirmar. Esc: cancelar. Ctrl+F2: visual desligado | ACCETTABILE |
| ru (Russian) | Стрелки: навигация. Ввод: подтвердить. Esc: назад. Ctrl+F2: визуальный выкл | Ввод: подтвердить. Esc: отмена. Ctrl+F2: визуальный выкл | ACCETTABILE |
| sk (Slovak) | Šípky: navigácia. Enter: potvrdiť. Esc: späť. Ctrl+F2: vizuálny vyp | Enter: potvrdiť. Esc: zrušiť. Ctrl+F2: vizuálny vyp | ACCETTABILE |
| vi (Vietnamese) | Mũi tên: điều hướng. Enter: xác nhận. Esc: quay lại. Ctrl+F2: hình ảnh tắt | Enter: xác nhận. Esc: hủy. Ctrl+F2: hình ảnh tắt | ACCETTABILE (R15 nativa) |
| zh (Chinese) | 方向键 ：导航。回车：确认。Esc：返回。Ctrl+F2：视觉关闭 | 回车： 确认。Esc：取消。Ctrl+F2：视觉关闭 | ACCETTABILE (R15 nativa) |

**Esito:** nessuna correzione applicata. Tutte le righe rispettano la
struttura attesa, contengono i nomi dei tasti fisici riconoscibili e
le azioni nella lingua target (o accettate come base per vi/zh).

I 27 test in `soundrts/tests/unittests/test_i18n_hints.py` (R13)
verificano la **presenza** dei token (`startswith("4365 ")`,
`startswith("4366 ")`), non il contenuto esatto: nessun aggiornamento
necessario.

---

## TASK-2 — Update-check endpoint

### Codice esaminato

`soundrts/clientversion.py` — `RevisionChecker.run()` (Thread daemon).

```python
def run(self):
    try:
        if _patch(VERSION) != -1:
            major_minor = ".".join(VERSION.split(".")[:2])
            url = f"http://jlpo.free.fr/soundrts/{major_minor}version.txt"
            latest_version = urllib.request.urlopen(url).read().strip().decode()
            if "404" not in latest_version and _patch(VERSION) < _patch(latest_version):
                voice.important(mp.UPDATE_AVAILABLE)
    except:
        pass
    ...
```

L'intera richiesta è già avvolta in `try/except` bare che inghiotte
qualsiasi eccezione (HTTPError, URLError, timeout, decode error, ecc.).

### Probe HTTP

```text
URL  : http://jlpo.free.fr/soundrts/1.4version.txt
Esito: HTTP 404 Not Found
```

### Ramo scelto: **RAMO-FILE-MANCANTE-SAFE**

- 404 è gestito silenziosamente: nessun crash, nessun TTS spurio.
- Thread daemon → non blocca lo shutdown del client.
- Rischio residuo: utenti `1.4.x` non ricevono notifica di nuove
  versioni. Tracciato come TODO R15 a bassa priorità.

### SUB-TASK-2A: non necessario

Il codice gestisce già correttamente il caso 404. Nessun fix
richiesto in `clientversion.py`.

### Test difensivi aggiunti

`soundrts/tests/unittests/test_version_check.py` (3 test):

- `test_http_404_does_not_raise` — mock `urllib.request.urlopen`
  con `HTTPError(404)`, verifica che `run()` ritorni normalmente.
- `test_network_timeout_does_not_raise` — mock con `TimeoutError`.
- `test_url_error_does_not_raise` — mock con `URLError`.

Tutti i test mockano anche `stats.Stats` e
`update_packages_from_servers` per isolare il blocco try/except
del version-check dalle chiamate di rete successive.

---

## TASK-3 — Release prep v1.4.3

### Discrepanza R13

R13 aveva bumpato `VERSION = "1.4.2"` ma il CHANGELOG era stato
aperto come `[1.4.3] — 2026-05-25`.

**OPZIONE-A scelta** (allineamento `version.py` → CHANGELOG): meno
invasiva, conferma confermata dall'analisi R13 di
`server_is_compatible()` (confronta `SERVER_COMPATIBILITY="0"`,
non `VERSION` — bump protocol-safe).

### Modifiche

- `soundrts/version.py`: `VERSION = "1.4.2"` → `VERSION = "1.4.3"`
- `CHANGELOG.md` `[1.4.3]`: estesa con voci R14 (test
  `test_version_check.py`, revisione i18n classificata
  ACCETTABILE 11/11, bump finale 1.4.3).
- `README.txt`: nessuna menzione versione, invariato.

### Verifica protocollo

`server_is_compatible()` in `soundrts/version.py`:

```python
def server_is_compatible(version):
    if version in ["1.2-c12", "1.3.0", "1.3.1"]:
        version = "0"
    return version == SERVER_COMPATIBILITY
```

Confronta `version` (parametro) con `SERVER_COMPATIBILITY="0"`,
ignora completamente la costante `VERSION` del modulo. Il bump
`VERSION` non altera la compatibilità di rete.

---

## TODO Round 15 (priorità)

1. **BASSA** — Revisione madrelingua `vi`/`zh` per token 4365/4366.
2. **BASSA** — Pubblicare `1.4version.txt` su `jlpo.free.fr` (o
   configurare endpoint alternativo) per riattivare la notifica
   update agli utenti `1.4.x`.
3. **OPERATORE** — Decidere se taggare `v1.4.3` in git
   (LEGGE-8 R14 ha vietato git autonomo).

---

## Suite

| Fase | Passed | Failed | Errors | Skipped | Log |
|------|--------|--------|--------|---------|-----|
| Baseline ingresso | 289 | 0 | 0 | 1 | (R13) |
| Dopo T2 (nuovi test) | 292 | 0 | 0 | 1 | suite_r14_t2 |
| Dopo T3 (bump version) | 292 | 0 | 0 | 1 | suite_r14_t3 |
| Finale | 292 | 0 | 0 | 1 | suite_r14_c1 |
