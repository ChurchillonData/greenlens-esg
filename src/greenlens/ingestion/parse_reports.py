"""Parse downloaded PDFs to clean text using pdfminer.six.

Run as a script:
    python -m greenlens.ingestion.parse_reports

Reads from data/raw/reports/, writes to data/processed/reports/.
Uses LAParams tuned for multi-column corporate report layouts.
"""

from io import StringIO
from pathlib import Path

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from greenlens.config import CONFIG


def make_laparams() -> LAParams:
    """Layout parameters tuned for multi-column corporate reports."""
    return LAParams(
        line_margin=0.3,        # tighter line grouping within columns
        char_margin=2.0,        # standard char spacing
        word_margin=0.1,        # standard word spacing
        boxes_flow=0.5,         # balance horizontal vs vertical text flow
        detect_vertical=False,  # most reports are horizontal text only
    )


def extract_pages(pdf_path: Path) -> list[str]:
    """Extract text from a PDF page by page."""
    pages: list[str] = []
    laparams = make_laparams()
    # pdfminer.six doesn't expose per-page extraction in high_level cleanly,
    # so we extract the whole document and use form-feed (\f) as the page split.
    output = StringIO()
    with open(pdf_path, "rb") as f:
        extract_text_to_fp(f, output, laparams=laparams)
    full_text = output.getvalue()
    return full_text.split("\f")


def parse_one(pdf_path: Path, out_dir: Path) -> Path:
    """Parse one PDF, write text with page markers."""
    pages = extract_pages(pdf_path)
    chunks: list[str] = []
    for i, page_text in enumerate(pages, start=1):
        page_text = page_text.strip()
        if page_text:
            chunks.append(f"\n--- PAGE {i} ---\n{page_text}")
    out_path = out_dir / f"{pdf_path.stem}.txt"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(chunks), encoding="utf-8")
    return out_path


def parse_all() -> None:
    """Parse every PDF in data/raw/reports/."""
    raw_dir = Path(CONFIG["paths"]["reports_raw"])
    out_dir = Path(CONFIG["paths"]["reports_processed"])

    pdfs = sorted(raw_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in {raw_dir}. Run download_reports.py first.")
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