from math import cos, radians, sin

import pygame

from . import clientsprites
from .definitions import style
from .lib.log import warning
from .lib.nofloat import PRECISION, square_of_distance
from .lib.screen import draw_line, draw_rect, get_screen
from .worldentity import COLLISION_RADIUS


# Fallback colors for automatic terrains that have an empty `color` field
# in style.txt. Improves visual differentiation for sighted players without
# touching the audio-only mode (Legge IA #8).
R_MIN = 4  # minimum unit circle radius in pixels (MAP-1)
UNIT_SCALE = 2.0  # visual multiplier for unit radius (MAP-SCALE-1, R7b)

# T2: vertical margin between the HUD resource bar (top of screen) and the
# top edge of the map viewport. Total offset is computed in
# `_update_coefs` from HudPanel.res_bar_height/margin + this margin.
HUD_MAP_MARGIN = 4

_AUTO_TERRAIN_FALLBACK = {
    "_meadows": (35, 80, 35),
    "_forest": (25, 65, 30),
    "_dense_forest": (15, 50, 25),
}


def terrain_color(terrain: str):
    color = style.get(terrain, "color", warn_if_not_found=False)
    try:
        color = pygame.Color(color[0])
    except (IndexError, TypeError,):
        color = _AUTO_TERRAIN_FALLBACK.get(terrain, (0, 25, 0))
    return color


def intensify(color):
    color = (color[0] * 2, color[1] * 2, color[2] * 2)
    color = tuple(min(x, 255) for x in color)
    return color


def square_color(square):
    color = terrain_color(square.type_name)
    if square.high_ground:
        color = intensify(color)
    return color


def fade(color):
    color = (color[0] / 10 + 15, color[1] / 10 + 15, color[2] / 10 + 15)
    return color


