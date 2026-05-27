from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, List, Optional, Sequence

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
    event_text_max_length = 23

    def __init__(self, interface: Any) -> None:
        self.interface = interface
        self._events: Deque[HudEvent] = deque(maxlen=self.max_events)
        # Cache of HUD panel rectangles for future hit-testing (C1 hook).
        self._panel_rects: dict = {}

    def on_event(self, entity: Any, event: Any) -> None:
        text = self._format_event(entity, event)
        if text:
            self._events.appendleft(HudEvent(severity=_classify_event(event), text=text))

    def handle_mouse_event(self, event: Any) -> bool:
        """Hook for future HUD interactions. Currently a no-op that always
        returns False so the main mouse handler keeps full control.
        """
        return False

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
        screen_render("|| PAUSA", (center_x, center_y), center=True, color=(255, 220, 0))

    def _draw_snapshot(self, screen: pygame.Surface, snapshot: HudSnapshot) -> None:
        from .lib.screen import screen_render, screen_render_header

        width, height = screen.get_size()
        left = self.margin
        top = self.margin
        right = width - self.margin
        bottom = height - self.margin
        self._panel_rects = {}

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
            cell_center_x = left + int(i * cell_width) + int(cell_width / 2)
            screen_render(text, (cell_center_x, bar_center_y), center=True, color=(255, 235, 130))
            if i > 0:
                sep_x = left + int(i * cell_width)
                pygame.draw.line(screen, (70, 110, 120), (sep_x, top + 1), (sep_x, top + res_bar_height - 1), 1)
        food_cell_left = left + int(len(snapshot.resources) * cell_width)
        food_cell_center_x = food_cell_left + int(cell_width / 2)
        if snapshot.resources:
            pygame.draw.line(screen, (70, 110, 120), (food_cell_left, top + 1), (food_cell_left, top + res_bar_height - 1), 1)
        screen_render(snapshot.food, (food_cell_center_x, bar_center_y), center=True, color=(220, 220, 210))

        # --- TIME panel (top-right, below res bar) ---
        time_width = 175
        time_rect = (right - time_width, res_bar_bottom, time_width, self.time_height)
        self._draw_panel(screen, time_rect)
        self._panel_rects["time"] = pygame.Rect(*time_rect)
        screen_render_header(self._hud_text("panel_time", "TIME"), (right - time_width + 6, res_bar_bottom + 4), color=(160, 210, 255))
        screen_render(snapshot.time, (right - time_width + 6, res_bar_bottom + self.panel_header_height), color=(220, 235, 245))
        screen_render(self._speed_with_icon(snapshot.speed), (right - time_width + 6, res_bar_bottom + self.panel_header_height + self.line_height), color=(220, 235, 245))

        # --- EVENTS panel (right side, below TIME) — aligned to col_right_width R6 ---
        col_right_width = 295  # unified right-column width (EVENTS = PLAYER = GROUP)
        event_height = self.panel_header_height + max(1, len(snapshot.events)) * self.line_height
        event_top = res_bar_bottom + self.time_height + self.margin
        event_rect = (right - col_right_width, event_top, col_right_width, event_height)
        self._draw_panel(screen, event_rect)
        self._panel_rects["events"] = pygame.Rect(*event_rect)
        screen_render_header(self._hud_text("panel_events", "EVENTS"), (right - col_right_width + 6, event_top + 4), color=(255, 190, 120))
        y = event_top + self.panel_header_height
        events = snapshot.events
        if not events:
            screen_render(self._hud_text("no_events", "No recent events"), (right - col_right_width + 6, y), color=(230, 220, 205))
        else:
            for ev in events[: self.max_events]:
                prefix, ev_color = self._event_style(ev.severity)
                screen_render(
                    self._fit("{} {}".format(prefix, ev.text), self.event_text_max_length),
                    (right - col_right_width + 6, y),
                    color=ev_color,
                )
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
        # Adaptive strategy A: cap visible units to available vertical space
        available_h = max(0, bottom - group_top - self.panel_header_height)
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
        for unit in units[:units_to_show]:
            hp = ""
            if unit.hit_points is not None and unit.max_hit_points is not None:
                hp = " {}/{} hp".format(unit.hit_points, unit.max_hit_points)
            line = self._fit("{}{} {}".format(unit.label, hp, unit.status).strip(), 40)
            screen_render(line, (player_left + 6, y), color=(220, 235, 245))
            y += self.line_height

    def _event_style(self, severity: str):
        if severity == "combat":
            return "!", (255, 110, 110)
        if severity == "info":
            return "+", (140, 220, 140)
        return "*", (255, 200, 110)

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
            return self._fit("{}: {} at {}".format(event_text, label, place_text), 80)
        return self._fit("{}: {}".format(event_text, label), 80)

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

    def _fit(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
