---
spark: true
name: spark-update-manifests
description: Skill per eseguire update_manifests.py. Descrive quando usarla,
  parametri CLI disponibili, output atteso e come interpretare i log stderr.
scf_owner: "spark-ops"
scf_file_role: "skill"
scf_version: "1.6.0"
scf_merge_strategy: "replace"
scf_merge_priority: 15
scf_protected: false
---

# Skill: spark-update-manifests

## Quando usarla

Usa questa skill quando devi aggiornare i `package-manifest.json` dei
pacchetti SPARK in `packages/` prima di sincronizzarli verso i repo plugin
esterni. Applicala tipicamente come primo step del ciclo di release.

Prerequisito obbligatorio: `scripts/sync_config.json` deve essere presente.
Il campo `local_path` non è richiesto per questa skill.

---

## Parametri CLI

```bash
python scripts/update_manifests.py [opzioni]

--packages PKG1,PKG2   Elabora solo i pacchetti elencati (virgola-separati).
                       Ometti per processare tutti gli abilitati in sync_config.json.
--bump patch|minor|major
                       Tipo di incremento SemVer (default: patch).
--version X.Y.Z        Versione esatta da impostare. Bypassa --bump.
--dry-run              Simula senza scrivere su disco.
```

---

## Output atteso

Lo script non produce nessun output su stdout.
Tutti i messaggi appaiono su `stderr` con il formato:

```
[SPARK-ENGINE][INFO] [spark-base] Versione: 1.2.3 → 1.2.4
[SPARK-ENGINE][INFO] [spark-base] Entry files_metadata aggiornate: 12
[SPARK-ENGINE][INFO] [spark-base] Manifest scritto: .../packages/spark-base/package-manifest.json
[SPARK-ENGINE][INFO] Completato con successo. Pacchetti processati: 3.
```

In caso di errore:

```
[SPARK-ENGINE][ERROR] [spark-base] Manifest non trovato: ...
[SPARK-ENGINE][ERROR] Completato con 1 errori su 3 pacchetti.
```

---

## Come interpretare i log

- `[INFO]` — operazione normale, tutto procede.
- `[WARNING]` — file dichiarato nel manifest non trovato su disco; lo script
  continua ma il file sarà marcato come mancante.
- `[ERROR]` — errore bloccante per il pacchetto corrente; lo script continua
  con gli altri pacchetti ma restituisce exit code 1 al termine.

---

## Verifica post-esecuzione

Dopo l'esecuzione (senza `--dry-run`), verifica che:

1. Il campo `"version"` in `package-manifest.json` sia aumentato.
2. Il campo `"updated_at"` contenga il timestamp UTC dell'esecuzione.
3. Ogni entry in `"files_metadata"` abbia `"scf_version"` allineato
   alla nuova versione.
4. Le entry aggiornate abbiano un campo `"sha256"` con hash del file
   fisico corrispondente.

---

## Riferimenti

- Script: `scripts/update_manifests.py`
- Configurazione: `scripts/sync_config.json`
- Skill coordinatrice: `spark-release-packages`
