---
spark: true
name: spark-release-packages
description: Skill coordinatrice per release_packages.py. Specifica ordine delle
  operazioni, controlli pre-esecuzione e lettura del riepilogo finale.
scf_owner: "spark-ops"
scf_file_role: "skill"
scf_version: "1.6.0"
scf_merge_strategy: "replace"
scf_merge_priority: 15
scf_protected: false
---

# Skill: spark-release-packages

## Quando usarla

Usa questa skill per eseguire l'intera pipeline di release in un unico comando:
`release_packages.py` invoca `update_manifests.py` poi `sync_packages.py` in
sequenza, con blocco automatico se il primo step fallisce.

Usa questa skill invece di eseguire i due script separatamente quando vuoi
completare l'intero ciclo in modo atomico.

---

## Controlli pre-esecuzione

Prima di lanciare lo script, verifica:

1. `scripts/sync_config.json` esiste ed è JSON valido.
2. `local_path` compilato per tutti i pacchetti da sincronizzare
   (controlla con `spark-sync-packages`).
3. I repo plugin locali sono in stato git pulito.
4. L'ambiente Python ha accesso a `git` nel PATH.

---

## Ordine delle operazioni

```
release_packages.py
  └─ Step 1: update_manifests.py
  │    - Bumpa versione in package-manifest.json
  │    - Ricalcola sha256 per files_metadata
  │    - Aggiorna scf_version e updated_at
  │    - Exit code 0 → procede al Step 2
  │    - Exit code != 0 → STOP, sync_packages non eseguito
  │
  └─ Step 2: sync_packages.py (solo se Step 1 ha successo)
       - Calcola diff SHA-256
       - Copia file modificati/nuovi
       - git add + commit + push
```

---

## Parametri CLI

```bash
python scripts/release_packages.py [opzioni]

--packages PKG1,PKG2   Elabora solo i pacchetti elencati.
--bump patch|minor|major
                       Tipo di incremento SemVer (default: patch).
--version X.Y.Z        Versione esatta (bypassa --bump).
--dry-run              Simula entrambi gli step senza scritture né git.
--no-push              Commit senza push nel repo plugin.
```

---

## Lettura del riepilogo finale

Al termine dello script il log mostra:

```
[SPARK-ENGINE][INFO] === RIEPILOGO PIPELINE ===
[SPARK-ENGINE][INFO] update_manifests: SUCCESSO
[SPARK-ENGINE][INFO] sync_packages:    SUCCESSO
[SPARK-ENGINE][INFO] === PIPELINE COMPLETATA CON SUCCESSO ===
```

In caso di errore in Step 1:

```
[SPARK-ENGINE][ERROR] update_manifests.py ha terminato con errori (exit 1).
                      sync_packages.py non sarà eseguito.
```

In caso di errore in Step 2 (Step 1 ok):

```
[SPARK-ENGINE][INFO] === RIEPILOGO PIPELINE ===
[SPARK-ENGINE][INFO] update_manifests: SUCCESSO
[SPARK-ENGINE][ERROR] sync_packages:    FALLITO (exit 1)
[SPARK-ENGINE][ERROR] Pipeline completata con errori in sync_packages (exit 1).
```

---

## Verifica push sui repo remoti

Dopo un'esecuzione riuscita, verifica che ogni repo plugin remoto abbia
ricevuto il commit:

```bash
# Nel repo plugin locale
git log origin/main --oneline -3
```

Cerca una riga del tipo:
`abc1234 sync: spark-base aggiornato da spark-engine [2026-05-20T...]`

---

## Riferimenti

- Script: `scripts/release_packages.py`
- Script Step 1: `scripts/update_manifests.py`
- Script Step 2: `scripts/sync_packages.py`
- Configurazione: `scripts/sync_config.json`
- Skill Step 1: `spark-update-manifests`
- Skill Step 2: `spark-sync-packages`
- Prompt: `release-packages`
