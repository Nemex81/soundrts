---
description: Pipeline completa di release pacchetti SPARK. Controlla i prerequisiti,
  esegue update_manifests poi sync_packages e verifica il riepilogo finale.
scf_protected: false
scf_file_role: "prompt"
name: release-packages
scf_merge_priority: 15
scf_merge_strategy: "replace"
scf_version: "1.6.0"
type: prompt
spark: true
scf_owner: "spark-ops"
---

# Release Packages

Obiettivo: eseguire la pipeline completa di release dei pacchetti SPARK:
aggiornamento manifest + sincronizzazione verso i repo plugin.

Regola obbligatoria: non avviare la pipeline senza aver verificato i prerequisiti.

Istruzioni operative:

**Step 0 — Controllo prerequisiti:**

1. Verifica che `scripts/sync_config.json` esista.
2. Per ogni pacchetto abilitato, controlla che `local_path` non sia vuoto.
3. Verifica che i repo plugin locali siano in stato git pulito.
4. Se uno qualsiasi dei controlli fallisce, comunica il problema e interrompi.
   Non procedere finché i prerequisiti non sono soddisfatti.

**Step 1 — Esecuzione pipeline:**

1. Chiedi all'utente il tipo di bump desiderato (default: patch) e
   l'eventuale lista di pacchetti specifici.
2. Esegui in dry-run per revisione:
   `python scripts/release_packages.py --dry-run`
3. Mostra il log stderr all'utente e chiedi conferma esplicita.
4. Se confermato, esegui la pipeline reale:
   `python scripts/release_packages.py [--packages ...] [--bump ...] [--no-push]`

**Step 2 — Lettura riepilogo:**

1. Cerca nel log la sezione `=== RIEPILOGO PIPELINE ===`.
2. Verifica che entrambi gli step riportino "SUCCESSO".
3. Se `update_manifests` ha fallito: riporta il log e interrompi.
4. Se `sync_packages` ha fallito: riporta i pacchetti con push fallito
   e suggerisci di eseguire manualmente `git push` nel repo interessato.

**Step 3 — Verifica push:**

1. Per ogni pacchetto sincronizzato con successo, verifica nel log
   la presenza di "Push completato su origin/{branch}".
2. Se richiesto dall'utente, fornisci il comando di verifica:
   `git -C {local_path} log origin/main --oneline -3`

Formato risposta:
- Sezione `Prerequisiti`: stato di ogni pacchetto e local_path.
- Sezione `Dry-run`: riepilogo delle modifiche pianificate.
- Sezione `Risultato pipeline`: update_manifests e sync_packages SUCCESSO/FALLITO.
- Sezione `Verifica push`: conferma o errori per ogni repo plugin.
- Se errori: log completo e azioni correttive suggerite.
