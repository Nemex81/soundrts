import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Sequence

import pygame

from .definitions import style
from .lib.sound_cache import sounds


# Event severity buckets used by the HUD to colour-code the event panel.
_COMBAT_EVENTS = frozenset({
    "attack", "under_attack", "death", "died", "killed", "destroyed",
})
_INFO_EVENTS = frozenset({
    "complete", "completed", "ready", "trained", "researched",
    "built", "discovered", "arrived",
})


def _classify_event(event: Any) -> str:
    name = str(event).lower()
    if name in _COMBAT_EVENTS or "attack" in name or "death" in name:
        return "combat"
    if name in _INFO_EVENTS:
        return "info"
    return "alert"


@dataclass(frozen=True)
class HudUnitSnapshot:
    label: str
    hit_points: Optional[int]
    max_hit_points: Optional[int]
    status: str


@dataclass(frozen=True)
class HudEvent:
    severity: str
    text: str


@dataclass(frozen=True)
class HudSnapshot:
    resources: List[str]
    food: str
    time: str
    speed: str
    units: List[HudUnitSnapshot]
    events: List[HudEvent]
    player: str


class HudPanel:
    min_width = 460
    min_height = 360
    max_units = 8
    max_events = 8
    margin = 8
    line_height = 26
    panel_header_height = 36
    player_height = 36
    time_height = 88
    res_bar_height = 40
    # T8-BOTTOMBAR: horizontal bottom strip with time + speed.
    bottom_bar_height = 40
    event_text_max_length = 23
    activity_width = 295
    activity_max_rows = 8
    activity_min_height = panel_header_height + line_height * 2 + margin

    def __init__(self, interface: Any) -> None:
        self.interface = interface
        self._events: Deque[HudEvent] = deque(maxlen=self.max_events)
        # Cache of HUD panel rectangles for future hit-testing (C1 hook).
        self._panel_rects: dict = {}
        # T3: collapse/expand state of the EVENTS panel. When False the
        # panel renders only its header and the rest of the right column
        # slides up to fill the freed space.
        self.events_visible: bool = False
        # T4: activity panel state (visible flag + active tab).
        # Tab values: "all" | "training" | "research" | "build".
        self.activity_visible: bool = False
        self.activity_tab: str = "all"
        self._tooltip_text = ""
        self._tooltip_pos: Optional[tuple] = None
        # T7-EVENTI: full (non-truncated) text of each rendered event row,
        # keyed by row index. Populated in _draw_snapshot, consumed in
        # _update_tooltip to feed the hover popup.
        self._event_row_texts: Dict[int, str] = {}
        # T7-MAPPA: map hover tracking with debounce delay.
        self._map_hover_entity: Any = None
        self._map_hover_start: float = 0.0
        self._map_tooltip_delay: float = 0.4
        # T7-COORD: last hovered map square (cell with col/row), kept on
        # the instance so set_map_hover can re-feed _build_map_tooltip
        # after the debounce timer elapses.
        self._map_hover_square: Any = None
        # T8-ACTIVITY: full text of each rendered activity row, used by
        # _update_tooltip to surface a popup on hover.
        self._activity_row_texts: Dict[int, str] = {}
        # T9-CANCEL: per-row unit reference, set by _draw_activity_panel
        # so handle_mouse_event can resolve a row index back to its
        # source unit and cancel its first active order.
        self._activity_row_units: Dict[int, Any] = {}
        # T9-TOOLTIP-GLOBAL: keep the last rendered snapshot so the
        # hover handler can read per-cell values (resources, units,
        # bottom bar) without re-querying the interface.
        self._last_snapshot: Optional[HudSnapshot] = None

    def on_event(self, entity: Any, event: Any) -> None:
        text = self._format_event(entity, event)
        if text:
            self._events.appendleft(HudEvent(severity=_classify_event(event), text=text))

    def handle_mouse_event(self, event: Any) -> bool:
        """Hit-test the HUD for click events.

        Returns True when the event has been consumed (so the caller
        should skip default map-click handling); False otherwise.

        Currently handled:
          - Left click on the EVENTS panel header toggles `events_visible`.
          - Left click on an ACTIVITY tab label switches `activity_tab`.
        """
        event_type = getattr(event, "type", None)
        pos = getattr(event, "pos", None)
        if event_type == pygame.MOUSEMOTION:
            self._update_tooltip(pos)
            return False
        if event_type != pygame.MOUSEBUTTONDOWN:
            return False
        if getattr(event, "button", None) != 1:
            return False
        if pos is None:
            return False
        events_rect = self._panel_rects.get("events_header")
        if events_rect is not None and events_rect.collidepoint(pos):
            self.events_visible = not self.events_visible
            return True
        # T8-ACTIVITY: header click toggles activity_visible (analogous
        # to the EVENTS header toggle).
        activity_header_rect = self._panel_rects.get("activity_header")
        if activity_header_rect is not None and activity_header_rect.collidepoint(pos):
            self.activity_visible = not self.activity_visible
            return True
        # T9-CANCEL: click on an ACTIVITY row cancels the first active
        # order of the unit that produced that row. Only honoured when
        # the panel is expanded; collapsed panels never expose rows.
        if self.activity_visible:
            for key, r in self._panel_rects.items():
                if not key.startswith("activity_row_"):
                    continue
                if r.collidepoint(pos):
                    try:
                        idx = int(key.split("_", 2)[2])
                    except (ValueError, IndexError):
                        continue
                    unit = self._activity_row_units.get(idx)
                    if unit is not None:
                        self._cancel_unit_order(unit)
                    return True
        # T4: tab strip hit-testing
        for tab_key in ("all", "training", "research", "build"):
            r = self._panel_rects.get("activity_tab_" + tab_key)
            if r is not None and r.collidepoint(pos):
                self.activity_tab = tab_key
                return True
        return False

    def _update_tooltip(self, pos: Any) -> None:
        self._tooltip_text = ""
        self._tooltip_pos = None
        if pos is None:
            return
        events_rect = self._panel_rects.get("events_header")
        if events_rect is not None and events_rect.collidepoint(pos):
            if self.events_visible:
                self._tooltip_text = self._hud_text("tooltip_events_hide", "Hide events")
            else:
                self._tooltip_text = self._hud_text("tooltip_events_show", "Show events")
            self._tooltip_pos = pos
            return
        # T8-ACTIVITY: header tooltip (show/hide hint).
        activity_header_rect = self._panel_rects.get("activity_header")
        if activity_header_rect is not None and activity_header_rect.collidepoint(pos):
            if self.activity_visible:
                self._tooltip_text = self._hud_text("tooltip_activity_hide", "Hide activity")
            else:
                self._tooltip_text = self._hud_text("tooltip_activity_show", "Show activity")
            self._tooltip_pos = pos
            return
        # T8-ACTIVITY: per-row tooltip with full activity text.
        if self.activity_visible:
            for key, r in self._panel_rects.items():
                if not key.startswith("activity_row_"):
                    continue
                if r.collidepoint(pos):
                    try:
                        idx = int(key.split("_", 2)[2])
                    except (ValueError, IndexError):
                        continue
                    full_text = self._activity_row_texts.get(idx, "")
                    if full_text:
                        # T9-CANCEL: append the cancel hint so the
                        # popup tells the mouse user the row is
                        # clickable.
                        hint = self._hud_text(
                            "tooltip_activity_cancel_hint",
                            "Click to cancel",
                        )
                        self._tooltip_text = self._hud_named_format(
                            "tooltip_activity_row_full",
                            "{row}  - {cancel_hint}",
                            row=full_text,
                            cancel_hint=hint,
                        )
                        self._tooltip_pos = pos
                        return
        for tab_key in self._ACTIVITY_TABS:
            r = self._panel_rects.get("activity_tab_" + tab_key)
            if r is not None and r.collidepoint(pos):
                style_key, default_label = self._ACTIVITY_TAB_LABELS[tab_key]
                tab_label = self._hud_text(style_key, default_label)
                self._tooltip_text = self._hud_named_format(
                    "tooltip_activity_tab",
                    "{tab}",
                    tab=tab_label,
                )
                self._tooltip_pos = pos
                return
        # T7-EVENTI: hover over a single event row in the EVENTS panel.
        # Only honoured when the panel is expanded, so a collapsed panel
        # never leaks tooltip popups for hidden rows.
        if self.events_visible:
            for key, r in self._panel_rects.items():
                if not key.startswith("event_row_"):
                    continue
                if r.collidepoint(pos):
                    try:
                        idx = int(key.split("_", 2)[2])
                    except (ValueError, IndexError):
                        continue
                    full_text = self._event_row_texts.get(idx, "")
                    if full_text:
                        self._tooltip_text = full_text
                        self._tooltip_pos = pos
                        return
        # T9-TOOLTIP-GLOBAL: per-cell tooltips for the static HUD
        # widgets (RES bar, BOTTOM bar, PLAYER panel, GROUP rows). All
        # values are read from the last rendered snapshot so the popup
        # always matches what the user is seeing on screen.
        snap = self._last_snapshot
        # Bottom bar: time cell.
        bt = self._panel_rects.get("bottom_time")
        if bt is not None and bt.collidepoint(pos):
            time_value = snap.time if snap is not None else ""
            self._tooltip_text = self._hud_named_format(
                "tooltip_bottom_time", "Game time: {time}", time=time_value
            )
            self._tooltip_pos = pos
            return
        # Bottom bar: speed cell.
        bs = self._panel_rects.get("bottom_speed")
        if bs is not None and bs.collidepoint(pos):
            speed_value = snap.speed if snap is not None else ""
            self._tooltip_text = self._hud_named_format(
                "tooltip_bottom_speed", "Game speed: {speed}", speed=speed_value
            )
            self._tooltip_pos = pos
            return
        # RES bar: food cell.
        fc = self._panel_rects.get("food_cell")
        if fc is not None and fc.collidepoint(pos):
            food_value = snap.food if snap is not None else ""
            self._tooltip_text = self._hud_named_format(
                "tooltip_food_cell", "Food: {food}", food=food_value
            )
            self._tooltip_pos = pos
            return
        # RES bar: individual resource cells.
        for key, r in self._panel_rects.items():
            if not key.startswith("res_cell_"):
                continue
            if not r.collidepoint(pos):
                continue
            try:
                idx = int(key.split("_", 2)[2])
            except (ValueError, IndexError):
                continue
            line = ""
            if snap is not None and 0 <= idx < len(snap.resources):
                line = snap.resources[idx]
            label, _, value = line.partition(":")
            self._tooltip_text = self._hud_named_format(
                "tooltip_res_cell",
                "{name}: {value}",
                name=label.strip() or "?",
                value=value.strip() or "?",
            )
            self._tooltip_pos = pos
            return
        # PLAYER panel (hover anywhere on the strip).
        pr = self._panel_rects.get("player")
        if pr is not None and pr.collidepoint(pos):
            name = snap.player if snap is not None else ""
            self._tooltip_text = self._hud_named_format(
                "tooltip_player_panel", "Player: {name}", name=name or "?"
            )
            self._tooltip_pos = pos
            return
        # GROUP rows: one tooltip per unit row.
        for key, r in self._panel_rects.items():
            if not key.startswith("group_row_"):
                continue
            if not r.collidepoint(pos):
                continue
            try:
                idx = int(key.split("_", 2)[2])
            except (ValueError, IndexError):
                continue
            unit = None
            if snap is not None and 0 <= idx < len(snap.units):
                unit = snap.units[idx]
            if unit is None:
                return
            status = unit.status or self._hud_text("idle", "idle")
            if unit.hit_points is not None and unit.max_hit_points is not None:
                self._tooltip_text = self._hud_named_format(
                    "tooltip_unit_row",
                    "{label} - {hp}/{hp_max} HP - {status}",
                    label=unit.label,
                    hp=unit.hit_points,
                    hp_max=unit.max_hit_points,
                    status=status,
                )
            else:
                self._tooltip_text = self._hud_named_format(
                    "tooltip_unit_row_nohp",
                    "{label} - {status}",
                    label=unit.label,
                    status=status,
                )
            self._tooltip_pos = pos
            return

    def get_snapshot(self) -> HudSnapshot:
        return HudSnapshot(
            resources=self._resource_lines(),
            food=self._food_line(),
            time=self._time_line(),
            speed=self._speed_line(),
            units=self._unit_lines(),
            events=list(self._events),
            player=self._player_line(),
        )

    def display(self) -> None:
        if not getattr(self.interface, "display_is_active", False):
            return
        screen = pygame.display.get_surface()
        if screen is None:
            return
        if screen.get_width() < self.min_width or screen.get_height() < self.min_height:
            return
        snapshot = self.get_snapshot()
        self._draw_snapshot(screen, snapshot)
        if getattr(self.interface, "is_paused", False):
            self._draw_pause_overlay(screen)

    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        from .lib.screen import screen_render

        width, height = screen.get_size()
        center_x = width // 2
        center_y = height // 2
        overlay = pygame.Surface((220, 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (center_x - 110, center_y - 30))
        pygame.draw.rect(screen, (255, 220, 0), pygame.Rect(center_x - 110, center_y - 30, 220, 60), 2)
        # T1: localized pause label (was hardcoded "|| PAUSA" — violated LEGGE-4).
        # Falls back to "|| PAUSED" if the active language has no `pause_label`
        # key under [hud] in style.txt.
        label = self._hud_text("pause_label", "|| PAUSED")
        screen_render(label, (center_x, center_y), center=True, color=(255, 220, 0))

    def _draw_snapshot(self, screen: pygame.Surface, snapshot: HudSnapshot) -> None:
        from .lib.screen import screen_render, screen_render_header

        # T9-TOOLTIP-GLOBAL: remember the snapshot so _update_tooltip
        # can read per-cell values on hover.
        self._last_snapshot = snapshot
        width, height = screen.get_size()
        left = self.margin
        top = self.margin
        right = width - self.margin
        # T8-BOTTOMBAR: reserve a horizontal strip at the bottom for the
        # new TIME+SPEED bar. Every right-column panel now sits above it.
        bottom = height - self.margin - self.bottom_bar_height
        self._panel_rects = {}
        # T7-EVENTI: reset per-frame mapping from event row index -> full text.
        self._event_row_texts = {}
        # T8-ACTIVITY: reset per-frame mapping from activity row -> full text.
        self._activity_row_texts = {}
        # T9-CANCEL: reset per-frame mapping from activity row -> unit.
        self._activity_row_units = {}

        # --- Layout anchor: horizontal resource bar ---
        res_bar_height = self.res_bar_height
        res_bar_bottom = self.margin + res_bar_height + self.margin

        # --- RES bar (horizontal, full-width top bar) ---
        bar_width = right - left
        res_rect = (left, top, bar_width, res_bar_height)
        self._draw_panel(screen, res_rect)
        self._panel_rects["res"] = pygame.Rect(*res_rect)
        num_cells = max(1, len(snapshot.resources) + 1)
        cell_width = bar_width / num_cells
        bar_center_y = top + res_bar_height // 2
        for i, line in enumerate(snapshot.resources):
            label, _, value = line.partition(":")
            text = "{}: {}".format(label.strip(), value.strip()) if value else label.strip()
            cell_left = left + int(i * cell_width)
            cell_right = left + int((i + 1) * cell_width)
            cell_center_x = cell_left + (cell_right - cell_left) // 2
            screen_render(text, (cell_center_x, bar_center_y), center=True, color=(255, 235, 130))
            # T9-TOOLTIP-GLOBAL: per-resource hit-test rect.
            self._panel_rects["res_cell_{}".format(i)] = pygame.Rect(
                cell_left, top, cell_right - cell_left, res_bar_height
            )
            if i > 0:
                pygame.draw.line(screen, (70, 110, 120), (cell_left, top + 1), (cell_left, top + res_bar_height - 1), 1)
        food_cell_left = left + int(len(snapshot.resources) * cell_width)
        food_cell_right = left + bar_width
        food_cell_center_x = food_cell_left + (food_cell_right - food_cell_left) // 2
        if snapshot.resources:
            pygame.draw.line(screen, (70, 110, 120), (food_cell_left, top + 1), (food_cell_left, top + res_bar_height - 1), 1)
        screen_render(snapshot.food, (food_cell_center_x, bar_center_y), center=True, color=(220, 220, 210))
        # T9-TOOLTIP-GLOBAL: hit-test rect for the food/pop cell.
        self._panel_rects["food_cell"] = pygame.Rect(
            food_cell_left, top, food_cell_right - food_cell_left, res_bar_height
        )

        # --- T8-BOTTOMBAR: TIME panel removed from the right column.
        # Time and speed are now rendered by the horizontal bottom bar
        # at the bottom of the screen. The events panel starts directly
        # below the resource bar.

        # --- EVENTS panel (right side, below RES BAR) — aligned to col_right_width R6 ---
        col_right_width = 295  # unified right-column width (EVENTS = PLAYER = GROUP)
        # T3: when collapsed, the panel shows only its header row.
        if self.events_visible:
            event_height = self.panel_header_height + max(1, len(snapshot.events)) * self.line_height
        else:
            event_height = self.panel_header_height
        event_top = res_bar_bottom
        event_rect = (right - col_right_width, event_top, col_right_width, event_height)
        self._draw_panel(screen, event_rect)
        self._panel_rects["events"] = pygame.Rect(*event_rect)
        # Header rect (used for click-to-toggle in handle_mouse_event).
        self._panel_rects["events_header"] = pygame.Rect(
            event_rect[0], event_rect[1], event_rect[2], self.panel_header_height
        )
        header_label = self._hud_text("panel_events", "EVENTS")
        if not self.events_visible:
            header_label = "{} {}".format(
                header_label, self._hud_text("events_collapsed", "(hidden)")
            )
        screen_render_header(header_label, (right - col_right_width + 6, event_top + 4), color=(255, 190, 120))
        if self.events_visible:
            y = event_top + self.panel_header_height
            events = snapshot.events
            if not events:
                screen_render(self._hud_text("no_events", "No recent events"), (right - col_right_width + 6, y), color=(230, 220, 205))
            else:
                for row_index, ev in enumerate(events[: self.max_events]):
                    prefix, ev_color = self._event_style(ev.severity)
                    full_line = self._hud_named_format(
                        "tooltip_event_full",
                        "{prefix} {text}",
                        prefix=prefix,
                        text=ev.text,
                    )
                    screen_render(
                        self._fit("{} {}".format(prefix, ev.text), self.event_text_max_length),
                        (right - col_right_width + 6, y),
                        color=ev_color,
                    )
                    # T7-EVENTI: register a hit-test rect for the full row
                    # and remember the non-truncated text for the tooltip.
                    self._panel_rects["event_row_{}".format(row_index)] = pygame.Rect(
                        right - col_right_width,
                        y,
                        col_right_width,
                        self.line_height,
                    )
                    self._event_row_texts[row_index] = full_line
                    y += self.line_height

        # --- PLAYER panel (bottom-right, below EVENTS) — Round 5 ---
        group_width = col_right_width
        event_bottom = event_top + event_height
        player_top = event_bottom + self.margin
        player_left = right - group_width
        player_rect = (player_left, player_top, group_width, self.player_height)
        self._draw_panel(screen, player_rect)
        self._panel_rects["player"] = pygame.Rect(*player_rect)
        screen_render_header(self._hud_text("panel_player", "PLAYER"), (player_left + 6, player_top + 4), color=(200, 230, 255))
        screen_render(snapshot.player, (player_left + 125, player_top + 8), color=(220, 235, 245))

        # --- GROUP panel (bottom-right, below PLAYER) — Round 5 ---
        group_top = player_top + self.player_height + 4
        # Adaptive strategy A: cap visible units to available vertical space.
        # UI-MASTER-02b BUG-T4: reserve room for the ACTIVITY section.
        # UI-MASTER-03 T8-ACTIVITY: the activity header is now ALWAYS
        # visible (acts as a toggle), so we reserve at least its header
        # height even when activity_visible == False.
        if self.activity_visible:
            reserved_for_activity = self.activity_min_height + self.margin
        else:
            reserved_for_activity = self.panel_header_height + self.margin
        available_h = max(
            0,
            bottom - group_top - self.panel_header_height - reserved_for_activity,
        )
        max_units_fit = max(1, available_h // self.line_height)
        units_to_show = max(1, min(self.max_units, int(max_units_fit)))
        unit_count = max(1, min(max(1, len(snapshot.units)), units_to_show))
        group_height = self.panel_header_height + unit_count * self.line_height
        group_rect = (player_left, group_top, group_width, group_height)
        self._draw_panel(screen, group_rect)
        self._panel_rects["group"] = pygame.Rect(*group_rect)
        screen_render_header(self._hud_text("panel_group", "GROUP"), (player_left + 6, group_top + 4), color=(180, 220, 255))
        y = group_top + self.panel_header_height
        units = snapshot.units or [HudUnitSnapshot(self._hud_text("no_unit", "No unit selected"), None, None, "")]
        for row_index, unit in enumerate(units[:units_to_show]):
            hp = ""
            if unit.hit_points is not None and unit.max_hit_points is not None:
                hp = " {}/{} hp".format(unit.hit_points, unit.max_hit_points)
            line = self._fit("{}{} {}".format(unit.label, hp, unit.status).strip(), 40)
            screen_render(line, (player_left + 6, y), color=(220, 235, 245))
            # T9-TOOLTIP-GLOBAL: per-unit hit-test rect.
            self._panel_rects["group_row_{}".format(row_index)] = pygame.Rect(
                player_left, y, group_width, self.line_height
            )
            y += self.line_height

        # --- T8-ACTIVITY: ACTIVITY header always visible (toggle) ---
        activity_header_top = group_top + group_height + self.margin
        activity_header_rect = pygame.Rect(
            player_left, activity_header_top, group_width, self.panel_header_height
        )
        self._draw_panel(screen, activity_header_rect)
        self._panel_rects["activity_header"] = activity_header_rect
        activity_label = self._hud_text("panel_activity", "ACTIVITY")
        if not self.activity_visible:
            activity_label = "{} {}".format(
                activity_label,
                self._hud_text("activity_collapsed", "(hidden)"),
            )
        screen_render_header(
            activity_label,
            (player_left + 6, activity_header_top + 4),
            color=(255, 220, 130),
        )
        if self.activity_visible:
            body_top = activity_header_top + self.panel_header_height
            if body_top < bottom - self.line_height:
                self._draw_activity_panel(
                    screen, player_left, body_top, group_width, bottom
                )
        else:
            # Clear cached tab and row rects so handle_mouse_event and
            # _update_tooltip don't react to clicks/hover on an invisible
            # strip.
            for key in list(self._panel_rects.keys()):
                if key.startswith("activity_tab_") or key.startswith("activity_row_"):
                    self._panel_rects.pop(key, None)

        # --- T8-BOTTOMBAR: horizontal bottom bar with time and speed ---
        bottom_bar_top = height - self.margin - self.bottom_bar_height
        bar_rect = (left, bottom_bar_top, right - left, self.bottom_bar_height)
        self._draw_panel(screen, bar_rect)
        self._panel_rects["bottom_bar"] = pygame.Rect(*bar_rect)
        cell_w = (right - left) // 2
        bar_cy = bottom_bar_top + self.bottom_bar_height // 2
        time_text = self._hud_named_format(
            "bottom_bar_time_fmt", "{time}", time=snapshot.time
        )
        screen_render(
            time_text,
            (left + cell_w // 2, bar_cy),
            center=True,
            color=(220, 235, 245),
        )
        pygame.draw.line(
            screen,
            (70, 110, 120),
            (left + cell_w, bottom_bar_top + 1),
            (left + cell_w, bottom_bar_top + self.bottom_bar_height - 1),
            1,
        )
        speed_text = self._hud_named_format(
            "bottom_bar_speed_fmt",
            "{speed}",
            speed=self._speed_with_icon(snapshot.speed),
        )
        screen_render(
            speed_text,
            (left + cell_w + cell_w // 2, bar_cy),
            center=True,
            color=(220, 235, 245),
        )
        # T9-TOOLTIP-GLOBAL: hit-test rects for the two bottom-bar cells.
        self._panel_rects["bottom_time"] = pygame.Rect(
            left, bottom_bar_top, cell_w, self.bottom_bar_height
        )
        self._panel_rects["bottom_speed"] = pygame.Rect(
            left + cell_w, bottom_bar_top, (right - left) - cell_w, self.bottom_bar_height
        )

        # UI-MASTER-02b: tooltip overlay must render regardless of the
        # ACTIVITY panel visibility (previous indentation kept it inside
        # the `else` branch and suppressed all popups when activity was
        # open).
        self._draw_tooltip(screen)

    def _event_style(self, severity: str):
        if severity == "combat":
            return "!", (255, 110, 110)
        if severity == "info":
            return "+", (140, 220, 140)
        return "*", (255, 200, 110)

    # ------------------------------------------------------------------
    # T4: activity panel helpers
    # ------------------------------------------------------------------
    _ACTIVITY_TABS = ("all", "training", "research", "build")
    _ACTIVITY_TAB_LABELS = {
        "all": ("tab_all", "ALL"),
        "training": ("tab_training", "TRAIN"),
        "research": ("tab_research", "RESEARCH"),
        "build": ("tab_build", "BUILD"),
    }
    def _classify_order(self, order: Any) -> str:
        """Return 'training' | 'research' | 'build' | '' for a worldorder
        instance. Defensive: never raises."""
        kw = ""
        try:
            cls = getattr(order, "cls", None)
            if cls is not None:
                kw = getattr(cls, "keyword", "") or ""
        except Exception:
            kw = ""
        if not kw:
            kw = type(order).__name__.lower()
        if "train" in kw:
            return "training"
        if "research" in kw:
            return "research"
        if "build" in kw or "upgrade" in kw:
            return "build"
        return ""

    def _collect_activity(self) -> List[tuple]:
        """Return a list of ``(kind, label, progress_pct, unit)`` tuples
        describing the active production/research/construction orders
        of the local player. The 4th field (``unit``) is the source
        unit reference, used by T9-CANCEL to resolve a clicked row
        back to the unit whose order must be cancelled. Defensive:
        returns [] on any error."""
        items: List[tuple] = []
        try:
            player = getattr(self.interface, "player", None)
            if player is None:
                return items
            units = getattr(player, "units", None) or []
            for u in units:
                orders = getattr(u, "orders", None)
                if not orders:
                    continue
                first = orders[0]
                kind = self._classify_order(first)
                if not kind:
                    continue
                target_type = getattr(first, "type", None)
                target_name = getattr(target_type, "type_name", None) or "?"
                time_left = getattr(first, "time", None)
                time_cost = getattr(first, "time_cost", None)
                pct = 0
                try:
                    if time_cost and time_cost > 0:
                        pct = max(0, min(100, int(100 - (float(time_left) * 100.0 / float(time_cost)))))
                except Exception:
                    pct = 0
                items.append((kind, target_name, pct, u))
        except Exception:
            pass
        return items

    def _draw_activity_panel(
        self,
        screen: pygame.Surface,
        left: int,
        top: int,
        width: int,
        bottom: int,
    ) -> None:
        """Draw the ACTIVITY body (tab strip + rows + progress bars).

        UI-MASTER-03 T8-ACTIVITY: the header is now rendered by
        ``_draw_snapshot`` so the panel is always togglable. ``top`` is
        the body top (immediately below the header).
        """
        from .lib.screen import screen_render

        items = self._collect_activity()
        # Pre-compute counters per tab for the strip labels. Tolerate
        # both the legacy 3-tuple and the T9-CANCEL 4-tuple so test
        # patches that still inject 3-tuples keep working.
        counts = {"all": len(items), "training": 0, "research": 0, "build": 0}
        for item in items:
            kind = item[0] if item else ""
            counts[kind] = counts.get(kind, 0) + 1
        if self.activity_tab == "all":
            filtered = items
        else:
            filtered = [it for it in items if it[0] == self.activity_tab]
        available_height = max(self.line_height * 2, bottom - top)
        rows_fit = max(
            1,
            (available_height - self.line_height - self.margin) // self.line_height,
        )
        rows = min(len(filtered), self.activity_max_rows, rows_fit)
        body_rows_height = max(1, rows) * self.line_height
        total_height = self.line_height + body_rows_height + self.margin
        rect = pygame.Rect(left, top, width, total_height)
        self._draw_panel(screen, rect)
        self._panel_rects["activity"] = rect
        # Tab strip
        tab_strip_top = top
        tab_count = len(self._ACTIVITY_TABS)
        tab_width = (width - 2 * self.margin) // tab_count
        for i, tab_key in enumerate(self._ACTIVITY_TABS):
            tab_left = left + self.margin + i * tab_width
            tab_rect = pygame.Rect(tab_left, tab_strip_top, tab_width - 2, self.line_height - 2)
            self._panel_rects["activity_tab_" + tab_key] = tab_rect
            is_active = (tab_key == self.activity_tab)
            color = (255, 235, 130) if is_active else (180, 190, 200)
            if is_active:
                pygame.draw.rect(screen, (255, 200, 80), tab_rect, 1)
            style_key, default_label = self._ACTIVITY_TAB_LABELS[tab_key]
            label = "{} ({})".format(
                self._hud_text(style_key, default_label), counts.get(tab_key, 0)
            )
            screen_render(self._fit(label, 12), (tab_left + 2, tab_strip_top), color=color)
        # Body rows
        body_top = tab_strip_top + self.line_height
        if not filtered:
            screen_render(
                self._hud_text("activity_empty", "(no active production)"),
                (left + 6, body_top),
                color=(200, 200, 200),
            )
            return
        y = body_top
        max_bar_width = max(1, width - 2 * self.margin)
        for row_index, item in enumerate(filtered[:rows]):
            # Accept both 3-tuple (legacy) and 4-tuple (T9-CANCEL).
            kind = item[0]
            name = item[1]
            pct = item[2]
            unit = item[3] if len(item) >= 4 else None
            prefix_key = {
                "training": "activity_prefix_training",
                "research": "activity_prefix_research",
                "build": "activity_prefix_build",
            }.get(kind, "activity_prefix_unknown")
            prefix = self._hud_text(prefix_key, "?")
            line = "[{}] {} {}%".format(prefix, name, pct)
            # Visual progress bar (thin strip at the row's bottom edge).
            bar_y = y + self.line_height - 4
            bg_rect = pygame.Rect(left + self.margin, bar_y, max_bar_width, 3)
            pygame.draw.rect(screen, (40, 60, 60), bg_rect)
            try:
                pct_int = max(0, min(100, int(pct)))
            except (TypeError, ValueError):
                pct_int = 0
            fill_w = max_bar_width * pct_int // 100
            if fill_w > 0:
                fill_rect = pygame.Rect(left + self.margin, bar_y, fill_w, 3)
                pygame.draw.rect(screen, (140, 220, 140), fill_rect)
            screen_render(self._fit(line, 38), (left + 6, y), color=(220, 235, 245))
            # Hit-test rect for tooltip / future cancel-click.
            self._panel_rects["activity_row_{}".format(row_index)] = pygame.Rect(
                left, y, width, self.line_height
            )
            self._activity_row_texts[row_index] = line
            # T9-CANCEL: remember the source unit for this row so a
            # left-click can resolve which unit's first order to drop.
            self._activity_row_units[row_index] = unit
            y += self.line_height

    def _speed_with_icon(self, speed_text: str) -> str:
        try:
            value = float(speed_text.rsplit("x", 1)[-1])
        except (ValueError, IndexError):
            return speed_text
        if value >= 1.5:
            prefix = ">>"
        elif value >= 1.0:
            prefix = ">"
        else:
            prefix = "="
        return "{} {}".format(prefix, speed_text)

    # ------------------------------------------------------------------
    # T7-MAPPA: map hover tooltip
    # ------------------------------------------------------------------
    def is_pos_over_hud(self, pos: Any) -> bool:
        """Return True when the screen position overlaps any HUD panel
        rect. Used by clientgame to skip map-hover tooltips while the
        mouse is over the HUD chrome."""
        if pos is None:
            return False
        for key, r in self._panel_rects.items():
            # Skip purely virtual rects (tab rects live inside the
            # activity panel rect already, so the parent check covers
            # them).
            if key.startswith("event_row_") or key.startswith("activity_tab_"):
                continue
            if r is not None and r.collidepoint(pos):
                return True
        return False

    def set_map_hover(self, entity: Any, pos: Any, square: Any = None) -> None:
        """Track the map-cell hover state and surface a tooltip after a
        short stable delay (``_map_tooltip_delay`` seconds). When
        ``entity`` is ``None`` and no ``square`` is provided the hover
        state and any active tooltip are cleared. When ``entity`` is
        ``None`` but ``square`` is provided (T9-TOOLTIP-GLOBAL) a
        coordinates-only tooltip is surfaced immediately so empty map
        cells still expose their (col,row) to mouse users. The
        optional ``square`` argument (T7-COORD) lets the caller pass
        the grid cell currently under the cursor so the tooltip can
        include its (col,row) coordinates. Defensive: never raises.
        """
        if entity is None:
            self._map_hover_entity = None
            self._map_hover_start = 0.0
            if square is None:
                # Full clear when leaving both map and HUD.
                self._map_hover_square = None
                self._tooltip_text = ""
                self._tooltip_pos = None
                return
            # T9-TOOLTIP-GLOBAL: empty cell tooltip with coordinates.
            self._map_hover_square = square
            try:
                col = getattr(square, "col", None)
                row = getattr(square, "row", None)
            except Exception:
                col = row = None
            if col is not None and row is not None:
                self._tooltip_text = self._hud_named_format(
                    "tooltip_map_empty_cell",
                    "Cell ({col},{row})",
                    col=col,
                    row=row,
                )
                self._tooltip_pos = pos
            else:
                self._tooltip_text = ""
                self._tooltip_pos = None
            return
        self._map_hover_square = square
        now = time.monotonic()
        if entity is not self._map_hover_entity:
            self._map_hover_entity = entity
            self._map_hover_start = now
            return
        if (now - self._map_hover_start) >= self._map_tooltip_delay:
            try:
                text = self._build_map_tooltip(entity, pos, square=square)
            except Exception:
                text = ""
            if text:
                self._tooltip_text = text
                self._tooltip_pos = pos

    def _build_map_tooltip(self, entity: Any, pos: Any, square: Any = None) -> str:
        """Compose the localized tooltip text for a hovered map entity.

        Every player-visible token is sourced from the ``[hud]`` style
        section (LEGGE-4). Each attribute access on ``entity`` is
        defensive: missing attributes simply skip their segment. The
        optional ``square`` (T7-COORD) appends ``(col,row)`` when the
        cell exposes those attributes.
        """
        # name --------------------------------------------------------------
        try:
            name = getattr(entity, "type_name", None)
        except Exception:
            name = None
        if not name:
            name = self._hud_text("entity_na", "?")
        # hp / hp_max -------------------------------------------------------
        hp_str = ""
        try:
            hp = getattr(entity, "hp", None)
            hp_max = getattr(entity, "hp_max", None)
            if hp is not None and hp_max is not None:
                hp_str = self._hud_named_format(
                    "tooltip_map_hp",
                    "HP: {hp}/{hp_max}",
                    hp=int(hp),
                    hp_max=int(hp_max),
                )
        except Exception:
            hp_str = ""
        # owner -------------------------------------------------------------
        owner_str = ""
        try:
            owner = getattr(entity, "player", None) or getattr(entity, "owner", None)
            if owner is not None:
                owner_name = getattr(owner, "name", None) or getattr(owner, "login", None)
                if owner_name:
                    owner_str = self._hud_named_format(
                        "tooltip_map_owner",
                        "[{owner}]",
                        owner=str(owner_name),
                    )
        except Exception:
            owner_str = ""
        # first order -------------------------------------------------------
        order_str = ""
        try:
            orders = getattr(entity, "orders", None) or []
            if orders:
                first = orders[0]
                kw = getattr(first, "keyword", None)
                if kw is None:
                    cls = getattr(first, "cls", None)
                    kw = getattr(cls, "keyword", None) if cls is not None else None
                if kw:
                    order_str = str(kw)
        except Exception:
            order_str = ""
        # coords (T7-COORD) -------------------------------------------------
        coords_str = ""
        try:
            if square is not None:
                col = getattr(square, "col", None)
                row = getattr(square, "row", None)
                if col is not None and row is not None:
                    coords_str = self._hud_named_format(
                        "tooltip_map_coords",
                        "({col},{row})",
                        col=col,
                        row=row,
                    )
        except Exception:
            coords_str = ""
        text = self._hud_named_format(
            "tooltip_map_entity",
            "{name} {hp} {owner} {order} {coords}",
            name=name,
            hp=hp_str,
            owner=owner_str,
            order=order_str,
            coords=coords_str,
        )
        # Collapse double spaces left by empty segments and trim.
        return " ".join(text.split()).strip()

    # ------------------------------------------------------------------
    # T9-CANCEL: client-side order cancellation triggered by a left
    # click on an ACTIVITY row.
    # ------------------------------------------------------------------
    def _cancel_unit_order(self, unit: Any) -> None:
        """Drop the first pending order of ``unit``. Strictly defensive:
        any exception (immutable orders list, missing attribute, racing
        snapshot update) is swallowed so a click can never crash the
        UI loop.
        """
        try:
            orders = getattr(unit, "orders", None)
            if orders:
                orders.pop(0)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # C1-HITTEST: public read-only access to panel rects
    # ------------------------------------------------------------------
    def rect_for(self, name: str) -> Optional[pygame.Rect]:
        """Return the pygame.Rect for the named HUD panel, or None if
        the name is not registered (e.g. the panel is collapsed or has
        not been drawn yet). Public stable API: external modules must
        not access ``_panel_rects`` directly."""
        return self._panel_rects.get(name)

    def panel_names(self) -> tuple:
        """Return the tuple of all currently registered panel rect
        names. Useful for diagnostics and tests."""
        return tuple(self._panel_rects.keys())

    def _draw_tooltip(self, screen: pygame.Surface) -> None:
        if not self._tooltip_text or self._tooltip_pos is None:
            return
        from .lib.screen import screen_render

        x, y = self._tooltip_pos
        text = self._fit(self._tooltip_text, 36)
        tooltip_width = max(90, min(260, len(text) * 8 + 16))
        tooltip_height = 26
        left = min(max(self.margin, x + 12), screen.get_width() - tooltip_width - self.margin)
        top = min(max(self.margin, y + 12), screen.get_height() - tooltip_height - self.margin)
        rect = (left, top, tooltip_width, tooltip_height)
        self._draw_panel(screen, rect)
        screen_render(text, (left + 8, top + 5), color=(240, 235, 190))

    def _draw_panel(self, screen: pygame.Surface, rect: Sequence[int]) -> None:
        panel = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 165))
        screen.blit(panel, (rect[0], rect[1]))
        pygame.draw.rect(screen, (70, 110, 120), pygame.Rect(*rect), 1)

    def _resource_lines(self) -> List[str]:
        lines = []
        try:
            resources = list(self.interface.resources)
        except Exception:
            resources = []
        for index, value in enumerate(resources):
            name = self._resource_name(index)
            lines.append("{}: {}".format(name, value))
        return lines or [self._hud_text("resources_na", "Resources: n/a")]

    def _resource_name(self, index: int) -> str:
        key = "resource_{}_title".format(index)
        try:
            parts = style.get("parameters", key)
        except Exception:
            parts = None
        if isinstance(parts, (list, tuple)):
            resolved = []
            for p in parts:
                if isinstance(p, str) and p.isdigit():
                    # Risolve il token numerico via il sistema TTS localizzato
                    # (es. 131 -> "gold"/"oro" in base alla lingua attiva)
                    text = sounds.translate_sound_number(int(p))
                    if text and not str(text).isdigit():
                        resolved.append(str(text))
                elif isinstance(p, str):
                    resolved.append(p)
            label = " ".join(resolved).strip()
        else:
            label = self._parts_to_text(parts)
        return label or self._hud_format("resource_n", "Resource {}", index + 1)

    def _food_line(self) -> str:
        try:
            return self._hud_format("pop_fmt", "Pop: {}/{}", self.interface.used_food, self.interface.available_food)
        except Exception:
            return self._hud_text("pop_na", "Pop: n/a")

    def _time_line(self) -> str:
        try:
            seconds = int(self.interface.last_virtual_time)
        except Exception:
            seconds = 0
        minutes, seconds = divmod(seconds, 60)
        return self._hud_format("time_fmt", "Time: {:02d}:{:02d}", minutes, seconds)

    def _speed_line(self) -> str:
        try:
            speed = self.interface._get_relative_speed()
        except Exception:
            speed = getattr(self.interface, "speed", 0)
        try:
            return self._hud_format("speed_fmt", "Speed: x{:.1f}", speed)
        except Exception:
            return self._hud_text("speed_na", "Speed: n/a")

    def _player_line(self) -> str:
        player = getattr(self.interface, "player", None)
        if player is None:
            return self._hud_text("player_na", "Player")
        name = getattr(player, "name", None) or getattr(player, "login", None)
        if not name:
            name = self._hud_text("player_na", "Player")
        race = getattr(player, "race", None)
        if race:
            return "{} ({})".format(name, race)
        return str(name)

    def _unit_lines(self) -> List[HudUnitSnapshot]:
        units = []
        group = list(getattr(self.interface, "group", []) or [])
        dobjets = getattr(self.interface, "dobjets", {}) or {}
        for unit_id in group[: self.max_units]:
            unit = dobjets.get(unit_id)
            if unit is None:
                continue
            units.append(
                HudUnitSnapshot(
                    label=self._unit_label(unit),
                    hit_points=self._safe_int(unit, "hp"),
                    max_hit_points=self._safe_int(unit, "hp_max"),
                    status=self._unit_status(unit),
                )
            )
        return units

    def _unit_label(self, unit: Any) -> str:
        label = getattr(unit, "type_name", None)
        number = getattr(unit, "number", None)
        if label and number is not None:
            return "{} #{}".format(label, number)
        if label:
            return str(label)
        return self._hud_text("unit_na", "unit")

    def _unit_status(self, unit: Any) -> str:
        orders = getattr(unit, "orders", None) or []
        if orders:
            keyword = getattr(orders[0], "keyword", None)
            if keyword:
                return str(keyword)
        activity = getattr(unit, "activity", None)
        if activity:
            return str(activity)
        return self._hud_text("idle", "idle")

    def _format_event(self, entity: Any, event: Any) -> str:
        event_text = str(event).replace("_", " ")
        label = getattr(entity, "type_name", None) or self._hud_text("object_na", "object")
        place = getattr(entity, "place", None)
        place_text = self._place_text(place)
        if place_text:
            return self._fit(
                self._hud_named_format(
                    "event_with_place_fmt",
                    "{event}: {object} {place}",
                    event=event_text,
                    object=label,
                    place=place_text,
                ),
                80,
            )
        return self._fit(
            self._hud_named_format(
                "event_fmt",
                "{event}: {object}",
                event=event_text,
                object=label,
            ),
            80,
        )

    def _place_text(self, place: Any) -> str:
        if place is None:
            return ""
        name = getattr(place, "name", None)
        if name:
            return str(name)
        col = getattr(place, "col", None)
        row = getattr(place, "row", None)
        if col is not None and row is not None:
            return "{},{}".format(col, row)
        return ""

    def _safe_int(self, unit: Any, name: str) -> Optional[int]:
        try:
            return int(getattr(unit, name))
        except Exception:
            return None

    def _parts_to_text(self, parts: Any) -> str:
        """Convert style parts to a display string. Numeric values are preserved."""
        if isinstance(parts, str):
            return parts
        if isinstance(parts, (list, tuple)):
            words = [str(part) for part in parts if isinstance(part, str)]
            return " ".join(words)
        return ""

    def _hud_text(self, key: str, default: str) -> str:
        try:
            text = self._parts_to_text(style.get("hud", key, warn_if_not_found=False))
        except Exception:
            text = ""
        return text or default

    def _hud_format(self, key: str, default: str, *args: Any) -> str:
        template = self._hud_text(key, default)
        try:
            return template.format(*args)
        except Exception:
            return default.format(*args)

    def _hud_named_format(self, key: str, default: str, **kwargs: Any) -> str:
        template = self._hud_text(key, default)
        try:
            return template.format(**kwargs)
        except Exception:
            return default.format(**kwargs)

    def _fit(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
