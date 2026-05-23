# Changelog

## [Unreleased]

### Added

- Added a Pygame HUD overlay for active visual displays, showing resources, population, selected group status, game time, speed, and recent gameplay events.
- Added unit tests for HUD snapshot collection and event buffering.
- Added technical planning and validation notes under `doc_admin/` for the HUD extension.

### Changed

- Integrated the HUD into `GameInterface` without changing `GridView`, world simulation, networking, or audio behavior.

### Notes

- Full pytest validation on Python 3.12 is currently blocked by an existing `locale.getdefaultlocale()` deprecation warning treated as an error by `pytest.ini`; see `doc_admin/ANOMALIA-TEST-2026-05-23.md`.
