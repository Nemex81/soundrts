"""Sprite normalization tool for SoundRTS Round 15-B.

Reads a curated mapping table that pairs each SoundRTS visual entity
(type_name) with a source PNG from the Kenney Medieval RTS pack.
For every entry the source file is opened with Pillow, converted to
RGBA, resized to the per-category target size with LANCZOS resampling,
and saved into ``res/img/<category>/<type_name>.png``.

For entries marked ``NO_MATCH`` (no semantically appropriate Kenney
sprite available, e.g. zombie, dragon, submarine) a fully transparent
RGBA placeholder of the target size is generated instead, so that the
output directory always contains the 54 mandatory files and the
SpriteCache contract from PLAN R15 is satisfied.

The script also writes ``tools/sprite_mapping.csv`` with one row per
mandatory sprite, recording source file, original size, final size,
RGBA mode, match level and final status. The CSV is the audit trail
consumed by ``tools/validate_sprites.py`` and by the human operator.

Constraints (Round 15-B):
* Only Pillow + stdlib. No pygame import in tooling.
* Pure dev-tool: lives under tools/, not under soundrts/.
* Idempotent: re-running overwrites existing files in res/img/.
* Output messages are plain-text, NVDA friendly. No emoji, no ASCII art.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - tooling environment guard
    print("ERRORE: Pillow non installata nel venv. Esegui: "
          ".venv\\Scripts\\python.exe -m pip install Pillow",
          file=sys.stderr)
    raise SystemExit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
KENNEY_ROOT = Path(r"C:\Users\nemex\Downloads\kenney_medievalRTSpack\PNG\Retina")
IMG_ROOT = REPO_ROOT / "res" / "img"
MAPPING_CSV = REPO_ROOT / "tools" / "sprite_mapping.csv"

CATEGORY_SIZE: dict[str, int] = {
    "units": 32,
    "buildings": 64,
    "resources": 32,
    "terrain": 64,
    "ui": 64,
}


@dataclass(frozen=True)
class Entry:
    """One row of the curated mapping table.

    Attributes
    ----------
    type_name:
        Filename stem produced in ``res/img/<category>/``. Matches the
        SoundRTS entity type identifier (peasant, footman, townhall...).
    category:
        One of ``units``, ``buildings``, ``resources``, ``terrain``,
        ``ui``. Drives the target output size.
    source:
        Filename inside the Kenney pack subfolder (e.g.
        ``medievalUnit_01.png``) or empty string for ``NO_MATCH``.
    kenney_subdir:
        Subfolder of ``KENNEY_ROOT`` containing ``source`` (Unit,
        Structure, Environment, Tile). Empty for ``NO_MATCH``.
    level:
        Match level: ``MEDIO`` for plausible-by-index mapping,
        ``NO_MATCH`` for placeholder, ``ALTO`` reserved for future
        verified visual matches.
    note:
        Free-text rationale. Logged to the CSV for operator review.
    """

    type_name: str
    category: str
    source: str
    kenney_subdir: str
    level: str
    note: str


# Mapping table.
#
# Match levels were assigned by Kenney pack inventory inspection
# (xml SubTexture sizes + filename convention) without per-sprite
# visual verification. Therefore every assigned entry is marked
# MEDIO and carries an explicit note recommending operator review.
# Entries with no plausible Kenney counterpart (undead, dragon,
# flying machines, naval, dragonslair, buildingsite, goldmine)
# are marked NO_MATCH and become transparent RGBA placeholders.
MAPPING: tuple[Entry, ...] = (
    # --- UNITS (18) ---
    Entry("peasant", "units", "medievalUnit_01.png", "Unit", "MEDIO",
          "indice 01 assunto come unita base team blu; richiede verifica visiva"),
    Entry("footman", "units", "medievalUnit_02.png", "Unit", "MEDIO",
          "indice 02 assunto come fante melee team blu"),
    Entry("archer", "units", "medievalUnit_03.png", "Unit", "MEDIO",
          "indice 03 assunto come arciere team blu"),
    Entry("knight", "units", "medievalUnit_04.png", "Unit", "MEDIO",
          "indice 04 assunto come cavaliere team blu"),
    Entry("mage", "units", "medievalUnit_05.png", "Unit", "MEDIO",
          "indice 05 assunto come caster team blu"),
    Entry("priest", "units", "medievalUnit_06.png", "Unit", "MEDIO",
          "indice 06 assunto come caster supporto team blu"),
    Entry("darkarcher", "units", "medievalUnit_15.png", "Unit", "MEDIO",
          "indice 15 assunto come arciere team rosso (variante scura)"),
    Entry("necromancer", "units", "medievalUnit_17.png", "Unit", "MEDIO",
          "indice 17 assunto come caster team rosso"),
    Entry("zombie", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("skeleton", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("catapult", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("dragon", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("new_flyingmachine", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("flyingmachine", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("boat", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("destroyer", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("battleship", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("submarine", "units", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),

    # --- BUILDINGS (22) ---
    Entry("townhall", "buildings", "medievalStructure_02.png", "Structure", "MEDIO",
          "indice 02 60x38 assunto come edificio centrale team blu"),
    Entry("keep", "buildings", "medievalStructure_03.png", "Structure", "MEDIO",
          "indice 03 52x34 assunto come mastio team blu"),
    Entry("castle", "buildings", "medievalStructure_09.png", "Structure", "MEDIO",
          "indice 09 56x60 assunto come castello grande"),
    Entry("barracks", "buildings", "medievalStructure_04.png", "Structure", "MEDIO",
          "indice 04 44x36 assunto come caserma team blu"),
    Entry("farm", "buildings", "medievalStructure_01.png", "Structure", "MEDIO",
          "indice 01 36x42 assunto come fattoria"),
    Entry("lumbermill", "buildings", "medievalStructure_05.png", "Structure", "MEDIO",
          "indice 05 44x42 assunto come segheria"),
    Entry("blacksmith", "buildings", "medievalStructure_10.png", "Structure", "MEDIO",
          "indice 10 44x40 assunto come fucina"),
    Entry("stables", "buildings", "medievalStructure_11.png", "Structure", "MEDIO",
          "indice 11 44x40 assunto come stalla"),
    Entry("workshop", "buildings", "medievalStructure_18.png", "Structure", "MEDIO",
          "indice 18 44x48 assunto come officina"),
    Entry("magestower", "buildings", "medievalStructure_12.png", "Structure", "MEDIO",
          "indice 12 20x36 torre alta assunta come torre dei maghi"),
    Entry("temple", "buildings", "medievalStructure_13.png", "Structure", "MEDIO",
          "indice 13 53x52 assunto come tempio"),
    Entry("necropolis", "buildings", "medievalStructure_14.png", "Structure", "MEDIO",
          "indice 14 63x63 assunto come necropoli (struttura grande scura)"),
    Entry("scouttower", "buildings", "medievalStructure_08.png", "Structure", "MEDIO",
          "indice 08 32x40 torre in legno"),
    Entry("guardtower", "buildings", "medievalStructure_22.png", "Structure", "MEDIO",
          "indice 22 32x40 torre in pietra team rosso"),
    Entry("cannontower", "buildings", "medievalStructure_16.png", "Structure", "MEDIO",
          "indice 16 44x60 torre alta con sommita armata"),
    Entry("wall", "buildings", "medievalStructure_06.png", "Structure", "MEDIO",
          "indice 06 60x38 assunto come sezione muro team blu"),
    Entry("massive_wall", "buildings", "medievalStructure_07.png", "Structure", "MEDIO",
          "indice 07 52x34 assunto come muro pesante team rosso"),
    Entry("gate", "buildings", "medievalStructure_15.png", "Structure", "MEDIO",
          "indice 15 62x64 assunto come cancello"),
    Entry("massive_gate", "buildings", "medievalStructure_21.png", "Structure", "MEDIO",
          "indice 21 60x60 assunto come cancello rinforzato"),
    Entry("shipyard", "buildings", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("dragonslair", "buildings", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),
    Entry("buildingsite", "buildings", "", "", "NO_MATCH",
          "nessuna impalcatura nel pack Kenney medievale base"),

    # --- RESOURCES (2) ---
    Entry("wood", "resources", "medievalEnvironment_12.png", "Environment", "MEDIO",
          "indice 12 38x35 cluster alberi assunto come bosco raccoglibile"),
    Entry("goldmine", "resources", "", "", "NO_MATCH",
          "non presente nel pack Kenney medievale base"),

    # --- TERRAIN (12) ---
    Entry("meadows", "terrain", "medievalTile_03.png", "Tile", "MEDIO",
          "indice 03 tile 64x64 assunto come prato base"),
    Entry("forest", "terrain", "medievalTile_15.png", "Tile", "MEDIO",
          "indice 15 tile 64x64 assunto come foresta rada"),
    Entry("dense_forest", "terrain", "medievalTile_18.png", "Tile", "MEDIO",
          "indice 18 tile 64x64 assunto come foresta fitta"),
    Entry("river", "terrain", "medievalTile_07.png", "Tile", "MEDIO",
          "indice 07 tile 64x64 acqua assunta come fiume"),
    Entry("lake", "terrain", "medievalTile_13.png", "Tile", "MEDIO",
          "indice 13 tile 64x64 acqua assunta come lago"),
    Entry("sea", "terrain", "medievalTile_19.png", "Tile", "MEDIO",
          "indice 19 tile 64x64 acqua assunta come mare"),
    Entry("ocean", "terrain", "medievalTile_20.png", "Tile", "MEDIO",
          "indice 20 tile 64x64 acqua scura assunta come oceano"),
    Entry("mountain", "terrain", "medievalTile_32.png", "Tile", "MEDIO",
          "indice 32 tile 64x64 assunto come montagna impassabile"),
    Entry("mountain_pass", "terrain", "medievalTile_27.png", "Tile", "MEDIO",
          "indice 27 tile 64x64 assunto come passo di montagna"),
    Entry("big_bridge", "terrain", "medievalTile_24.png", "Tile", "MEDIO",
          "indice 24 50x36 assunto come ponte"),
    Entry("ford", "terrain", "medievalTile_38.png", "Tile", "MEDIO",
          "indice 38 50x36 assunto come guado"),
    Entry("marsh", "terrain", "medievalTile_41.png", "Tile", "MEDIO",
          "indice 41 tile 64x64 assunto come palude"),
)


def _placeholder(size: int) -> Image.Image:
    """Return a fully transparent RGBA image of side ``size``."""
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def _normalize_one(entry: Entry) -> dict[str, str]:
    """Produce the output PNG for ``entry`` and return its CSV row."""
    target = CATEGORY_SIZE[entry.category]
    out_dir = IMG_ROOT / entry.category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{entry.type_name}.png"

    row = {
        "type_name": entry.type_name,
        "categoria": entry.category,
        "file_sorgente": entry.source,
        "size_originale": "",
        "size_finale": f"{target}x{target}",
        "modalita_rgba": "RGBA",
        "livello_match": entry.level,
        "note": entry.note,
        "status": "",
    }

    if entry.level == "NO_MATCH" or not entry.source:
        img = _placeholder(target)
        img.save(out_path, format="PNG")
        row["status"] = "PLACEHOLDER"
        return row

    src_path = KENNEY_ROOT / entry.kenney_subdir / entry.source
    if not src_path.exists():
        img = _placeholder(target)
        img.save(out_path, format="PNG")
        row["status"] = "PLACEHOLDER_SOURCE_MISSING"
        row["note"] = (entry.note + " | sorgente non trovata: "
                       + str(src_path))
        return row

    with Image.open(src_path) as src:
        src.load()
        row["size_originale"] = f"{src.width}x{src.height}"
        rgba = src.convert("RGBA")
        resized = rgba.resize((target, target), Image.LANCZOS)
        resized.save(out_path, format="PNG")
    row["status"] = "OK"
    return row


def main() -> int:
    """Generate all 54 sprites and the mapping CSV."""
    if not KENNEY_ROOT.exists():
        print(f"ATTENZIONE: pack Kenney non trovato in {KENNEY_ROOT}",
              file=sys.stderr)
        print("Tutti i file verranno generati come placeholder trasparenti.",
              file=sys.stderr)

    rows: list[dict[str, str]] = []
    counters = {"OK": 0, "PLACEHOLDER": 0,
                "PLACEHOLDER_SOURCE_MISSING": 0}

    for entry in MAPPING:
        row = _normalize_one(entry)
        rows.append(row)
        counters[row["status"]] = counters.get(row["status"], 0) + 1

    MAPPING_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MAPPING_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"TOTALE_TARGET: {len(MAPPING)}")
    print(f"OK: {counters.get('OK', 0)}")
    print(f"PLACEHOLDER: {counters.get('PLACEHOLDER', 0)}")
    print(f"PLACEHOLDER_SOURCE_MISSING: "
          f"{counters.get('PLACEHOLDER_SOURCE_MISSING', 0)}")
    print(f"CSV: {MAPPING_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
