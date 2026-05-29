import pygame

my_cursors = {}


def record_cursor(name, center, strings):
    data, mask = pygame.cursors.compile(strings)
    my_cursors[name] = ((len(strings),) * 2, center, data, mask)


record_cursor(
    "square",
    (4, 4),
    (
        "XXXXXXXX",
        "X      X",
        "X      X",
        "X      X",
        "X      X",
        "X      X",
        "X      X",
        "XXXXXXXX",
    ),
)

record_cursor(
    "target",
    (4, 4),
    (
        "  XXXX  ",
        " X    X ",
        "X      X",
        "X  XX  X",
        "X  XX  X",
        "X      X",
        " X    X ",
        "  XXXX  ",
    ),
)

# UI-SIGHTED-02/SI-07: crosshair cursor surfaced when hovering over a
# hostile entity outside of an order-targeting workflow. Visually
# distinct from "target" (which is the inner-square reticle used while
# selecting a target for a queued order).
record_cursor(
    "attack",
    (4, 4),
    (
        "XX    XX",
        "XXX  XXX",
        " XXXXXX ",
        "  XXXX  ",
        "  XXXX  ",
        " XXXXXX ",
        "XXX  XXX",
        "XX    XX",
    ),
)

# UI-SIGHTED-03/SI-10: "move in every direction" cursor displayed while
# the player is drawing a rubber-band selection rectangle. The 8x8
# pattern evokes four diagonal arrows around a hollow centre — visually
# distinct from "attack" (solid corners) and "target" (centred reticle).
record_cursor(
    "sizeall",
    (4, 4),
    (
        " XX  XX ",
        "XXXXXXXX",
        " XX  XX ",
        "X      X",
        "X      X",
        " XX  XX ",
        "XXXXXXXX",
        " XX  XX ",
    ),
)


def set_cursor(name):
    """Apply ``name`` cursor. Defensive: unknown / unavailable cursor
    names are silently ignored so a missing pygame.cursors entry can
    never crash the input loop (LEGGE-4 / SI-07 portability)."""
    try:
        if name in my_cursors:
            cursor = my_cursors[name]
        else:
            cursor = getattr(pygame.cursors, name)
        pygame.mouse.set_cursor(*cursor)
    except Exception:
        pass
