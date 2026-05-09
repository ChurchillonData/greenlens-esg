"""Load Guardian articles into evidence records."""

import json
from pathlib import Path

from greenlens.retrieval.source_weights import SOURCE_WEIGHTS


def make_record(article: dict, company_id: str, idx: int) -> dict:
    """Convert one Guardian article into an evidence record."""
    text = article.get("title", "") + ". " + (article.get("body", "") or article.get("trail", ""))
    return {
        "evidence_id": f"guardian_{company_id}_{idx:03d}",
        "source": "Guardian",
        "source_credibility": SOURCE_WEIGHTS["Guardian"],
        "url": article.get("url", ""),
        "date": article.get("date", ""),
        "applies_to": [company_id],
        "text": text,
    }


def load_company_articles(json_path: Path) -> list[dict]:
    """Load all articles for one company."""
    company_id = json_path.stem
    with open(json_path, encoding="utf-8-sig") as f:
        articles = json.load(f)
    return [make_record(art, company_id, i) for i, art in enumerate(articles)]


def load_all(guardian_dir: Path) -> list[dict]:
    """Load Guardian articles for all companies in the directory."""
    if not guardian_dir.exists():
        return []
    records = []
    for json_file in sorted(guardian_dir.glob("*.json")):
        records.extend(load_company_articles(json_file))
    return records