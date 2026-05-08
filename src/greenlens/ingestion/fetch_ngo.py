"""Load curated NGO press releases from config/ngo_sources.yaml.

No scraping. Reads the hand-curated list and saves to data/evidence/.

Run as a script:
    python -m greenlens.ingestion.fetch_ngo
"""

import json
from pathlib import Path

import yaml

from greenlens.config import CONFIG


def load_curated() -> dict:
    """Read the curated NGO press release list."""
    path = Path(__file__).resolve().parents[3] / "config" / "ngo_sources.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def save_source(source_id: str, items: list[dict], out_dir: Path) -> None:
    """Write one source's items to a JSON file."""
    out_path = out_dir / f"{source_id}.json"
    out_path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"[ok  ] {source_id}: {len(items)} items saved")


def fetch_all() -> None:
    """Save all curated sources to data/evidence/."""
    out_dir = Path(CONFIG["paths"]["evidence"])
    out_dir.mkdir(parents=True, exist_ok=True)

    curated = load_curated()
    for source_id, items in curated.items():
        save_source(source_id, items, out_dir)


if __name__ == "__main__":
    fetch_all()