"""Round 8 - Visual UI: ScreenManager fullscreen per menu/dialoghi.

Gated da `config.visual_mode`: quando 0 (default) tutto e no-op e il
comportamento audio-only originale non viene mai toccato (LEGGE-1).

Lo stack visivo specchia lo stack di navigazione audio gia gestito da
`Menu` in `clientmenu.py` (LEGGE-3): qui non si decide la navigazione,
si rispecchia lo stato.
"""

from __future__ import annotations

from typing import Any, List, Optional

import pygame

from . import config
from .lib.screen import get_screen

# Palette layout fissa (header + body + footer)
HEADER_H = 80
FOOTER_H = 60
PADDING = 24
LINE_H = 44

COLOR_HEADER_BG = (20, 20, 35)
COLOR_HEADER_FG = (220, 235, 245)
COLOR_BODY_BG = (12, 12, 20)
COLOR_FOOTER_BG = (20, 20, 35)
COLOR_FOOTER_FG = (140, 140, 160)

COLOR_ITEM_BG = (25, 25, 40)
COLOR_ITEM_BORDER = (50, 50, 70)
COLOR_ITEM_FG = (180, 180, 200)
COLOR_ITEM_SEL_BG = (45, 90, 160)
COLOR_ITEM_SEL_BORDER = (100, 160, 255)
COLOR_ITEM_SEL_FG = (255, 255, 255)

COLOR_SCRIM = (0, 0, 0, 160)
COLOR_PANEL_BG = (30, 30, 50)
COLOR_PANEL_BORDER = (100, 160, 255)
COLOR_INPUT_BG = (15, 15, 25)
COLOR_INPUT_FG = (255, 255, 255)

FOOTER_HINT_MENU = "Up/Down Naviga   Enter Conferma   Esc Indietro   Ctrl+F2 Visivo OFF"
FOOTER_HINT_DIALOG = "Enter Conferma   Esc Annulla   Ctrl+F2 Visivo OFF"


def _safe_font(size: int, bold: bool = False) -> Optional["pygame.font.Font"]:
    """Crea un font Arial con fallback silenzioso. None se pygame non init."""
    if not pygame.font.get_init():
        try:
            pygame.font.init()
        except Exception:
            return None
    try:
        return pygame.font.SysFont("arial", size, bold=bold)
    except Exception:
        return None


class ScreenManager:
    """Stack di schermate visive. No-op completo se visual_mode=0 (LEGGE-1)."""

    def __init__(self) -> None:
        self._stack: List[Any] = []

    # --- stack -----------------------------------------------------------
    def push(self, screen: Any) -> None:
        if not config.visual_mode:
            return
        self._stack.append(screen)
        self._render_current()

    def pop(self) -> None:
        if not config.visual_mode:
            return
        if self._stack:
            self._stack.pop()
        self._render_current()

    @property
    def current(self) -> Optional[Any]:
        if not self._stack:
            return None
        return self._stack[-1]

    def update_current(self, title: Any, choices: Any, index: Optional[int]) -> None:
        """LEGGE-7: aggiornamento in-place senza push/pop (TrainingMenu)."""
        if not config.visual_mode:
            return
        cur = self.current
        if cur is None:
            return
        if hasattr(cur, "update_menu"):
            cur.update_menu(title, choices, index)
            self._render_current()

    def cleanup(self) -> None:
        """LEGGE-8: pulizia stato prima di SystemExit."""
        self._stack.clear()

    # --- input -----------------------------------------------------------
    def handle_mouse_motion(self, pos):
        if not config.visual_mode:
            return None
        cur = self.current
        if cur is None or not hasattr(cur, "handle_mouse_motion"):
            return None
        return cur.handle_mouse_motion(pos)

    def handle_mouse_click(self, pos):
        if not config.visual_mode:
            return None
        cur = self.current
        if cur is None or not hasattr(cur, "handle_mouse_click"):
            return None
        return cur.handle_mouse_click(pos)

    # --- render ----------------------------------------------------------
    def _render_current(self) -> None:
        if not config.visual_mode:
            return
        if get_screen() is None:
            return
        cur = self.current
        if cur is None or not hasattr(cur, "render"):
            return
        try:
            cur.render()
            pygame.display.flip()
        except Exception:
            # mai propagare errori di render nel path audio (LEGGE-2)
            pass


# Singleton di modulo
_screen_manager = ScreenManager()


def get_screen_manager() -> ScreenManager:
    return _screen_manager
