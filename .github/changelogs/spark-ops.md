---
spark: true
scf_file_role: "config"
scf_version: "1.0.0"
scf_merge_strategy: "replace"
scf_protected: false
scf_owner: "spark-ops"
scf_merge_priority: 15
---

<!-- markdownlint-disable MD024 -->

# Changelog - spark-ops

## [Unreleased]

## [1.6.0] — 2026-05-20

### Added

- `copilot-instructions.md`: acquisito da spark-base; file di configurazione
  istruzioni Copilot per workspace utente.
- `project-profile.md`: acquisito da spark-base; profilo progetto utente
  per contestualizzazione agenti.
- `instructions/framework-guard.instructions.md`: acquisito da spark-base.
- `instructions/git-policy.instructions.md`: acquisito da spark-base.
- `instructions/model-policy.instructions.md`: acquisito da spark-base.
- `instructions/personality.instructions.md`: acquisito da spark-base.
- `instructions/project-reset.instructions.md`: acquisito da spark-base.
- `instructions/spark-assistant-guide.instructions.md`: acquisito da spark-base.
- `instructions/verbosity.instructions.md`: acquisito da spark-base.
- `instructions/workflow-standard.instructions.md`: acquisito da spark-base.
  spark-ops è ora il layer operativo completo per l'interazione utente↔sistema SPARK.
- 36 file aggiuntivi (prompts e skills) precedentemente presenti nel filesystem
  ma non dichiarati nel manifest: allineamento completo `plugin_files`, `files`,
  `files_metadata` al filesystem fisico. Include: `framework-unlock`, `git-commit`,
  `git-merge`, `help`, `init`, `orchestrate`, `personality`, `project-setup`,
  `project-update`, `start`, `status`, `sync-docs`, `verbosity` (prompts) e
  `accessibility-output`, `agent-selector`, `changelog-entry`, `conventional-commit`,
  `document-template`, `error-recovery`, `file-deletion-guard`, `framework-guard`,
  `framework-index`, `framework-query`, `framework-scope-guard`, `git-execution`,
  `personality`, `project-doc-bootstrap`, `project-profile`, `project-reset`,
  `rollback-procedure`, `semver-bump`, `style-setup`, `validate-accessibility`,
  `verbosity` (skills).

### Changed

- `package-manifest.json`: version bump 1.5.0 → 1.6.0; manifest allineato
  al filesystem fisico del package store; `mcp_resources.instructions` popolato
  con 8 instruction names; `mcp_resources.skills` esteso da 2 a 23 entries;
  `mcp_resources.prompts` esteso da 19 a 32 entries.

## [1.4.0] — 2026-05-19

### Added

- Agent-Git: agente git migrato da spark-base v2.2.0
- Agent-Welcome: agente di benvenuto migrato da spark-base v2.2.0

### Removed

- Agent-Release: rimosso per errore di classificazione, ricollocato esclusivamente in spark-base

## [1.3.0] - 2026-05-19

### Added

- `spark-assistant` e `spark-guide` ora forniti da `spark-ops` (spostati da `spark-base`).
- Prompt `package-update` trasferito da `spark-base`: coordina aggiornamento pacchetti SCF.
- Prompt `spark-engine-decoupling-validation` trasferito da `spark-base` come risorsa interna.
- Skill `semantic-gate` promossa da `spark-base` con contenuto completo (gate 1/2/3 + procedure), versione `1.1.0`.
- Skill `task-scope-guard` dichiarata nel manifest (engine-managed stub già presente fisicamente).
- Prompt `framework-changelog`, `framework-release`, `framework-update`, `release` aggiornati a `v1.2.0` con contenuto completo e prerequisiti bloccanti.

### Removed

- `Agent-Orchestrator` spostato in `spark-base` (agente core del ciclo E2E utente).
- Prompt `orchestrate` spostato in `spark-base` (segue Agent-Orchestrator).

## [1.0.0] - 2026-05-10

### Added

- First release of the SPARK operational layer split from `spark-base`.
