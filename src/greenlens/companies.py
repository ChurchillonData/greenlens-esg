"""Load the company registry from config/companies.yaml."""

from pathlib import Path

import yaml


def load_companies() -> list[dict]:
    """Read all ten companies from the registry."""
    path = Path(__file__).resolve().parents[2] / "config" / "companies.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["companies"]


def get_company(company_id: str) -> dict:
    """Look up a single company by its id."""
    for company in load_companies():
        if company["id"] == company_id:
            return company
    raise ValueError(f"Unknown company id: {company_id}")