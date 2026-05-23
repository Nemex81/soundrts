---
description: Esegui update_manifests.py, verifica i log e conferma le versioni aggiornate.
scf_protected: false
scf_file_role: "prompt"
name: update-manifests
scf_merge_priority: 15
scf_merge_strategy: "replace"
scf_version: "1.6.0"
type: prompt
spark: true
scf_owner: "spark-ops"
---

# Update Manifests

Obiettivo: aggiornare i `package-manifest.json` dei pacchetti SPARK in `packages/`.

Regola obbligatoria: verifica che `scripts/sync_config.json` esista prima di
procedere. Se non esiste, interrompi e comunica all'utente.

Istruzioni operative:

1. Verifica la presenza di `scripts/sync_config.json`.
   Se assente: comunica "sync_config.json non trovato. Crea il file prima di
   procedere (vedi scripts/sync_config.example.json come riferimento)."
2. Chiedi all'utente quali pacchetti elaborare e il tipo di bump
   (default: patch). Se non specificato, usa tutti gli abilitati e patch.
3. Esegui in dry-run per vedere l'output senza modifiche:
   `python scripts/update_manifests.py --dry-run`
4. Mostra all'utente il log stderr e chiedi conferma.
5. Se confermato, esegui senza dry-run:
   `python scripts/update_manifests.py [--packages ...] [--bump ...]`
6. Verifica che l'exit code sia 0 e che il log non contenga `[ERROR]`.
7. Riporta versioni precedenti e nuove per ogni pacchetto elaborato.

Formato risposta:
- Sezione `Pre-check`: stato di sync_config.json.
- Sezione `Dry-run output`: log stderr dell'esecuzione simulata.
- Sezione `Risultato`: versioni aggiornate, eventuali warning su file mancanti.
- Se exit code != 0: riporta il log di errore completo e interrompi.
