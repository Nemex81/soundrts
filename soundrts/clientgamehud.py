from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, List, Optional, Sequence

import pygame

from .definitions import style


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
    min_height = 280
    max_units = 8
    max_events = 8
    margin = 8
    line_height = 19

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

    def _draw_snapshot(self, screen: pygame.Surface, snapshot: HudSnapshot) -> None:
        from .lib.screen import screen_render, screen_render_header

        width, height = screen.get_size()
        left = self.margin
        top = self.margin
        right = width - self.margin
        bottom = height - self.margin
        self._panel_rects = {}

        # --- RES panel (top-left) ---
        res_rect = (left, top, 180, 30 + (len(snapshot.resources) + 1) * self.line_height)
        self._draw_panel(screen, res_rect)
        self._panel_rects["res"] = pygame.Rect(*res_rect)
        screen_render_header("RES", (left + 6, top + 4), color=(120, 220, 190))
        y = top + 25
        for line in snapshot.resources:
            label, _, value = line.partition(":")
            screen_render(label + ":", (left + 6, y), color=(220, 220, 210))
            if value:
                screen_render(value.strip(), (left + 100, y), color=(255, 235, 130))
            y += self.line_height
        screen_render(snapshot.food, (left + 6, y), color=(220, 220, 210))

        # --- TIME panel (top-right) ---
        time_width = 175
        time_rect = (right - time_width, top, time_width, 60)
        self._draw_panel(screen, time_rect)
        self._panel_rects["time"] = pygame.Rect(*time_rect)
        screen_render_header("TIME", (right - time_width + 6, top + 4), color=(160, 210, 255))
        screen_render(snapshot.time, (right - time_width + 6, top + 27), color=(220, 235, 245))
        screen_render(self._speed_with_icon(snapshot.speed), (right - time_width + 6, top + 42), color=(220, 235, 245))

        # --- EVENTS panel (right side, below TIME) ---
        event_width = 260
        event_height = 30 + max(1, len(snapshot.events)) * self.line_height
        event_top = top + 70
        event_rect = (right - event_width, event_top, event_width, event_height)
        self._draw_panel(screen, event_rect)
        self._panel_rects["events"] = pygame.Rect(*event_rect)
        screen_render_header("EVENTS", (right - event_width + 6, event_top + 4), color=(255, 190, 120))
        y = event_top + 25
        events = snapshot.events
        if not events:
            screen_render("No recent events", (right - event_width + 6, y), color=(230, 220, 205))
        else:
            for ev in events[: self.max_events]:
                prefix, ev_color = self._event_style(ev.severity)
                screen_render(
                    self._fit("{} {}".format(prefix, ev.text), 36),
                    (right - event_width + 6, y),
                    color=ev_color,
                )
                y += self.line_height

        # --- PLAYER panel (bottom-left, above GROUP) ---
        player_height = 30
        group_width = 295
        unit_count = max(1, len(snapshot.units))
        group_height = 30 + unit_count * self.line_height
        group_top = bottom - group_height
        player_top = group_top - player_height - 4
        player_rect = (left, player_top, group_width, player_height)
        self._draw_panel(screen, player_rect)
        self._panel_rects["player"] = pygame.Rect(*player_rect)
        screen_render_header("PLAYER", (left + 6, player_top + 4), color=(200, 230, 255))
        screen_render(snapshot.player, (left + 80, player_top + 8), color=(220, 235, 245))

        # --- GROUP panel (bottom-left) ---
        group_rect = (left, group_top, group_width, group_height)
        self._draw_panel(screen, group_rect)
        self._panel_rects["group"] = pygame.Rect(*group_rect)
        screen_render_header("GROUP", (left + 6, group_top + 4), color=(180, 220, 255))
        y = group_top + 25
        units = snapshot.units or [HudUnitSnapshot("No unit selected", None, None, "")]
        for unit in units[: self.max_units]:
            hp = ""
            if unit.hit_points is not None and unit.max_hit_points is not None:
                hp = " {}/{} hp".format(unit.hit_points, unit.max_hit_points)
            line = self._fit("{}{} {}".format(unit.label, hp, unit.status).strip(), 40)
            screen_render(line, (left + 6, y), color=(220, 235, 245))
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
        return lines or ["Resources: n/a"]

    def _resource_name(self, index: int) -> str:
        key = "resource_{}_title".format(index)
        try:
            parts = style.get("parameters", key)
        except Exception:
            parts = None
        label = self._parts_to_text(parts)
        return label or "Resource {}".format(index + 1)

    def _food_line(self) -> str:
        try:
            return "Pop: {}/{}".format(self.interface.used_food, self.interface.available_food)
        except Exception:
            return "Pop: n/a"

    def _time_line(self) -> str:
        try:
            seconds = int(self.interface.last_virtual_time)
        except Exception:
            seconds = 0
        minutes, seconds = divmod(seconds, 60)
        return "Time: {:02d}:{:02d}".format(minutes, seconds)

    def _speed_line(self) -> str:
        try:
            speed = self.interface._get_relative_speed()
        except Exception:
            speed = getattr(self.interface, "speed", 0)
        try:
            return "Speed: x{:.1f}".format(speed)
        except Exception:
            return "Speed: n/a"

    def _player_line(self) -> str:
        player = getattr(self.interface, "player", None)
        if player is None:
            return "Player"
        name = getattr(player, "name", None) or getattr(player, "login", None)
        if not name:
            name = "Player"
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
        return "unit"

    def _unit_status(self, unit: Any) -> str:
        orders = getattr(unit, "orders", None) or []
        if orders:
            keyword = getattr(orders[0], "keyword", None)
            if keyword:
                return str(keyword)
        activity = getattr(unit, "activity", None)
        if activity:
            return str(activity)
        return "idle"

    def _format_event(self, entity: Any, event: Any) -> str:
        event_text = str(event).replace("_", " ")
        label = getattr(entity, "type_name", None) or "object"
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
        if isinstance(parts, str):
            return parts
        if isinstance(parts, (list, tuple)):
            words = [str(part) for part in parts if isinstance(part, str)]
            return " ".join(words)
        return ""

    def _fit(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
