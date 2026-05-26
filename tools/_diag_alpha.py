"""Diagnostic: verify alpha sampling on actual Kenney PNGs (R16-FIX)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from pathlib import Path

root = Path("res/img")
ok = 0
bad = 0
for cat in ["units", "buildings", "resources", "terrain"]:
    d = root / cat
    for png in sorted(d.glob("*.png")):
        surf = pygame.image.load(str(png)).convert_alpha()
        w, h = surf.get_size()
        samples = [
            surf.get_at((0, 0))[3],
            surf.get_at((w - 1, 0))[3],
            surf.get_at((0, h - 1))[3],
            surf.get_at((w - 1, h - 1))[3],
            surf.get_at((w // 2, h // 2))[3],
        ]
        is_ph = all(a == 0 for a in samples)
        # Count opaque pixels brute-force
        opaque = sum(1 for x in range(w) for y in range(h) if surf.get_at((x, y))[3] > 0)
        tag = "PLACEHOLDER" if is_ph else "OK"
        if is_ph and opaque > 0:
            tag = "FALSE_NEG"
            bad += 1
        else:
            ok += 1
        center_a = samples[4]
        print(f"{tag:12s}  {cat}/{png.name}  size={w}x{h}  opaque_px={opaque}  center_a={center_a}  corners={samples[:4]}")

print(f"\nSummary: OK={ok}  BAD(false neg)={bad}")
