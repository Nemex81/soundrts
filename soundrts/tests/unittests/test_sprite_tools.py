"""Minimal unit tests for tools/normalize_sprites.py and tools/validate_sprites.py.

These tests guard the contract of the sprite pipeline introduced in
Round 15-B without re-running it against the real Kenney pack.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PIL = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

from tools import normalize_sprites as ns
from tools import validate_sprites as vs


def test_mapping_covers_54_mandatory_sprites() -> None:
    """The curated mapping must contain exactly 54 entries."""
    assert len(ns.MAPPING) == 54


def test_mapping_categories_are_known() -> None:
    """Every entry must belong to a category with a declared size."""
    for entry in ns.MAPPING:
        assert entry.category in ns.CATEGORY_SIZE, entry.type_name


def test_no_match_entries_have_empty_source() -> None:
    """NO_MATCH entries must not reference a Kenney source file."""
    for entry in ns.MAPPING:
        if entry.level == "NO_MATCH":
            assert entry.source == ""
            assert entry.kenney_subdir == ""


def test_placeholder_is_transparent_rgba(tmp_path: Path) -> None:
    """The placeholder helper must produce a fully transparent RGBA image."""
    img = ns._placeholder(32)
    assert img.mode == "RGBA"
    assert img.size == (32, 32)
    alpha = img.split()[-1]
    assert alpha.getextrema() == (0, 0)


def test_classify_missing_file(tmp_path: Path) -> None:
    """A non-existent file must classify as MANCANTE."""
    stato, _ = vs._classify(tmp_path / "does_not_exist.png", 32)
    assert stato == "MANCANTE"


def test_classify_wrong_size(tmp_path: Path) -> None:
    """A file with wrong dimensions must classify as ERRORE_FORMATO."""
    p = tmp_path / "wrong.png"
    Image.new("RGBA", (16, 16), (255, 0, 0, 255)).save(p)
    stato, _ = vs._classify(p, 32)
    assert stato == "ERRORE_FORMATO"


def test_classify_wrong_mode(tmp_path: Path) -> None:
    """A non-RGBA file must classify as ERRORE_FORMATO."""
    p = tmp_path / "rgb.png"
    Image.new("RGB", (32, 32), (255, 0, 0)).save(p)
    stato, _ = vs._classify(p, 32)
    assert stato == "ERRORE_FORMATO"


def test_classify_placeholder(tmp_path: Path) -> None:
    """A transparent RGBA at exact size must classify as PLACEHOLDER."""
    p = tmp_path / "ph.png"
    Image.new("RGBA", (32, 32), (0, 0, 0, 0)).save(p)
    stato, _ = vs._classify(p, 32)
    assert stato == "PLACEHOLDER"


def test_classify_ok(tmp_path: Path) -> None:
    """An opaque RGBA at exact size must classify as OK."""
    p = tmp_path / "ok.png"
    Image.new("RGBA", (32, 32), (10, 20, 30, 255)).save(p)
    stato, _ = vs._classify(p, 32)
    assert stato == "OK"
