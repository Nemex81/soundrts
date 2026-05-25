"""Sprite cache for the SoundRTS Visual UI (Round 16).

This module exposes a tiny, lazy, headless-friendly cache that maps
``(category, name, size)`` triples to ``pygame.Surface`` instances
backed by PNG files under ``res/img/``. It is consumed by
``soundrts.clientgamegridview`` to draw entities and terrain as sprites
on top of the existing geometric primitives, which remain as a
fallback whenever a sprite is missing or unloadable.

Design constraints (Legge IA #8, R16):

* Audio-only invariant: this module is only imported by Visual UI code
  paths, so ``visual_mode=0`` never triggers a sprite load.
* Headless tests must not crash: every error path returns ``None``
  instead of raising, mirroring the pattern of ``soundrts.lib.sound``.
* Placeholder PNGs from Round 15-B (fully transparent RGBA) must
  behave as MISSING from the rendering point of view, so the
  geometric fallback kicks in for entities that have no real artwork
  yet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pygame

from .lib.log import warning


# ``soundrts/`` lives directly under the repository root; the sprite
# assets live at ``<repo>/res/img/<category>/<type_name>.png``.
_IMG_ROOT: Path = Path(__file__).resolve().parent.parent / "res" / "img"

# Cache keyed by ``"<category>/<name>@<size>"``. ``None`` is a
# negative cache entry (sprite known to be unavailable: missing file,
# load error, or fully transparent placeholder).
_cache: dict[str, Optional[pygame.Surface]] = {}


# Static category map for the 54 mandatory entities documented in
# ``tools/sprite_mapping.csv`` and ``doc_admin/round15_sprite_report.md``.
# Resolved at module import time to keep ``category_of`` free of
# runtime parsing of ``res/ui/style.txt`` (which mods may extend).
_UNITS: frozenset[str] = frozenset({
    "peasant", "footman", "zombie", "archer", "darkarcher", "skeleton",
    "knight", "catapult", "dragon", "mage", "priest", "necromancer",
    "new_flyingmachine", "flyingmachine", "boat", "destroyer",
    "battleship", "submarine",
})
_BUILDINGS: frozenset[str] = frozenset({
    "buildingsite", "farm", "lumbermill", "barracks", "townhall",
    "keep", "castle", "blacksmith", "stables", "workshop",
    "dragonslair", "magestower", "temple", "necropolis", "scouttower",
    "guardtower", "cannontower", "wall", "massive_wall", "gate",
    "massive_gate", "shipyard",
})
_RESOURCES: frozenset[str] = frozenset({"goldmine", "wood"})
_TERRAIN: frozenset[str] = frozenset({
    "meadows", "forest", "dense_forest", "river", "lake", "sea",
    "ocean", "mountain", "mountain_pass", "big_bridge", "ford", "marsh",
})


def _is_fully_transparent(surface: pygame.Surface) -> bool:
    """Return True iff a representative sample of pixels is fully
    transparent.

    Round 15-B generated transparent RGBA placeholders for entities
    with no Kenney counterpart. Treating those as "no sprite" lets
    the geometric fallback render them as before.

    We sample the four corners plus the center to avoid the heavy
    ``pygame.surfarray`` dependency on NumPy (not in the project
    requirements). This is sufficient for the uniformly-transparent
    placeholders produced by ``tools/normalize_sprites.py``.
    """
    w, h = surface.get_size()
    if w == 0 or h == 0:
        return True
    try:
        samples = (
            surface.get_at((0, 0))[3],
            surface.get_at((w - 1, 0))[3],
            surface.get_at((0, h - 1))[3],
            surface.get_at((w - 1, h - 1))[3],
            surface.get_at((w // 2, h // 2))[3],
        )
    except (pygame.error, IndexError):
        return False
    return all(a == 0 for a in samples)


def get(category: str, name: str, size: int) -> Optional[pygame.Surface]:
    """Return the sprite scaled to a ``(size, size)`` square, or None.

    Parameters
    ----------
    category:
        One of ``"units"``, ``"buildings"``, ``"resources"``,
        ``"terrain"``, ``"ui"``. Maps to the subdirectory of
        ``res/img/``.
    name:
        Filename stem (e.g. ``"peasant"``). Terrain callers must
        strip the leading underscore of auto-applied terrains
        (``"_meadows"`` → ``"meadows"``).
    size:
        Side length in pixels of the returned surface.

    Returns ``None`` when the file is missing, fails to load, or is
    a transparent placeholder. Callers must always handle ``None``
    by falling back to the geometric primitive.
    """
    if not category or not name or size <= 0:
        return None
    key = f"{category}/{name}@{size}"
    if key in _cache:
        return _cache[key]
    path = _IMG_ROOT / category / f"{name}.png"
    try:
        raw = pygame.image.load(str(path))
        try:
            surf = raw.convert_alpha()
        except pygame.error:
            # No display initialised (e.g. headless tests): keep the
            # software surface, callers will still be able to blit it.
            surf = raw
        if _is_fully_transparent(surf):
            _cache[key] = None
            return None
        scaled = pygame.transform.scale(surf, (size, size))
        _cache[key] = scaled
    except (FileNotFoundError, pygame.error, OSError) as exc:
        warning("SpriteCache miss for %s: %s", path, exc)
        _cache[key] = None
    return _cache[key]


def clear() -> None:
    """Invalidate the entire cache.

    Call this when the resolution changes so that previously scaled
    surfaces are discarded and reloaded at the new size.
    """
    _cache.clear()


def category_of(o: Any) -> Optional[str]:
    """Resolve the sprite category of a renderable game object.

    Returns ``"units"``, ``"buildings"``, ``"resources"`` or ``None``
    when the type is not mapped (no sprite available, geometric
    fallback only). Terrain is handled separately via the caller in
    ``GridView._display``.
    """
    type_name = getattr(o, "type_name", None)
    if not isinstance(type_name, str):
        return None
    if type_name in _UNITS:
        return "units"
    if type_name in _BUILDINGS:
        return "buildings"
    if type_name in _RESOURCES:
        return "resources"
    return None
