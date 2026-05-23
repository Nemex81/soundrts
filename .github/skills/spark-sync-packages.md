---
spark: true
name: spark-sync-packages
description: Skill per eseguire sync_packages.py. Include prerequisito esplicito
  su local_path e descrizione del comportamento di diff e commit.
scf_owner: "spark-ops"
scf_file_role: "skill"
scf_version: "1.6.0"
scf_merge_strategy: "replace"
scf_merge_priority: 15
scf_protected: false
---

# Skill: spark-sync-packages

## Quando usarla

Usa questa skill quando devi propagare i file aggiornati da `packages/{pkg}/`
verso le cartelle locali dei repo plugin, seguita da git commit e push.
Applicala tipicamente come secondo step del ciclo di release, dopo
`spark-update-manifests`.

---

## Prerequisiti obbligatori

Prima di eseguire lo script, verifica che:

1. `scripts/sync_config.json` esista e sia JSON valido.
2. Il campo `"local_path"` di ogni pacchetto da sincronizzare sia compilato
   con il percorso assoluto della cartella locale del repo plugin.
   Se `local_path` è vuoto, lo script logga un WARNING e salta il pacchetto.
3. Il repo plugin locale sia in uno stato git pulito (nessun conflitto aperto).
4. Le credenziali git abbiano i permessi di push su `origin/{remote_branch}`.

---

## Parametri CLI

```bash
python scripts/sync_packages.py [opzioni]

--packages PKG1,PKG2   Elabora solo i pacchetti elencati (virgola-separati).
                       Ometti per processare tutti gli abilitati.
--dry-run              Calcola il diff ma non copia né esegue git.
--no-push              Esegue add e commit ma non push.
```

---

## Comportamento

- Calcola il diff per SHA-256 tra `packages/{pkg}/` e `{local_path}/`.
- Copia solo i file modificati o nuovi.
- Non cancella mai file presenti in `local_path` ma assenti nel repo engine.
- Se nessun file è cambiato, logga INFO e non esegue commit.
- Esegue `git add .`, `git commit -m "sync: ..."`, `git push origin {branch}`.
- Se il push fallisce, logga ERROR con l'output completo di git ma continua
  con gli altri pacchetti.

---

## Output atteso

Lo script non produce nessun output su stdout.
Tutti i messaggi appaiono su `stderr`:

```
[SPARK-ENGINE][INFO] [spark-base] File da sincronizzare: 3
[SPARK-ENGINE][INFO] [spark-base]   → .github/agents/spark-assistant.agent.md
[SPARK-ENGINE][INFO] [spark-base] Copiato: .github/agents/spark-assistant.agent.md
[SPARK-ENGINE][INFO] [spark-base] Commit eseguito: sync: spark-base aggiornato da spark-engine [2026-05-20T...]
[SPARK-ENGINE][INFO] [spark-base] Push completato su origin/main.
```

Se `local_path` non è configurato:

```
[SPARK-ENGINE][WARNING] [spark-base] local_path non configurato.
  Compila il campo 'local_path' in scripts/sync_config.json ...
```

---

## Compilare sync_config.json

Edita `scripts/sync_config.json` e imposta `local_path` per ogni pacchetto:

```json
{
  "packages": {
    "spark-base": {
      "local_path": "C:/Users/Nemex/projects/spark-base",
      "remote_branch": "main",
      "enabled": true
    }
  }
}
```

Per un esempio completo vedi `scripts/sync_config.example.json`.

---

## Riferimenti

- Script: `scripts/sync_packages.py`
- Configurazione: `scripts/sync_config.json`
- Esempio configurazione: `scripts/sync_config.example.json`
- Skill precedente: `spark-update-manifests`
- Skill coordinatrice: `spark-release-packages`
