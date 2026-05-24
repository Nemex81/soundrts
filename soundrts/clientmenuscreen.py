"""Round 8 - Visual UI: MenuScreen + DialogScreen + _label_to_str.

Tutti i metodi visivi sono gated da `config.visual_mode` (LEGGE-1).
`_label_to_str` non solleva mai eccezioni: token non traducibili saltati,
label vuota -> stringa vuota (LEGGE-4).
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

import pygame

from . import config
from . import msgparts as mp
from . import clientvisualui as vui
from .lib.screen import get_screen
from .lib.sound_cache import sounds


def _label_to_str(label: Any) -> str:
    """Converte una label SoundRTS (lista di token sound/str/int) in stringa.

    Mai solleva eccezioni: ogni token in try/except, token non traducibili
    saltati, label None o vuota -> "". (LEGGE-4)
    """
    if not label:
        return ""
    parts: List[str] = []
    try:
        iterator = iter(label)
    except Exception:
        return ""
    for token in iterator:
        try:
            if isinstance(token, str):
                # token speciali tipo "," o testo gia tradotto
                if token in (",", ".", ";"):
                    continue
                parts.append(token)
                continue
            # numero -> prova traduzione via sound_cache. Se torna un oggetto
            # Sound (non stringa) lo skippiamo: niente audio nel rendering.
            text = sounds.translate_sound_number(token)
            if isinstance(text, str) and text:
                parts.append(text)
        except Exception:
            # token sconosciuto: salta silenziosamente
            continue
    return " ".join(p for p in parts if p).strip()


class MenuScreen:
    """Rappresentazione visiva di un Menu audio (LEGGE-3 stack mirror)."""

    def __init__(self, title: Any, choices: List[Any], index: Optional[int]):
        self.title = title
        self.choices = list(choices) if choices else []
        self.index = index
        self._item_rects: List[Tuple[pygame.Rect, int]] = []
        self._dirty = True

    def update(self, index: Optional[int]) -> None:
        """Aggiorna solo l'indice selezionato (non ricostruisce la lista)."""
        if self.index != index:
            self.index = index
            self._dirty = True

    def update_menu(self, title: Any, choices: Any, index: Optional[int]) -> None:
        """LEGGE-7: ricostruzione lista in-place (TrainingMenu.update_menu)."""
        self.title = title
        self.choices = list(choices) if choices else []
        self.index = index
        self._dirty = True

    def render(self) -> None:
        if not config.visual_mode:
            return
        screen = get_screen()
        if screen is None:
            return
        w, h = screen.get_size()
        # header
        screen.fill(vui.COLOR_HEADER_BG, pygame.Rect(0, 0, w, vui.HEADER_H))
        # body
        body_y = vui.HEADER_H
        body_h = h - vui.HEADER_H - vui.FOOTER_H
        screen.fill(vui.COLOR_BODY_BG, pygame.Rect(0, body_y, w, body_h))
        # footer
        screen.fill(vui.COLOR_FOOTER_BG, pygame.Rect(0, h - vui.FOOTER_H, w, vui.FOOTER_H))

        font_h = vui._safe_font(24, True)
        font_i = vui._safe_font(20, True)
        font_s = vui._safe_font(16, False)

        if font_h is not None:
            title_text = _label_to_str(self.title) or _label_to_str(mp.MENU)
            surf = font_h.render(title_text, True, vui.COLOR_HEADER_FG)
            rect = surf.get_rect(center=(w // 2, vui.HEADER_H // 2))
            screen.blit(surf, rect)

        # voci: scroll auto centrato sull'indice
        self._item_rects.clear()
        if not self.choices:
            return
        sel = self.index if self.index is not None else 0
        # numero max di voci visibili
        max_items = max(1, (body_h - 2 * vui.PADDING) // vui.LINE_H)
        # finestra centrata su sel
        half = max_items // 2
        start = max(0, sel - half)
        end = min(len(self.choices), start + max_items)
        start = max(0, end - max_items)

        y = body_y + vui.PADDING
        for i in range(start, end):
            choice = self.choices[i]
            label = choice[0] if isinstance(choice, (list, tuple)) and choice else choice
            text = _label_to_str(label)
            is_sel = (i == sel)
            rect = pygame.Rect(vui.PADDING, y, w - 2 * vui.PADDING, vui.LINE_H - 6)
            bg = vui.COLOR_ITEM_SEL_BG if is_sel else vui.COLOR_ITEM_BG
            border = vui.COLOR_ITEM_SEL_BORDER if is_sel else vui.COLOR_ITEM_BORDER
            fg = vui.COLOR_ITEM_SEL_FG if is_sel else vui.COLOR_ITEM_FG
            screen.fill(bg, rect)
            pygame.draw.rect(screen, border, rect, 2 if is_sel else 1)
            if font_i is not None and text:
                surf = font_i.render(text, True, fg)
                screen.blit(surf, (rect.x + 12, rect.y + (rect.h - surf.get_height()) // 2))
            self._item_rects.append((rect, i))
            y += vui.LINE_H

        if font_s is not None:
            surf = font_s.render(_label_to_str(vui.FOOTER_HINT_MENU), True, vui.COLOR_FOOTER_FG)
            r = surf.get_rect(center=(w // 2, h - vui.FOOTER_H // 2))
            screen.blit(surf, r)

        self._dirty = False

    def handle_mouse_motion(self, pos) -> Optional[int]:
        """Ritorna il nuovo indice se cambiato, altrimenti None (LEGGE-6 additivo)."""
        if not config.visual_mode:
            return None
        for rect, idx in self._item_rects:
            if rect.collidepoint(pos):
                if idx != self.index:
                    self.index = idx
                    return idx
                return None
        return None

    def handle_mouse_click(self, pos) -> Optional[int]:
        """Ritorna l'indice cliccato (per conferma), altrimenti None."""
        if not config.visual_mode:
            return None
        for rect, idx in self._item_rects:
            if rect.collidepoint(pos):
                return idx
        return None


class DialogScreen:
    """Pannello fullscreen con scrim per input dialog."""

    def __init__(self, prompt: Any, current_input: str = ""):
        self.prompt = prompt
        self.current_input = current_input or ""

    def update_input(self, text: str) -> None:
        self.current_input = text or ""

    def render(self) -> None:
        if not config.visual_mode:
            return
        screen = get_screen()
        if screen is None:
            return
        w, h = screen.get_size()
        # base layout
        screen.fill(vui.COLOR_HEADER_BG, pygame.Rect(0, 0, w, vui.HEADER_H))
        body_y = vui.HEADER_H
        body_h = h - vui.HEADER_H - vui.FOOTER_H
        screen.fill(vui.COLOR_BODY_BG, pygame.Rect(0, body_y, w, body_h))
        screen.fill(vui.COLOR_FOOTER_BG, pygame.Rect(0, h - vui.FOOTER_H, w, vui.FOOTER_H))

        # scrim sul body
        scrim = pygame.Surface((w, body_h), pygame.SRCALPHA)
        scrim.fill(vui.COLOR_SCRIM)
        screen.blit(scrim, (0, body_y))

        # pannello centrato
        pw = min(800, max(400, w // 2))
        ph = min(300, max(180, body_h // 3))
        px = (w - pw) // 2
        py = body_y + (body_h - ph) // 2
        panel = pygame.Rect(px, py, pw, ph)
        screen.fill(vui.COLOR_PANEL_BG, panel)
        pygame.draw.rect(screen, vui.COLOR_PANEL_BORDER, panel, 2)

        font_h = vui._safe_font(22, True)
        font_i = vui._safe_font(20, False)
        font_s = vui._safe_font(16, False)

        if font_h is not None:
            ptext = _label_to_str(self.prompt) or ""
            if ptext:
                surf = font_h.render(ptext, True, vui.COLOR_HEADER_FG)
                screen.blit(surf, (px + 20, py + 20))

        input_rect = pygame.Rect(px + 20, py + ph - 80, pw - 40, 44)
        screen.fill(vui.COLOR_INPUT_BG, input_rect)
        pygame.draw.rect(screen, vui.COLOR_PANEL_BORDER, input_rect, 1)
        if font_i is not None:
            surf = font_i.render(self.current_input, True, vui.COLOR_INPUT_FG)
            screen.blit(surf, (input_rect.x + 8, input_rect.y + (input_rect.h - surf.get_height()) // 2))

        if font_s is not None:
            surf = font_s.render(_label_to_str(vui.FOOTER_HINT_DIALOG), True, vui.COLOR_FOOTER_FG)
            r = surf.get_rect(center=(w // 2, h - vui.FOOTER_H // 2))
            screen.blit(surf, r)

    # mouse no-op nei dialoghi
    def handle_mouse_motion(self, pos):
        return None

    def handle_mouse_click(self, pos):
        return None
