---
description: Esegui sync_packages.py verso i repo plugin locali, con controllo
  prerequisiti local_path prima di avviare.
scf_protected: false
scf_file_role: "prompt"
name: sync-packages
scf_merge_priority: 15
scf_merge_strategy: "replace"
scf_version: "1.6.0"
type: prompt
spark: true
scf_owner: "spark-ops"
---

# Sync Packages

Obiettivo: sincronizzare i file da `packages/{pkg}/` verso i repo plugin locali
e propagare le modifiche con git commit e push.

Regola obbligatoria: non eseguire la sincronizzazione finché tutti i `local_path`
dei pacchetti target non sono configurati in `sync_config.json`.

Istruzioni operative:

**Step 0 — Controllo prerequisiti:**

1. Leggi `scripts/sync_config.json`.
2. Per ogni pacchetto abilitato, verifica che `local_path` non sia vuoto.
3. Se uno o più `local_path` sono vuoti, comunica all'utente:
   "Il campo 'local_path' per {pacchetto} non è configurato.
   Edita scripts/sync_config.json con il percorso assoluto del repo locale.
   Esempio: C:/Users/Nemex/projects/{pacchetto}"
4. Non procedere al Step 1 finché i prerequisiti non sono soddisfatti.

**Step 1 — Esecuzione in dry-run:**

1. Esegui: `python scripts/sync_packages.py --dry-run`
2. Mostra il log stderr all'utente: file che sarebbero copiati, pacchetti skippati.
3. Chiedi conferma prima di procedere.

**Step 2 — Esecuzione reale:**

1. Se confermato: `python scripts/sync_packages.py [--packages ...] [--no-push]`
2. Monitora il log stderr per `[ERROR]` relativi a git push fallito.
3. Se push fallisce per un pacchetto, segnalalo ma non interrompere gli altri.

Formato risposta:
- Sezione `Prerequisiti`: stato di ogni local_path.
- Sezione `Dry-run`: file che sarebbero sincronizzati per pacchetto.
- Sezione `Risultato`: file copiati, commit eseguiti, push riusciti/falliti.
- Se errori: riporta log completo con suggerimento per il retry.
