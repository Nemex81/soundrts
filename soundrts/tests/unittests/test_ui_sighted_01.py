"""Tests for UI-SIGHTED-01 round (sighted-player UX layer).

Coverage matrix:
  - SI-01 (context menu on right-click over own unit):
      * show_context_menu(None, pos) is a no-op (never raises)
      * show_context_menu(unit, pos) populates the menu from
        interface.orders() and stores items with the right keywords
      * ESC closes the menu via handle_context_menu_event
      * Click on a no-target item dispatches send_order(keyword,...)
        and flash_order fires; click outside closes the menu
      * Pause auto-closes any open menu on the next display() call
  - SI-04 (transient flashes for non-move orders):
      * flash_order registers an OrderFlash entry
      * Expired flashes are pruned on the next _draw_order_flashes
  - GridView.entity_at_mousepos: own unit returned, foreign unit and
    empty cell return None.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

import time

import pygame
import pytest

from soundrts.clientgamehud import (
    ContextMenu,
    ContextMenuItem,
    HudPanel,
    OrderFlash,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _make_order(keyword: str, nb_args: int = 0):
    """Minimal stand-in for OrderTypeView with the attributes the
    context-menu builder reads (cls.keyword, nb_args)."""
    cls = SimpleNamespace(keyword=keyword)
    return SimpleNamespace(cls=cls, nb_args=nb_args, title=[])


def _make_interface(orders=None, send_order=None, select_order=None):
    iface = MagicMock()
    iface.display_is_active = True
    iface.is_paused = False
    iface.resources = [100, 200]
    iface.used_food = 0
    iface.available_food = 10
    iface.last_virtual_time = 0
    iface.speed = 1.0
    iface._get_relative_speed = lambda: 1.0
    iface.group = []
    iface.dobjets = {}
    iface.player = SimpleNamespace(name="Tester", race=None, units=[])
    iface.orders = MagicMock(return_value=orders or [])
    iface.send_order = send_order or MagicMock()
    iface._select_order = select_order or MagicMock()
    return iface


def _make_hud(**kwargs):
    return HudPanel(_make_interface(**kwargs))


# ---------------------------------------------------------------------------
# SI-01 context menu
# ---------------------------------------------------------------------------


def test_show_context_menu_none_unit_is_noop():
    hud = _make_hud(orders=[_make_order("stop")])
    hud.show_context_menu(None, (100, 100))
    assert hud._context_menu is None


def test_show_context_menu_populates_items_from_interface_orders():
    orders = [_make_order("stop"), _make_order("attack", nb_args=1)]
    hud = _make_hud(orders=orders)
    unit = SimpleNamespace(id=42)
    hud.show_context_menu(unit, (120, 80))
    assert isinstance(hud._context_menu, ContextMenu)
    keywords = [i.keyword for i in hud._context_menu.items]
    assert keywords == ["stop", "attack"]
    # nb_args > 0 marks the item as needs_target.
    needs_target = {i.keyword: i.needs_target for i in hud._context_menu.items}
    assert needs_target == {"stop": False, "attack": True}


def test_show_context_menu_does_not_open_when_paused():
    iface_orders = [_make_order("stop")]
    hud = _make_hud(orders=iface_orders)
    hud.interface.is_paused = True
    hud.show_context_menu(SimpleNamespace(id=1), (10, 10))
    assert hud._context_menu is None


def test_handle_context_menu_event_escape_closes_menu():
    hud = _make_hud(orders=[_make_order("stop")])
    hud.show_context_menu(SimpleNamespace(id=1), (50, 50))
    assert hud._context_menu is not None
    ev = SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)
    consumed = hud.handle_context_menu_event(ev)
    assert consumed is True
    assert hud._context_menu is None


def test_click_on_no_target_item_dispatches_send_order_and_flashes():
    send = MagicMock()
    hud = _make_hud(orders=[_make_order("stop")], send_order=send)
    hud.show_context_menu(SimpleNamespace(id=1), (60, 60))
    # The first item rect lives at pos + padding; pick a point inside it.
    item_pos = (
        60 + hud._CTX_PADDING + 2,
        60 + hud._CTX_PADDING + 2,
    )
    ev = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=item_pos)
    consumed = hud.handle_context_menu_event(ev)
    assert consumed is True
    send.assert_called_once_with("stop", None, [])
    assert "stop" in hud._order_flashes
    assert hud._context_menu is None


def test_click_outside_menu_closes_it_without_dispatch():
    send = MagicMock()
    hud = _make_hud(orders=[_make_order("stop")], send_order=send)
    hud.show_context_menu(SimpleNamespace(id=1), (60, 60))
    far = (5, 5)
    ev = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=far)
    hud.handle_context_menu_event(ev)
    send.assert_not_called()
    assert hud._context_menu is None


def test_target_required_item_invokes_select_order():
    select = MagicMock()
    send = MagicMock()
    orders = [_make_order("attack", nb_args=1)]
    hud = _make_hud(orders=orders, send_order=send, select_order=select)
    hud.show_context_menu(SimpleNamespace(id=1), (60, 60))
    pos = (60 + hud._CTX_PADDING + 2, 60 + hud._CTX_PADDING + 2)
    ev = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
    hud.handle_context_menu_event(ev)
    select.assert_called_once()
    send.assert_not_called()


# ---------------------------------------------------------------------------
# SI-04 flash orders
# ---------------------------------------------------------------------------


def test_flash_order_registers_entry_for_known_keyword():
    hud = _make_hud()
    hud.flash_order("attack", (10, 20))
    assert "attack" in hud._order_flashes
    assert isinstance(hud._order_flashes["attack"], OrderFlash)


def test_flash_order_ignores_unknown_keyword():
    hud = _make_hud()
    hud.flash_order("build", (10, 20))  # build has no colour entry
    assert hud._order_flashes == {}


def test_expired_flash_is_pruned_on_draw():
    hud = _make_hud()
    hud.flash_order("stop", (10, 20))
    # Force the entry to have expired.
    flash = hud._order_flashes["stop"]
    hud._order_flashes["stop"] = OrderFlash(
        pos=flash.pos,
        color=flash.color,
        start=flash.start - 10.0,
        duration=flash.duration,
    )
    surf = pygame.Surface((100, 100))
    hud._draw_order_flashes(surf)
    assert "stop" not in hud._order_flashes


# ---------------------------------------------------------------------------
# GridView.entity_at_mousepos (SI-01 probe helper)
# ---------------------------------------------------------------------------


def _make_grid_view(object_returned, own_player):
    from soundrts.clientgamegridview import GridView

    iface = MagicMock()
    iface.player = own_player
    gv = GridView.__new__(GridView)
    gv.interface = iface
    gv.object_from_mousepos = MagicMock(return_value=object_returned)
    return gv


def test_entity_at_mousepos_returns_own_unit():
    player = SimpleNamespace(name="me")
    obj = SimpleNamespace(player=player)
    gv = _make_grid_view(obj, player)
    assert gv.entity_at_mousepos((0, 0)) is obj


def test_entity_at_mousepos_returns_none_for_foreign_unit():
    player = SimpleNamespace(name="me")
    enemy = SimpleNamespace(name="enemy")
    obj = SimpleNamespace(player=enemy)
    gv = _make_grid_view(obj, player)
    assert gv.entity_at_mousepos((0, 0)) is None


def test_entity_at_mousepos_returns_none_for_empty_cell():
    player = SimpleNamespace(name="me")
    gv = _make_grid_view(None, player)
    assert gv.entity_at_mousepos((0, 0)) is None
