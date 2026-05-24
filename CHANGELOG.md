# Changelog

## [Unreleased]

<!-- UI Fix Round 3 + i18n IT — 2026-05-24 -->

### Fixed

- [FIX-1] Status bar: corrected the runtime fallback path in `screen_subtitle_set()` so non-game-mode subtitle rendering now uses the same bottom-right anchor as `screen_render_subtitle()` (`x = width - text_width - 16`, `y = height - text_height - 4`).

### Changed

- [FIX-2] Further upgraded HUD body font to Arial 20 bold (from 17), header font to 24 bold, and small font to 18 regular for improved fullscreen readability.
- Updated HUD geometry for the larger font: `line_height` 23 → 26 px, `min_height` 308 → 360 px, `time_height` 68 → 88 px, and dynamic panel header space to 36 px.
- Reduced EVENTS text fit length to 23 characters to keep long event labels within the 260 px panel after the font increase.

### Added

- [FIX-3] Added 18 localizable graphical HUD strings through the existing `style.get("hud", ...)` system, with Italian values in `res/ui-it/style.txt` and English base values in `res/ui/style.txt`.
- Added automated Round 3 layout tests for HUD font constants, subtitle bottom-right positioning, and Italian HUD i18n keys.

### Tests

- `test_hud_layout.py`: 34 passed, 0 failed.

<!-- UI Fix Round 2 — 2026-05-24 -->

### Fixed

- [FIX-C] TIME panel height raised from 60 to 68 px, eliminating the critical 1 px bottom margin that caused text descender clipping on some systems.
- [FIX-B] Status bar (`screen_render_subtitle`) repositioned from horizontal center to bottom-right anchor (`x = width - text_width - 16`, `y = height - text_height - 4`), eliminating overlap with the game map.
- Fixed a critical overlap between the RES and EVENTS HUD panels at 420×260 resolution by raising `HudPanel.min_width` from 420 to 460 and `HudPanel.min_height` from 260 to 280; the 420×260 resolution is now correctly excluded from the HUD rendering path.
- Fixed the RES panel height calculation that omitted the food row: `res_rect` height now uses `30 + (len(resources) + 1) * line_height` instead of `len(resources)`.

### Changed

- [FIX-A] Further upgraded HUD body font to Arial 17 bold (from 14) for improved readability on real fullscreen monitors; `HudPanel.line_height` updated from 19 to 23 px (font height 20 px + 3 px inter-line gap); `HudPanel.min_height` raised to 308 to maintain panel geometry with the larger font.
- [FIX-A] Scaled HUD font hierarchy: header font 18 → 21 bold, small font 12 → 15 regular (body+4 / body-2 rule).
- Upgraded HUD body font from Arial 12 bold to Arial 14 bold for improved readability at all resolutions; `HudPanel.line_height` updated from 15 to 19 px.
- Scaled HUD font hierarchy proportionally (session Round 1): header font 16 → 18 bold, small font 11 → 12 regular.
- Updated `test_hud_layout.py`: `FUNCTIONAL_RESOLUTIONS` now starts at 640×480 (420×260 moved to below-threshold bucket); T1 boundary test updated to 420×260.

### Tests

- Added `test_time_panel_has_minimum_height` (T_TIME_PADDING): asserts TIME panel height ≥ 68 px across all functional resolutions.
- `T_SUBTITLE_RIGHT` documented as a manual runtime test in `test_hud_layout.py` (requires a live pygame display).

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
