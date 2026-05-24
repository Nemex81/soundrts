import ctypes

import pygame
from pygame.locals import FULLSCREEN

from .. import version
from .log import warning

pygame.font.init()
_font = pygame.font.SysFont("arial", 20, bold=True)


def _make_font(size, bold):
    """Create a SysFont with safe fallback to the default `_font`."""
    try:
        return pygame.font.SysFont("arial", size, bold=bold)
    except Exception:
        return _font


_font_header = _make_font(24, True)
_font_small = _make_font(18, False)


def _render_with(font, text, dest, right=False, center=False, color=(200, 200, 200)):
    try:
        surface = font.render(text, True, color, (0, 0, 0))
    except Exception:
        surface = font.render(text[:160] + "...", True, color, (0, 0, 0))
    r = surface.get_rect()
    if right:
        if dest[0] == -1:
            dest = list(dest)
            dest[0] += pygame.display.get_surface().get_width()
        r.right, r.top = dest
    elif center:
        r.center = dest
    else:
        r = dest
    _screen.blit(surface, r)


def screen_render_header(text, dest, right=False, center=False, color=(220, 235, 245)):
    _render_with(_font_header, text, dest, right=right, center=center, color=color)


def screen_render_small(text, dest, right=False, center=False, color=(200, 200, 200)):
    _render_with(_font_small, text, dest, right=right, center=center, color=color)


def draw_line(color, xy1, xy2):
    pygame.draw.line(_screen, color, xy1, xy2, width=3)


def draw_rect(color, rect, width2=0):
    pygame.draw.rect(_screen, color, pygame.Rect(*rect), width2)


def _get_desktop_screen_mode():
    try:
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except:
        if pygame.display.get_init():
            warning("Info() must be called before set_mode()")
        pygame.display.init()
        i = pygame.display.Info()
        try:
            return i.current_w, i.current_h
        except:
            return 640, 480


def get_desktop_screen_mode():
    return _x, _y


def screen_render(text, dest, right=False, center=False, color=(200, 200, 200)):
    try:
        surface = _font.render(text, True, color, (0, 0, 0))
    except:
        surface = _font.render(text[:160] + "...", True, color, (0, 0, 0))
    r = surface.get_rect()
    if right:
        if dest[0] == -1:
            dest = list(dest)
            dest[0] += pygame.display.get_surface().get_width()
        r.right, r.top = dest
    elif center:
        r.center = dest
    else:
        r = dest
    _screen.blit(surface, r)


def _subtitle_position(screen, rendered_text):
    x = screen.get_width() - rendered_text.get_width() - 16
    y = screen.get_height() - rendered_text.get_height() - 4
    return x, y


def screen_render_subtitle():
    if not _subtitle:
        return
    ren = _font.render(_subtitle, True, (200, 200, 200), (0, 0, 0))
    _screen.blit(ren, _subtitle_position(_screen, ren))


def screen_subtitle_set(txt):
    global _subtitle
    _subtitle = txt
    if _game_mode:
        # render later
        pass
    else:
        get_screen().fill((0, 0, 0))
        screen_render_subtitle()
        pygame.display.flip()


def set_game_mode(m):
    global _game_mode
    _game_mode = m


def set_screen(fullscreen):
    global _screen
    if fullscreen:
        x, y = get_desktop_screen_mode()
        window_style = FULLSCREEN
    else:
        # Round 8: visual_mode attiva fullscreen anche fuori dal gameplay
        # (menu, opzioni, dialoghi). Import locale per evitare cicli.
        try:
            from .. import config as _config
            _visual = bool(getattr(_config, "visual_mode", 0))
        except Exception:
            _visual = False
        if _visual:
            x, y = get_desktop_screen_mode()
            window_style = FULLSCREEN
        elif version.IS_DEV_VERSION:
            x, y = 200, 200
            window_style = 0
        else:
            x, y = 400, 75
            window_style = 0
    try:
        _screen = pygame.display.set_mode((x, y), window_style)
    except:
        _screen = pygame.display.set_mode((640, 480))


def get_screen():
    return _screen


_x, _y = _get_desktop_screen_mode()
_screen = None
_game_mode = False
_subtitle = ""