class GridView:
    def __init__(self, interface):
        self.interface = interface
        # T2: filled in by `_update_coefs`; offset (in pixels) applied to
        # the top of the map viewport so it does not overlap the HUD
        # resource bar drawn at y=0.
        self._y_offset = 0

    def _get_rect_from_map_coords(self, xc, yc):
        width, height = self.square_view_width, self.square_view_height
        left, top = xc * width, self._y_offset + self.ymax - (yc + 1) * height
        return left, top, width, height

    def _display(self):
        # map borders
        draw_rect(
            (100, 100, 100),
            (
                0,
                self._y_offset,
                self.square_view_width * (self.interface.xcmax + 1),
                self.square_view_height * (self.interface.ycmax + 1),
            ),
            1,
        )
        # backgrounds
        squares_to_view = []
        player = self.interface.player
        for xc in range(0, self.interface.xcmax + 1):
            for yc in range(0, self.interface.ycmax + 1):
                sq = player.world.grid[(xc, yc)]
                if sq in player.observed_squares or sq in player.observed_before_squares:
                    color = square_color(sq)
                    if sq not in player.observed_squares:
                        color = fade(color)
                    rect = self._get_rect_from_map_coords(xc, yc)
                    draw_rect(color, rect)
                    # PR-1: overlay terrain sprite if available; the
                    # draw_rect above remains as fallback when the
                    # sprite is missing (placeholder) or fails to load.
                    terrain_name = sq.type_name.lstrip("_")
                    terrain_sprite = clientsprites.get(
                        "terrain", terrain_name, self.square_view_width
                    )
                    if terrain_sprite is not None:
                        get_screen().blit(terrain_sprite, (rect[0], rect[1]))
                    squares_to_view.append(sq)
        # walls
        for sq in squares_to_view:
            exits = {e.o for e in sq.exits if not e.is_blocked()}
            walls = {-90, 90, 180, 0} - exits
            x, y = self._xy_coords(sq.x, sq.y)
            for color, borders in (((230, 230, 230), walls),):
                for o in borders:
                    dx = cos(radians(o)) * self.square_view_width / 2
                    dy = -sin(radians(o)) * self.square_view_width / 2
                    draw_line(
                        color, (x - dx - dy, y - dy - dx), (x - dx + dy, y - dy + dx)
                    )

    def _get_view_coords_from_world_coords(self, ox, oy):
        x = int(ox / self.interface.square_width * self.square_view_width)
        y = int(self._y_offset + self.ymax - oy / self.interface.square_width * self.square_view_height)
        return x, y

    def _object_coords(self, o):
        return self._get_view_coords_from_world_coords(o.x, o.y)

    def _xy_coords(self, ox, oy):
        return self._get_view_coords_from_world_coords(ox / 1000.0, oy / 1000.0)

    def screen_pos_of_square(self, square):
        """UI-MASTER-06 P2-MOVE-INDICATOR.

        Restituisce il centro geometrico di ``square`` in coordinate
        schermo (stesso sistema di ``square_from_mousepos``).

        Aggiorna i coefficienti di vista prima di proiettare, così la
        chiamata e' robusta anche se invocata fuori da un ciclo di
        rendering attivo (es. handler eventi mouse). Restituisce
        ``None`` se ``square`` non espone ``.x``/``.y`` validi.
        """
        if square is None:
            return None
        try:
            sx = square.x
            sy = square.y
        except AttributeError:
            return None
        self._update_coefs()
        return self._get_view_coords_from_world_coords(sx, sy)

    def display_object(self, o):
        if getattr(o, "is_inside", False):
            return
        if self.interface.target is not None and self.interface.target is o:
            width = 0  # fill circle
        else:
            width = 1
        x, y = self._object_coords(o)
        R_vis = max(R_MIN, int(R * UNIT_SCALE))
        # PR-2 / PR-3: try sprite blit first, fall back to the legacy
        # geometric rendering when no sprite is available. This keeps
        # behaviour identical for placeholders and for entities
        # without artwork (Legge IA #8: audio invariant; the fallback
        # is the previous code path verbatim).
        #
        # sprite_size is clamped to at least half the cell width so
        # that sprites are clearly visible even on small maps where
        # R_vis * 2 would produce a 16-pixel thumbnail.
        sprite_size = max(R_vis * 2, self.square_view_width // 2)
        category = clientsprites.category_of(o)
        sprite = (
            clientsprites.get(category, o.type_name, sprite_size)
            if category is not None
            else None
        )
        if o.shape() == "square":
            rect = x - R_vis, y - R_vis, R_vis * 2, R_vis * 2
            if sprite is not None:
                get_screen().blit(sprite, (x - sprite_size // 2, y - sprite_size // 2))
            else:
                draw_rect(o.corrected_color(), rect, width)
        else:
            if sprite is not None:
                get_screen().blit(sprite, (x - sprite_size // 2, y - sprite_size // 2))
            elif o.collision:
                pygame.draw.circle(get_screen(), o.corrected_color(), (x, y), R_vis, width)
            elif self.interface.target is not None and self.interface.target is o:
                pygame.draw.circle(get_screen(), o.corrected_color(), (x, y), R_vis, 0)
            else:
                get_screen().set_at((x, y), o.corrected_color())
        if getattr(o.model, "player", None) is not None:
            if o.id in self.interface.group:
                color = (0, 255, 0)
            elif o.player is self.interface.player:
                color = (60, 140, 60)
            elif o.player in self.interface.player.allied:
                color = (0, 0, 155)
            elif o.player.player_is_an_enemy(self.interface.player):
                color = (155, 0, 0)
            else:
                color = (180, 180, 180)
            pygame.draw.circle(get_screen(), color, (x, y), max(2, R_vis // 2), 0)
            if getattr(o, "hp", None) is not None and o.hp != o.hp_max:
                hp_prop = 100 * o.hp // o.hp_max
                if hp_prop > 80:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)
                W = max(3, R_vis - 2)
                if color != (0, 255, 0):
                    pygame.draw.line(
                        get_screen(),
                        (0, 55, 0),
                        (x - W, y - R_vis - 2),
                        (x - W + 2 * W, y - R_vis - 2),
                    )
                pygame.draw.line(
                    get_screen(),
                    color,
                    (x - W, y - R_vis - 2),
                    (x - W + hp_prop * (2 * W) // 100, y - R_vis - 2),
                )

    def display_objects(self):
        for o in list(self.interface.dobjets.values()):
            self.display_object(o)
            if (
                o.place is None
                and not o.is_inside
                and not (
                    self.interface.already_asked_to_quit or self.interface.end_loop
                )
            ):
                warning("%s.place is None", o.type_name)
                if o.is_memory:
                    warning("(memory)")

    def _hud_right_width(self) -> int:
        """Width reserved for the HUD right column plus margin."""
        return 303  # col_right_width=295 + margin=8 in HudPanel

    def _update_coefs(self):
        global R, R2
        screen = get_screen()
        sw, sh = screen.get_size()
        hud_right = self._hud_right_width()
        # T2: reserve vertical space at the top for the HUD resource bar.
        # UI-MASTER-03 T8-BOTTOMBAR: also reserve space at the bottom for
        # the new horizontal time/speed bar so the map never draws on top
        # of it. We import lazily to avoid a circular import (clientgamehud
        # also imports utilities from this module via the interface).
        from .clientgamehud import HudPanel
        self._y_offset = HudPanel.res_bar_height + 2 * HudPanel.margin + HUD_MAP_MARGIN
        bottom_reserved = HudPanel.bottom_bar_height + HudPanel.margin
        sh_effective = max(1, sh - self._y_offset - bottom_reserved)
        map_w = max(sw // 2, sw - hud_right)
        self.square_view_width = self.square_view_height = min(
            map_w // (self.interface.xcmax + 1),
            sh_effective // (self.interface.ycmax + 1),
        )
        self.ymax = self.square_view_height * (self.interface.ycmax + 1)
        R = max(
            1,
            int(
                COLLISION_RADIUS
                / PRECISION
                / self.interface.square_width
                * self.square_view_width
            ),
        )
        R = max(R, R_MIN)  # MAP-1: enforce minimum radius
        R2 = R * R

    def _collision_display(self):
        for t, c in (("ground", (0, 0, 255)), ("air", (255, 0, 0))):
            for ox, oy in self.interface.collision_debug[t].xy_set():
                pygame.draw.circle(get_screen(), c, self._xy_coords(ox, oy), 0, 0)

    def _display_active_zone_border(self):
        if self.interface.zoom_mode:
            zoom = self.interface.zoom
            left, bottom = self._xy_coords(zoom.xmin, zoom.ymin)
            right, top = self._xy_coords(zoom.xmax, zoom.ymax)
            rect = left, top, right - left, bottom - top
        else:
            rect = self._get_rect_from_map_coords(
                *self.interface.coords_in_map(self.interface.place)
            )
            rect = list(rect)
        if self.interface.target is None:
            color = (255, 255, 255)
        else:
            color = (200, 200, 200)
        draw_rect(color, rect, 2)

        # display the observer (camera position)
        observer_coordinates = self._get_view_coords_from_world_coords(self.interface.x, self.interface.y)
        pygame.draw.circle(get_screen(), (255, 230, 90), observer_coordinates, 4, 2)

    def display(self):
        self._update_coefs()
        self._display()
        self.display_objects()
        self._display_active_zone_border()
        if self.interface.collision_debug:
            self._collision_display()

    def invalidate_sprite_cache(self):
        """Drop cached sprites (call on resolution change).

        Round 16 hook: scaled surfaces are sized for the current
        ``square_view_width`` / ``R_vis``. After a resize the cache
        must be invalidated so that the next display() rescales from
        the source PNGs.
        """
        clientsprites.clear()

    def square_from_mousepos(self, pos):
        self._update_coefs()
        x, y = pos
        xc = x // self.square_view_width
        # T2: reverse the vertical offset applied to map drawing so that
        # mouse clicks at the very top of the map area resolve to the
        # correct grid square instead of going off-screen above it.
        yc = (self._y_offset + self.ymax - y) // self.square_view_height
        if 0 <= xc <= self.interface.xcmax and 0 <= yc <= self.interface.ycmax:
            return self.interface.server.player.world.grid[(xc, yc)]

    def object_from_mousepos(self, pos):
        self._update_coefs()
        x, y = pos
        for o in list(self.interface.dobjets.values()):
            xo, yo = self._object_coords(o)
            if square_of_distance(x, y, xo, yo) <= R2 + 1:  # is + 1 necessary?
                return o

    def units_from_mouserect(self, pos, pos2):
        result = []
        self._update_coefs()
        x, y = pos
        x2, y2 = pos2
        if x > x2:
            x, x2 = x2, x
        if y > y2:
            y, y2 = y2, y
        for o in self.interface.units():
            xo, yo = self._object_coords(o)
            if x < xo < x2 and y < yo < y2:
                result.append(o.id)
        return result

    def display_attack(self, attacker_id, target):
        a = self.interface.dobjets[attacker_id]
        self._update_coefs()
        R_vis = max(R_MIN, int(R * UNIT_SCALE))
        if self.interface.player.is_an_enemy(a):
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)
        r1 = pygame.draw.line(
            get_screen(),
            color,
            self._object_coords(target),
            self._object_coords(a),
        )
        r2 = pygame.draw.circle(
            get_screen(),
            (100, 100, 100),
            self._object_coords(target),
            R_vis * 3 // 2,
            0,
        )
        pygame.display.update(r1.union(r2))
