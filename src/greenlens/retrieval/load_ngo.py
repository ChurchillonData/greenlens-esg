"""Load NGO press releases and PDFs into evidence records."""

import json
from pathlib import Path

import pdfplumber

from greenlens.companies import load_companies
from greenlens.retrieval.source_weights import SOURCE_WEIGHTS


def all_company_ids() -> list[str]:
    """Return the list of all company ids from the registry."""
    return [c["id"] for c in load_companies()]


def make_press_record(item: dict, source: str, idx: int) -> dict:
    """Convert one press release into an evidence record."""
    slug = source.lower().replace(" ", "_")
    return {
        "evidence_id": f"{slug}_{idx:03d}",
        "source": source,
        "source_credibility": SOURCE_WEIGHTS[source],
        "url": item.get("url", ""),
        "date": item.get("date", ""),
        "applies_to": item.get("companies", all_company_ids()),
        "text": item.get("title", ""),
    }


def load_press_releases(json_path: Path, source: str) -> list[dict]:
    """Load press releases from a curated JSON file."""
    if not json_path.exists():
        return []
    with open(json_path, encoding="utf-8-sig") as f:
        items = json.load(f)
    return [make_press_record(item, source, i) for i, item in enumerate(items)]


def extract_pdf_text(pdf_path: Path, max_chars: int = 50000) -> str:
    """Extract text from a PDF, capped to max_chars."""
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
    return "\n".join(parts)[:max_chars]


def pdf_applies_to(pdf_stem: str) -> list[str]:
    """Decide which companies a PDF applies to based on its filename."""
    companies = all_company_ids()
    if pdf_stem.startswith("sector_"):
        return companies
    if pdf_stem in companies:
        return [pdf_stem]
    return companies


def make_pdf_record(pdf: Path, source: str, folder: str, idx: int) -> dict:
    """Convert one PDF into an evidence record."""
    return {
        "evidence_id": f"{folder}_{idx:03d}",
        "source": source,
        "source_credibility": SOURCE_WEIGHTS[source],
        "url": "",
        "date": "",
        "applies_to": pdf_applies_to(pdf.stem),
        "text": extract_pdf_text(pdf),
    }


def load_pdf_folder(folder_path: Path, source: str) -> list[dict]:
    """Load all PDFs in a folder."""
    if not folder_path.exists():
        return []
    pdfs = sorted(folder_path.glob("*.pdf"))
    folder_name = folder_path.name
    return [make_pdf_record(pdf, source, folder_name, i) for i, pdf in enumerate(pdfs)]