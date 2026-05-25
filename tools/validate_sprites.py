"""Sprite validation tool for SoundRTS Round 15-B.

Scans ``res/img/`` against the expected catalog (54 mandatory sprites
distributed across units, buildings, resources, terrain) declared in
``tools/normalize_sprites.MAPPING`` and produces a textual QA report
that is screen-reader friendly (no emoji, no ASCII art).

For every file the script verifies:
* presence at the expected path,
* RGBA mode (not just RGB or palette),
* exact size in pixels (32x32 or 64x64 per category),
* file size > 0 bytes.

Each entry is classified as one of:
* OK: present, RGBA, exact size, non-empty content (alpha not full zero),
* PLACEHOLDER: present, RGBA, exact size, fully transparent
  (alpha == 0 on every pixel),
* MANCANTE: file does not exist,
* ERRORE_FORMATO: file exists but mode or size is wrong, or load failed.

The summary plus per-file table is printed on stdout and written to
``tools/sprite_validation_report.txt`` (UTF-8).
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("ERRORE: Pillow non installata.", file=sys.stderr)
    raise SystemExit(2)

from tools.normalize_sprites import (
    CATEGORY_SIZE,
    IMG_ROOT,
    MAPPING,
    REPO_ROOT,
)

REPORT_PATH = REPO_ROOT / "tools" / "sprite_validation_report.txt"


def _classify(path: Path, target_size: int) -> tuple[str, str]:
    """Return ``(stato, dettaglio)`` for the file at ``path``."""
    if not path.exists():
        return "MANCANTE", "file non trovato"
    try:
        with Image.open(path) as img:
            img.load()
            if img.mode != "RGBA":
                return "ERRORE_FORMATO", f"mode={img.mode} atteso RGBA"
            if img.size != (target_size, target_size):
                return ("ERRORE_FORMATO",
                        f"size={img.size} atteso "
                        f"({target_size}, {target_size})")
            alpha = img.split()[-1]
            extrema = alpha.getextrema()
            if extrema == (0, 0):
                return "PLACEHOLDER", "alpha tutto 0"
            return "OK", f"alpha range {extrema}"
    except Exception as exc:  # noqa: BLE001 - tooling needs broad catch
        return "ERRORE_FORMATO", f"load fallito: {exc!r}"


def main() -> int:
    """Validate every mandatory sprite and emit the report."""
    lines: list[str] = []
    counters = {"OK": 0, "PLACEHOLDER": 0,
                "MANCANTE": 0, "ERRORE_FORMATO": 0}
    per_category: dict[str, dict[str, int]] = {}

    lines.append("SPRITE VALIDATION REPORT - SoundRTS Round 15-B")
    lines.append("=" * 60)
    lines.append("")
    lines.append("DETTAGLIO PER SPRITE")
    lines.append("-" * 60)

    for entry in MAPPING:
        target = CATEGORY_SIZE[entry.category]
        path = IMG_ROOT / entry.category / f"{entry.type_name}.png"
        stato, dettaglio = _classify(path, target)
        counters[stato] = counters.get(stato, 0) + 1
        cat = per_category.setdefault(
            entry.category,
            {"OK": 0, "PLACEHOLDER": 0,
             "MANCANTE": 0, "ERRORE_FORMATO": 0},
        )
        cat[stato] = cat.get(stato, 0) + 1
        lines.append(
            f"{entry.category}/{entry.type_name}.png  "
            f"-> {stato}  ({dettaglio})"
        )

    lines.append("")
    lines.append("SUMMARY PER CATEGORIA")
    lines.append("-" * 60)
    for cat in ("units", "buildings", "resources", "terrain"):
        c = per_category.get(cat, {})
        lines.append(
            f"{cat}: OK={c.get('OK', 0)} "
            f"PLACEHOLDER={c.get('PLACEHOLDER', 0)} "
            f"MANCANTE={c.get('MANCANTE', 0)} "
            f"ERRORE_FORMATO={c.get('ERRORE_FORMATO', 0)}"
        )

    totale_target = len(MAPPING)
    presenti = counters["OK"] + counters["PLACEHOLDER"]
    mancanti = counters["MANCANTE"]
    errori = counters["ERRORE_FORMATO"]

    if mancanti == 0 and errori == 0 and counters["OK"] >= totale_target // 2:
        stato_generale = "OK"
    elif mancanti == 0 and errori == 0:
        stato_generale = "ATTENZIONE"
    else:
        stato_generale = "CRITICO"

    lines.append("")
    lines.append("SUMMARY GLOBALE")
    lines.append("-" * 60)
    lines.append(f"TOTALE_TARGET: {totale_target}")
    lines.append(f"PRESENTI: {presenti}")
    lines.append(f"  di cui OK: {counters['OK']}")
    lines.append(f"  di cui PLACEHOLDER: {counters['PLACEHOLDER']}")
    lines.append(f"MANCANTI: {mancanti}")
    lines.append(f"ERRORI_FORMATO: {errori}")
    lines.append(f"STATO_GENERALE: {stato_generale}")

    report = "\n".join(lines) + "\n"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)

    return 0 if stato_generale != "CRITICO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
