"""Simula PR-2/PR-3: verifica che get() restituisca Surface per entities reali."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from soundrts import clientsprites

# Simula gli entity type_names che appaiono in gioco
test_entities = [
    ("units", "peasant"),
    ("units", "footman"),
    ("units", "archer"),
    ("units", "knight"),
    ("units", "mage"),
    ("buildings", "townhall"),
    ("buildings", "barracks"),
    ("buildings", "farm"),
    ("resources", "wood"),
    ("resources", "goldmine"),
]

R_vis = 8  # typical value (R_MIN=4, R*UNIT_SCALE=8)
size = R_vis * 2  # = 16

print(f"Testing get() with size={size}")
clientsprites.clear()

ok = 0
none_count = 0
for cat, name in test_entities:
    surf = clientsprites.get(cat, name, size)
    status = "OK" if surf is not None else "NONE"
    if surf is not None:
        ok += 1
    else:
        none_count += 1
    print(f"  {status:4s}  {cat}/{name}@{size}")

print(f"\nSummary: {ok} sprites loaded, {none_count} None (placeholder/missing)")

# Verifica category_of con oggetto mock
class FakeEntity:
    type_name = "peasant"

for tn in ["peasant", "footman", "townhall", "barracks", "goldmine", "wood"]:
    obj = FakeEntity()
    obj.type_name = tn
    cat = clientsprites.category_of(obj)
    print(f"  category_of({tn!r}) = {cat!r}")
