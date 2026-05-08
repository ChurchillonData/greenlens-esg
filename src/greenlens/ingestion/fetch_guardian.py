"""Fetch Guardian articles for each company over the last 12 months.

Run as a script:
    python -m greenlens.ingestion.fetch_guardian

Saves one JSON file per company to data/evidence/guardian/<company_id>.json.
Each file contains a list of articles with title, date, url, and body text.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

from greenlens.companies import load_companies
from greenlens.config import CONFIG, get_api_key

API_URL = "https://content.guardianapis.com/search"


def build_query(keywords: list[str]) -> str:
    """Combine company keywords into a Guardian search query (OR logic)."""
    quoted = [f'"{k}"' if " " in k else k for k in keywords]
    return " OR ".join(quoted)


def fetch_page(query: str, page: int, from_date: str, api_key: str) -> dict:
    """Fetch one page of results from the Guardian search API."""
    params = {
        "q": query,
        "section": CONFIG["guardian"]["section"],
        "from-date": from_date,
        "page": page,
        "page-size": 50,
        "show-fields": "bodyText,trailText",
        "order-by": "newest",
        "api-key": api_key,
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["response"]


def parse_article(item: dict) -> dict:
    """Trim a Guardian API result to the fields we need."""
    fields = item.get("fields", {})
    return {
        "id": item["id"],
        "title": item["webTitle"],
        "date": item["webPublicationDate"],
        "url": item["webUrl"],
        "summary": fields.get("trailText", ""),
        "body": fields.get("bodyText", ""),
    }


def fetch_company(company: dict, api_key: str, from_date: str) -> list[dict]:
    """Fetch all articles for one company across paginated results."""
    query = build_query(company["keywords"])
    articles: list[dict] = []
    page = 1

    while True:
        data = fetch_page(query, page, from_date, api_key)
        articles.extend(parse_article(item) for item in data["results"])
        if page >= data["pages"] or page >= 10:  # cap at 500 articles
            break
        page += 1
        time.sleep(0.3)  # be polite to the API

    return articles


def fetch_all() -> None:
    """Fetch articles for every company in the registry."""
    api_key = get_api_key("GUARDIAN_API_KEY")
    out_dir = Path(CONFIG["paths"]["evidence"]) / "guardian"
    out_dir.mkdir(parents=True, exist_ok=True)

    lookback = CONFIG["guardian"]["lookback_days"]
    from_date = (datetime.now() - timedelta(days=lookback)).strftime("%Y-%m-%d")

    for company in load_companies():
        cid = company["id"]
        out_path = out_dir / f"{cid}.json"
        print(f"[get ] {cid}: searching from {from_date}")
        try:
            articles = fetch_company(company, api_key, from_date)
            out_path.write_text(json.dumps(articles, indent=2), encoding="utf-8")
            print(f"[ok  ] {cid}: {len(articles)} articles saved")
        except requests.RequestException as e:
            print(f"[fail] {cid}: {e}")


if __name__ == "__main__":
    fetch_all()