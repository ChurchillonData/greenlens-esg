"""Parse downloaded PDFs to clean text.

Run as a script:
    python -m greenlens.ingestion.parse_reports

Reads from data/raw/reports/, writes to data/processed/reports/.
Output is plain text, one .txt file per company, with page markers.
"""

from pathlib import Path

import pdfplumber

from greenlens.config import CONFIG


def extract_text(pdf_path: Path) -> str:
    """Extract text from a PDF, with a marker between pages."""
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"\n--- PAGE {i} ---\n{text}")
    return "\n".join(pages)


def parse_one(pdf_path: Path, out_dir: Path) -> Path:
    """Parse a single PDF and write the cleaned text. Return output path."""
    company_id = pdf_path.stem
    out_path = out_dir / f"{company_id}.txt"
    text = extract_text(pdf_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def parse_all() -> None:
    """Parse every PDF in data/raw/reports/ to text."""
    raw_dir = Path(CONFIG["paths"]["reports_raw"])
    out_dir = Path(CONFIG["paths"]["reports_processed"])

    pdfs = sorted(raw_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {raw_dir}. Run download_reports.py first.")
        return

    for pdf_path in pdfs:
        print(f"[parse] {pdf_path.name}")
        try:
            out_path = parse_one(pdf_path, out_dir)
            size_kb = out_path.stat().st_size // 1024
            print(f"[ok   ] {pdf_path.stem}: {size_kb} KB of text")
        except Exception as e:
            print(f"[fail ] {pdf_path.stem}: {e}")


if __name__ == "__main__":
    parse_all()