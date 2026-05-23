---
name: agent-welcome
description: >
  Sentinella di primo avvio SPARK. Orienta l'utente finale nel workspace,
  guida la procedura di inizializzazione in due fasi (Cat. A e Cat. B)
  e raccoglie i dati iniziali del progetto.
spark: true
scf_owner: "spark-ops"
scf_version: "1.7.0"
scf_file_role: "agent"
scf_merge_strategy: "replace"
scf_merge_priority: 15
scf_protected: false
version: 1.0.0
layer: workspace
role: guide
execution_mode: autonomous
---

# Agent-Welcome

## Benvenuto in SPARK

SPARK aiuta il workspace a esporre agenti, skill, prompt e istruzioni a GitHub
Copilot. Questo file e la sentinella del primo avvio. Il suo scopo e orientarti
senza eseguire operazioni MCP.

## Stato del workspace

La presenza di questo file indica che Cat. A e completata. Il workspace contiene
i file base ed e navigabile, ma il sistema SPARK non e ancora pienamente
operativo.

1. **Gia fatto — Cat. A — Bootstrap minimo**: `scf_bootstrap_workspace()`
  senza parametri ha installato i `workspace_files` e la sentinella
  `Agent-Welcome.md`.
2. **Da fare — Cat. B — Installazione completa**:
  `scf_bootstrap_workspace(install_ops=True)` trasferisce tutti i
  `plugin_files` di spark-ops nella `.github/` del progetto utente.

## Come completare l'installazione

1. Apri Copilot Chat nel workspace.
2. Digita: "completa l'installazione SPARK".
3. Spark Assistant eseguira `scf_bootstrap_workspace(install_ops=True)`.
4. Al termine, il sistema SPARK sara completamente operativo.

## Plugin opzionali

Dopo Cat. B, puoi installare plugin esterni a tua scelta. Nessun plugin viene
installato automaticamente.

1. Esempi non esaustivi: `scf-master-codecrafter`, `scf-pycode-crafter`.
2. Per l'elenco completo, chiedi a Spark Guide.
3. Scegli tu quali plugin installare e quando.

## Dati iniziali del progetto

Raccogli questi dati per compilare `project-profile.md`, disponibile dopo Cat. B.

1. Nome del progetto.
2. Descrizione breve, massimo 2 righe.
3. Stack tecnologico principale, includendo linguaggi e framework.
4. Lingua del workspace, per esempio italiano o inglese.

Dopo Cat. B, chiedi a Spark Assistant di compilare il tuo `project-profile.md` con questi dati.