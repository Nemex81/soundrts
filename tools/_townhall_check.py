import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from pathlib import Path

f = Path("res/img/buildings/townhall.png")
s = pygame.image.load(str(f)).convert_alpha()
w, h = s.get_size()
stride = max(1, min(w, h) // 8)
print(f"townhall {w}x{h} stride={stride}")
non_zero = [
    (x, y, s.get_at((x, y))[3])
    for y in range(0, h, stride)
    for x in range(0, w, stride)
    if s.get_at((x, y))[3] > 0
]
print(f"opaque_in_stride_grid: {len(non_zero)}")
if non_zero:
    print(f"first few: {non_zero[:5]}")
print("DONE")
