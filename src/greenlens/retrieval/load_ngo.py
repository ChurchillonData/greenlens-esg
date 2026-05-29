"""Load NGO press releases and PDFs into evidence records."""

import json
from pathlib import Path

import pdfplumber

from greenlens.companies import load_companies
from greenlens.retrieval.source_weights import SOURCE_WEIGHTS

_CHUNK_WORDS = 350
_OVERLAP_WORDS = 50


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
        "text": (item.get("body") or item.get("title", ""))[:6000],
    }


def load_press_releases(json_path: Path, source: str) -> list[dict]:
    """Load press releases from a curated JSON file."""
    if not json_path.exists():
        return []
    with open(json_path, encoding="utf-8-sig") as f:
        items = json.load(f)
    return [make_press_record(item, source, i) for i, item in enumerate(items)]


def extract_pdf_text(pdf_path: Path, max_chars: int = 120000) -> str:
    """Extract text from a PDF, capped to max_chars."""
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
    return "\n".join(parts)[:max_chars]


def chunk_text(text: str, chunk_words: int = _CHUNK_WORDS, overlap_words: int = _OVERLAP_WORDS) -> list[str]:
    """Split text into overlapping word-count chunks.

    Each chunk is chunk_words words; adjacent chunks share overlap_words words.
    Short documents that fit in one chunk are returned as-is.
    """
    words = text.split()
    if len(words) <= chunk_words:
        return [text] if text.strip() else []

    chunks = []
    step = chunk_words - overlap_words
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_words])
        if chunk.strip():
            chunks.append(chunk)
        i += step
    return chunks


def pdf_applies_to(pdf_stem: str) -> list[str]:
    """Decide which companies a PDF applies to based on its filename."""
    companies = all_company_ids()
    if pdf_stem.startswith("sector_"):
        return companies
    if pdf_stem in companies:
        return [pdf_stem]
    return companies


def make_pdf_records(pdf: Path, source: str, folder: str, pdf_idx: int, url: str = "") -> list[dict]:
    """Convert one PDF into multiple evidence records, one per text chunk."""
    full_text = extract_pdf_text(pdf)
    chunks = chunk_text(full_text)
    applies = pdf_applies_to(pdf.stem)
    weight = SOURCE_WEIGHTS[source]
    return [
        {
            "evidence_id": f"{folder}_{pdf_idx:03d}_c{ci:03d}",
            "source": source,
            "source_credibility": weight,
            "url": url,
            "date": "",
            "applies_to": applies,
            "text": chunk,
        }
        for ci, chunk in enumerate(chunks)
    ]


def load_pdf_folder(folder_path: Path, source: str, pdf_urls: dict[str, str] | None = None) -> list[dict]:
    """Load all PDFs in a folder, splitting each into overlapping chunks.

    pdf_urls maps filename stem (e.g. "bp") to a URL string.
    """
    if not folder_path.exists():
        return []
    pdfs = sorted(folder_path.glob("*.pdf"))
    folder_name = folder_path.name
    records = []
    for i, pdf in enumerate(pdfs):
        url = (pdf_urls or {}).get(pdf.stem, "")
        chunks = make_pdf_records(pdf, source, folder_name, i, url=url)
        records.extend(chunks)
        print(f"    {pdf.name}: {len(chunks)} chunks")
    return records
