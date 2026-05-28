"""Apply Task 1 localization fix: add SET_SPEED_1..7, PAUSE_ON/OFF entries
to tts.txt of all languages, and add `pause_label` hud key to style.txt.

EN baseline: res/ui/ (already has 4367-4375).
IT: real translation.
Other 11 languages: EN placeholders with "# TODO: tradurre" comment.

This is a dev-tool, idempotent: re-running skips files that already contain
the entries.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "res"

IT_TTS = """
4367 Velocita 1 (molto lenta)
4368 Velocita 2 (lenta)
4369 Velocita 3 (normale)
4370 Velocita 4 (veloce)
4371 Velocita 5 (molto veloce)
4372 Velocita 6 (rapidissima)
4373 Velocita 7 (massima)
4374 Gioco in pausa
4375 Gioco ripreso
"""

# EN placeholders, used as fallback for all non-EN/IT languages.
PLACEHOLDER_TTS = """
; TODO: tradurre (placeholder EN)
4367 set speed to 1 very slow
4368 set speed to 2 slow
4369 set speed to 3 normal
4370 set speed to 4 fast
4371 set speed to 5
4372 set speed to 6 very fast
4373 set speed to 7 maximum
4374 game paused
4375 game resumed
"""

# style.txt hud additions (key = pause_label)
EN_HUD = "pause_label || PAUSED\n"
IT_HUD = "pause_label || IN PAUSA\n"
# Optional per-language translations for pause_label (others fall back via _hud_text default)
PER_LANG_HUD = {
    "ui-it": IT_HUD,
}


def append_tts(lang_dir: Path, content: str) -> bool:
    tts = lang_dir / "tts.txt"
    if not tts.exists():
        return False
    text = tts.read_text(encoding="utf-8", errors="replace")
    if "4367" in text:
        return False  # already present
    with tts.open("a", encoding="utf-8") as f:
        f.write(content)
    return True


def append_hud_key(style_path: Path, line: str) -> bool:
    if not style_path.exists():
        return False
    text = style_path.read_text(encoding="utf-8", errors="replace")
    if "pause_label" in text:
        return False
    # We append at the end of the file. Style files use `def hud` to start
    # the hud section and the section continues until the next `def` or EOF.
    # The simplest safe approach: insert at the end (assumes hud is the last
    # section, which holds for ui-it/style.txt and res/ui/style.txt).
    with style_path.open("a", encoding="utf-8") as f:
        if not text.endswith("\n"):
            f.write("\n")
        f.write(line)
    return True


def main() -> None:
    changed = []
    # 1) EN baseline already has 4367-4375; just add pause_label hud key.
    if append_hud_key(RES / "ui" / "style.txt", EN_HUD):
        changed.append("res/ui/style.txt: +pause_label")

    # 2) IT: real translations.
    if append_tts(RES / "ui-it", IT_TTS):
        changed.append("res/ui-it/tts.txt: +4367..4375 (IT)")
    if append_hud_key(RES / "ui-it" / "style.txt", IT_HUD):
        changed.append("res/ui-it/style.txt: +pause_label")

    # 3) Other languages: placeholders + TODO comment.
    other_langs = sorted(
        d.name for d in RES.iterdir()
        if d.is_dir() and d.name.startswith("ui-") and d.name != "ui-it"
    )
    for name in other_langs:
        lang_dir = RES / name
        if append_tts(lang_dir, PLACEHOLDER_TTS):
            changed.append(f"res/{name}/tts.txt: +4367..4375 (EN placeholder)")
        per_lang = PER_LANG_HUD.get(name, EN_HUD)
        if append_hud_key(lang_dir / "style.txt", per_lang):
            changed.append(f"res/{name}/style.txt: +pause_label")

    if not changed:
        print("Nothing to change (already up to date).")
    else:
        for line in changed:
            print(line)


if __name__ == "__main__":
    main()
