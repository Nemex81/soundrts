"""Apply Task 3 + Task 4 localization: add EVENTS_SHOWN/HIDDEN (4376-4377)
and ACTIVITY_PANEL_*/TAB_* (4378-4383) to tts.txt of all languages, plus
extra `def hud` keys used by the activity panel.

Idempotent: re-running skips files already containing the new IDs.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "res"

IT_TTS = """
4376 Eventi mostrati
4377 Eventi nascosti
4378 Pannello attivita aperto
4379 Pannello attivita chiuso
4380 Tutto
4381 Addestramento
4382 Ricerche
4383 Costruzioni
"""

PLACEHOLDER_TTS = """
; TODO: tradurre (placeholder EN)
4376 events shown
4377 events hidden
4378 activity panel open
4379 activity panel closed
4380 all
4381 training
4382 research
4383 buildings
"""

# Extra hud keys (used by clientgamehud.py for the activity panel and
# the events panel hint). Default EN values; IT overrides below.
EN_HUD_EXTRA = (
    "panel_activity || ACTIVITY\n"
    "tab_all || ALL\n"
    "tab_training || TRAIN\n"
    "tab_research || RESEARCH\n"
    "tab_build || BUILD\n"
    "events_collapsed || (hidden)\n"
    "activity_empty || (no active production)\n"
)
IT_HUD_EXTRA = (
    "panel_activity || ATTIVITA\n"
    "tab_all || TUTTO\n"
    "tab_training || ADDESTR.\n"
    "tab_research || RICERCHE\n"
    "tab_build || COSTR.\n"
    "events_collapsed || (nascosti)\n"
    "activity_empty || (nessuna produzione attiva)\n"
)
PER_LANG_HUD_EXTRA = {"ui-it": IT_HUD_EXTRA}


def append_tts(lang_dir: Path, content: str, marker: str) -> bool:
    tts = lang_dir / "tts.txt"
    if not tts.exists():
        return False
    text = tts.read_text(encoding="utf-8", errors="replace")
    if marker in text:
        return False
    with tts.open("a", encoding="utf-8") as f:
        f.write(content)
    return True


def append_hud_block(style_path: Path, block: str, marker: str) -> bool:
    if not style_path.exists():
        return False
    text = style_path.read_text(encoding="utf-8", errors="replace")
    if marker in text:
        return False
    with style_path.open("a", encoding="utf-8") as f:
        if not text.endswith("\n"):
            f.write("\n")
        f.write(block)
    return True


def main() -> None:
    changed = []

    # EN baseline: TTS already added below, hud keys added here.
    en_tts = RES / "ui" / "tts.txt"
    en_text = en_tts.read_text(encoding="utf-8", errors="replace") if en_tts.exists() else ""
    if "\n4376" not in en_text and "4376 " not in en_text:
        # Add EN baseline (English) using placeholders content (English).
        if append_tts(RES / "ui", PLACEHOLDER_TTS.replace("; TODO: tradurre (placeholder EN)\n", "; T3/T4 events panel + activity panel TTS\n"), "4376"):
            changed.append("res/ui/tts.txt: +4376..4383 (EN)")
    if append_hud_block(RES / "ui" / "style.txt", EN_HUD_EXTRA, "panel_activity"):
        changed.append("res/ui/style.txt: +activity hud keys")

    # IT translations
    if append_tts(RES / "ui-it", IT_TTS, "4376"):
        changed.append("res/ui-it/tts.txt: +4376..4383 (IT)")
    if append_hud_block(RES / "ui-it" / "style.txt", IT_HUD_EXTRA, "panel_activity"):
        changed.append("res/ui-it/style.txt: +activity hud keys")

    # Other languages
    other_langs = sorted(
        d.name for d in RES.iterdir()
        if d.is_dir() and d.name.startswith("ui-") and d.name != "ui-it"
    )
    for name in other_langs:
        lang_dir = RES / name
        if append_tts(lang_dir, PLACEHOLDER_TTS, "4376"):
            changed.append(f"res/{name}/tts.txt: +4376..4383 (EN placeholder)")
        per_lang = PER_LANG_HUD_EXTRA.get(name, EN_HUD_EXTRA)
        # Only append hud block if style.txt has the hud section (i.e. it
        # already contains the previous pause_label key). For languages
        # with no style.txt we rely on the EN baseline.
        sp = lang_dir / "style.txt"
        if sp.exists() and "pause_label" in sp.read_text(encoding="utf-8", errors="replace"):
            if append_hud_block(sp, per_lang, "panel_activity"):
                changed.append(f"res/{name}/style.txt: +activity hud keys")

    if not changed:
        print("Nothing to change (already up to date).")
    else:
        for line in changed:
            print(line)


if __name__ == "__main__":
    main()
