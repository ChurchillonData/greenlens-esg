"""Download sustainability report PDFs listed in config/companies.yaml.

Run as a script:
    python -m claimify.ingestion.download_reports

Saves PDFs to data/raw/reports/<company_id>.pdf.
HTML-only URLs are skipped with a message; download those by hand.
"""

from pathlib import Path

import requests

from claimify.companies import load_companies
from claimify.config import CONFIG


def is_pdf_url(url: str) -> bool:
    """Crude check: does the URL look like a direct PDF link."""
    return url.lower().endswith(".pdf")


def download_pdf(url: str, dest: Path) -> None:
    """Download a single PDF to dest, streaming to handle large files."""
    headers = {"User-Agent": "Claimify/0.1 (portfolio research project)"}
    response = requests.get(url, headers=headers, stream=True, timeout=60)
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def download_all() -> None:
    """Download every company's report. Skip HTML and already-downloaded files."""
    raw_dir = Path(CONFIG["paths"]["reports_raw"])
    skipped: list[str] = []

    for company in load_companies():
        cid = company["id"]
        url = company.get("report_url", "").strip()
        dest = raw_dir / f"{cid}.pdf"

        if not url or not is_pdf_url(url):
            print(f"[skip] {cid}: not a direct PDF URL, download manually to {dest}")
            skipped.append(cid)
            continue

        if dest.exists():
            print(f"[have] {cid}: already downloaded")
            continue

        print(f"[get ] {cid}: {url}")
        try:
            download_pdf(url, dest)
            print(f"[ok  ] {cid}: saved to {dest}")
        except requests.RequestException as e:
            print(f"[fail] {cid}: {e}")
            skipped.append(cid)

    if skipped:
        print(f"\nManual download needed for: {', '.join(skipped)}")
        print(f"Place the PDFs in {raw_dir}/ as <company_id>.pdf")


if __name__ == "__main__":
    download_all()