"""Round 13 - SOSPESO-B: localized hint tokens 4365/4366 catalog coverage.

Verifies that VISUAL_MENU_HINT (4365) and VISUAL_DIALOG_HINT (4366) are
present in every UI catalog under res/ui-XX/tts.txt. This protects against
silent regressions where new locales would fallback to English.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RES_DIR = REPO_ROOT / "res"

# All locale folders whose tts.txt must include hint tokens.
LOCALE_DIRS = sorted(
    p.name for p in RES_DIR.iterdir()
    if p.is_dir() and p.name.startswith("ui") and (p / "tts.txt").exists()
)

REQUIRED_TOKENS = ("4365", "4366")


def _read_tokens(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    tokens: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        head = line.split(" ", 1)[0]
        if head.isdigit():
            tokens.add(head)
    return tokens


@pytest.mark.parametrize("locale_dir", LOCALE_DIRS)
@pytest.mark.parametrize("token", REQUIRED_TOKENS)
def test_locale_catalog_has_visual_hint_token(locale_dir: str, token: str) -> None:
    """Each ui-XX/tts.txt must define hint tokens 4365 and 4366."""
    path = RES_DIR / locale_dir / "tts.txt"
    tokens = _read_tokens(path)
    assert token in tokens, f"{locale_dir}/tts.txt missing token {token}"


def test_locale_catalogs_discovered() -> None:
    """Sanity check: discovery returned at least the expected core locales."""
    # ui (EN fallback) + ui-it must always be present.
    assert "ui" in LOCALE_DIRS
    assert "ui-it" in LOCALE_DIRS
