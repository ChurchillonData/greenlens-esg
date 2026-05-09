"""Split parsed reports into sentences with page numbers.

Run as a script:
    python -m greenlens.nlp.split_sentences

Reads from data/processed/reports/<company>.txt
Writes to data/processed/reports/<company>_sentences.jsonl
"""

import json
import re
from pathlib import Path

import nltk

from greenlens.config import CONFIG

# Download punkt model on first run.
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def split_into_pages(text: str) -> list[tuple[int, str]]:
    """Split a report into (page_number, page_text) tuples."""
    pattern = r"--- PAGE (\d+) ---"
    parts = re.split(pattern, text)
    pages: list[tuple[int, str]] = []
    # parts looks like ["", "1", "<page 1 text>", "2", "<page 2 text>", ...]
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        page_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        pages.append((page_num, page_text))
    return pages


def split_into_sentences(text: str) -> list[str]:
    """Split a chunk of text into sentences using NLTK.

    Drops fragments and layout chrome:
    - shorter than 30 chars (page numbers, headers)
    - longer than 600 chars (multiple sections fused together)
    - more than 4 line breaks (layout block, not a sentence)
    - more than 40% uppercase letters (heading text)
    - not ending in .!? (incomplete fragments, TOC entries)
    Whitespace inside surviving sentences is collapsed to single spaces.
    """
    if not text.strip():
        return []
    sentences = nltk.sent_tokenize(text)
    cleaned: list[str] = []
    for s in sentences:
        s = " ".join(s.split())  # collapse whitespace
        if len(s) < 30 or len(s) > 600:
            continue
        if s.count("\n") > 4:
            continue
        if s[-1] not in ".!?":
            continue
        letters = [c for c in s if c.isalpha()]
        if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.4:
            continue
        cleaned.append(s)
    return cleaned


def process_report(report_path: Path) -> list[dict]:
    """Read a parsed report, return a list of sentence records."""
    text = report_path.read_text(encoding="utf-8")
    company_id = report_path.stem
    records: list[dict] = []
    for page_num, page_text in split_into_pages(text):
        for sentence in split_into_sentences(page_text):
            records.append({
                "company_id": company_id,
                "page": page_num,
                "sentence": sentence,
            })
    return records


def save_sentences(records: list[dict], out_path: Path) -> None:
    """Write sentence records as JSONL."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def split_all() -> None:
    """Split every parsed report into sentences."""
    in_dir = Path(CONFIG["paths"]["reports_processed"])
    txt_files = sorted(in_dir.glob("*.txt"))

    if not txt_files:
        print(f"No .txt reports found in {in_dir}. Run parse_reports.py first.")
        return

    for txt in txt_files:
        out_path = in_dir / f"{txt.stem}_sentences.jsonl"
        print(f"[split] {txt.name}")
        try:
            records = process_report(txt)
            save_sentences(records, out_path)
            print(f"[ok   ] {txt.stem}: {len(records)} sentences")
        except Exception as e:
            print(f"[fail ] {txt.stem}: {e}")


if __name__ == "__main__":
    split_all()