"""Append placeholder UI-MASTER-02b HUD keys to non-IT/EN style.txt."""
import pathlib

BLOCK = """tooltip_event_full {prefix} {text}
tooltip_map_entity {name} {hp} {owner} {order}
tooltip_map_hp HP: {hp}/{hp_max}
tooltip_map_owner [{owner}]
tooltip_map_coords ({col},{row})
entity_na ?
; TODO: tradurre (placeholder EN) - UI-MASTER-02b
"""

LANGS = [
    "ui-be", "ui-cs", "ui-de", "ui-es", "ui-fr", "ui-pl",
    "ui-pt-BR", "ui-ru", "ui-sk", "ui-vi", "ui-zh",
]

root = pathlib.Path(__file__).resolve().parents[1] / "res"
for lang in LANGS:
    p = root / lang / "style.txt"
    if not p.exists():
        print(f"missing {p}")
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    if "tooltip_event_full" in txt:
        print(f"skip {p}")
        continue
    with p.open("a", encoding="utf-8") as f:
        if not txt.endswith("\n"):
            f.write("\n")
        f.write(BLOCK)
    print(f"patched {p}")
