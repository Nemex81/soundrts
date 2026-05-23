from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, List, Optional, Sequence

import pygame

from .definitions import style


@dataclass(frozen=True)
class HudUnitSnapshot:
    label: str
    hit_points: Optional[int]
    max_hit_points: Optional[int]
    status: str


@dataclass(frozen=True)
class HudSnapshot:
    resources: List[str]
    food: str
    time: str
    speed: str
    units: List[HudUnitSnapshot]
    events: List[str]


class HudPanel:
    min_width = 420
    min_height = 260
    max_units = 8
    max_events = 8
    margin = 8
    line_height = 15

    def __init__(self, interface: Any) -> None:
        self.interface = interface
        self._events: Deque[str] = deque(maxlen=self.max_events)

    def on_event(self, entity: Any, event: Any) -> None:
        text = self._format_event(entity, event)
        if text:
            self._events.appendleft(text)

    def get_snapshot(self) -> HudSnapshot:
        return HudSnapshot(
            resources=self._resource_lines(),
            food=self._food_line(),
            time=self._time_line(),
            speed=self._speed_line(),
            units=self._unit_lines(),
            events=list(self._events),
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
        from .lib.screen import screen_render

        width, height = screen.get_size()
        left = self.margin
        top = self.margin
        right = width - self.margin
        bottom = height - self.margin

        self._draw_panel(screen, (left, top, 170, 25 + len(snapshot.resources) * self.line_height))
        screen_render("RES", (left + 6, top + 5), color=(120, 220, 190))
        y = top + 20
        for line in snapshot.resources:
            screen_render(line, (left + 6, y), color=(220, 220, 210))
            y += self.line_height
        screen_render(snapshot.food, (left + 6, y), color=(220, 220, 210))

        time_width = 165
        self._draw_panel(screen, (right - time_width, top, time_width, 55))
        screen_render(snapshot.time, (right - time_width + 6, top + 6), color=(160, 210, 255))
        screen_render(snapshot.speed, (right - time_width + 6, top + 23), color=(160, 210, 255))

        event_width = 245
        event_height = 25 + max(1, len(snapshot.events)) * self.line_height
        event_top = top + 65
        self._draw_panel(screen, (right - event_width, event_top, event_width, event_height))
        screen_render("EVENTS", (right - event_width + 6, event_top + 5), color=(255, 190, 120))
        y = event_top + 20
        events = snapshot.events or ["No recent events"]
        for line in events[: self.max_events]:
            screen_render(self._fit(line, 34), (right - event_width + 6, y), color=(230, 220, 205))
            y += self.line_height

        group_width = 285
        unit_count = max(1, len(snapshot.units))
        group_height = 25 + unit_count * self.line_height
        group_top = bottom - group_height
        self._draw_panel(screen, (left, group_top, group_width, group_height))
        screen_render("GROUP", (left + 6, group_top + 5), color=(180, 220, 255))
        y = group_top + 20
        units = snapshot.units or [HudUnitSnapshot("No unit selected", None, None, "")]
        for unit in units[: self.max_units]:
            hp = ""
            if unit.hit_points is not None and unit.max_hit_points is not None:
                hp = " {}/{} hp".format(unit.hit_points, unit.max_hit_points)
            line = self._fit("{}{} {}".format(unit.label, hp, unit.status).strip(), 40)
            screen_render(line, (left + 6, y), color=(220, 235, 245))
            y += self.line_height

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
