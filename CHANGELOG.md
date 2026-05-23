# Changelog

## [Unreleased]

### Added

- Added a Pygame HUD overlay for active visual displays, showing resources, population, selected group status, game time, speed, and recent gameplay events.
- Added unit tests for HUD snapshot collection and event buffering.
- Added technical planning and validation notes under `doc_admin/` for the HUD extension.
- Added a typographic hierarchy to `soundrts.lib.screen` (`screen_render_header`, `screen_render_small`) with safe SysFont fallbacks for systems without Arial.
- Added a `HudEvent` dataclass and severity classification (combat/info/alert) with colour-coded prefixes (`!`, `+`, `*`) in the HUD events panel.
- Added a HUD `PLAYER` panel showing the current player's name and faction when available.
- Added a `HudPanel.handle_mouse_event` no-op hook in `GameInterface._process_fullscreen_mode_mouse_event` to reserve a future hit-test path for clickable HUD widgets without altering current RTS mouse behaviour.
- Added new HUD tests for severity classification, the no-op mouse hook, and the player line fallbacks.
- Added technical planning documents `docs/ui-visual-plan.md`, `docs/ui-color-palette.md`, `docs/ui-hud-layout.md` describing the visual optimisation roadmap for sighted players.

### Changed

- Integrated the HUD into `GameInterface` without changing `GridView`, world simulation, networking, or audio behavior.
- Improved tactical grid readability for sighted players in `clientgamegridview`: differentiated fallback palette for `_meadows`/`_forest`/`_dense_forest`, lighter walls `(230,230,230)`, brighter neutral faction flag `(180,180,180)`, brighter own-faction flag `(60,140,60)`, thicker active-zone border (width 2), and a more visible observer marker (yellow `(255,230,90)`, radius 4, width 2).
- Promoted HUD panel headers (`RES`, `TIME`, `EVENTS`, `GROUP`, `PLAYER`) to a dedicated Arial 16 bold font and highlighted resource values in bright yellow `(255,235,130)`; added a speed icon prefix (`>>`, `>`, `=`).

### Notes

- Full pytest validation on Python 3.12 is currently blocked by an existing `locale.getdefaultlocale()` deprecation warning treated as an error by `pytest.ini`; see `doc_admin/ANOMALIA-TEST-2026-05-23.md`.
