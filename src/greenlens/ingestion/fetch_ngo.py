"""Load curated NGO press releases from config/ngo_sources.yaml.

Fetches actual web content for each URL and stores it as a 'body' field.

Run as a script:
    python -m greenlens.ingestion.fetch_ngo           # fetch live content
    python -m greenlens.ingestion.fetch_ngo --dry-run # save titles only, no network
"""

import json
import sys
import time
from pathlib import Path

import yaml

from greenlens.config import CONFIG
from greenlens.ingestion.fetch_web import fetch_text


def load_curated() -> dict:
    """Read the curated NGO press release list."""
    path = Path(__file__).resolve().parents[3] / "config" / "ngo_sources.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def enrich_item(item: dict, dry_run: bool = False) -> dict:
    """Fetch body text for a press release item and add it as 'body'."""
    url = item.get("url", "")
    if not url or dry_run:
        return item
    print(f"    fetching {url[:90]}...")
    body = fetch_text(url)
    if body:
        return {**item, "body": body}
    print(f"    [warn] no content retrieved — falling back to title")
    return item


def save_source(source_id: str, items: list[dict], out_dir: Path) -> None:
    """Write one source's items to a JSON file."""
    out_path = out_dir / f"{source_id}.json"
    out_path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"  [ok] {source_id}: {len(items)} items -> {out_path.name}")


def fetch_all(dry_run: bool = False) -> None:
    """Save all curated sources to data/evidence/."""
    out_dir = Path(CONFIG["paths"]["evidence"])
    out_dir.mkdir(parents=True, exist_ok=True)

    curated = load_curated()
    for source_id, items in curated.items():
        print(f"\n{source_id} ({len(items)} items):")
        enriched = []
        for item in items:
            enriched.append(enrich_item(item, dry_run=dry_run))
            if not dry_run:
                time.sleep(1.2)  # polite crawl delay
        save_source(source_id, enriched, out_dir)

    print("\nDone.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("Dry-run mode: saving titles only, no network requests.")
    fetch_all(dry_run=dry_run)
