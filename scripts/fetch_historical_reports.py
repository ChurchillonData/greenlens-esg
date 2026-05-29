"""Download 2021 sustainability/climate reports for all 10 companies.

Run from the project root:
    python scripts/fetch_historical_reports.py
"""

import time
from pathlib import Path

import requests

OUT_DIR = Path("data/historical")
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,*/*",
}

REPORTS = [
    {
        "company": "bp",
        "year": 2021,
        "label": "BP CDP Climate Change Questionnaire 2021",
        "url": "https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/sustainability/group-reports/bp-cdp-climate-change-questionnaire-2021.pdf",
    },
    {
        "company": "shell",
        "year": 2021,
        "label": "Shell Sustainability Report 2021",
        "url": "https://www.shell.com/sustainability/reporting-centre/reporting-centre-archive/_jcr_content/root/main/section_2106585602/tabs/tab_598795121/text_copy_copy_copy_/links/item0.stream/1742906404689/177c3ffdf8569f5b4ded34845ba698da7b44cac3/shell-sustainability-report-2021.pdf",
    },
    {
        "company": "totalenergies",
        "year": 2021,
        "label": "TotalEnergies Climate Roadmap in Action 2021",
        "url": "https://totalenergies.com/system/files/documents/2021-02/climate_roadmap_in_action.pdf",
    },
    {
        "company": "equinor",
        "year": 2021,
        "label": "Equinor Sustainability Report 2021",
        "url": "https://www.equinor.com/content/dam/statoil/documents/sustainability-reports/2021/sustainaiblity-report-2021-equinor.pdf",
    },
    {
        "company": "exxon",
        "year": 2021,
        "label": "ExxonMobil Advancing Climate Solutions 2021",
        "url": "https://corporate.exxonmobil.com/-/media/global/files/advancing-climate-solutions/2021-advancing-climate-solutions-progress-report.pdf",
    },
    {
        "company": "chevron",
        "year": 2021,
        "label": "Chevron Climate Change Resilience Report 2021",
        "url": "https://www.chevron.com/-/media/chevron/sustainability/documents/climate-change-resilience-report-7-21.pdf",
    },
    {
        "company": "conoco",
        "year": 2021,
        "label": "ConocoPhillips CDP Climate Change Report 2021",
        "url": "https://static.conocophillips.com/files/resources/2021-cdp-climate-change-report.pdf",
    },
    {
        "company": "eni",
        "year": 2021,
        "label": "Eni for 2021 – Sustainability Performance",
        "url": "https://www.eni.com/assets/documents/eng/just-transition/2021/eni-for-2021-sustainability-performance-eng.pdf",
    },
    {
        "company": "repsol",
        "year": 2021,
        "label": "Repsol ESG Engagement Report 2020-2021",
        "url": "https://www.repsol.com/content/dam/repsol-corporate/en_gb/accionistas-e-inversores/pdfs/annual-esg-engagement-report-2020-2021.pdf",
    },
    {
        "company": "occidental",
        "year": 2021,
        "label": "Occidental (Oxy) Sustainability Report 2021",
        "url": "https://www.oxy.com/siteassets/documents/publications/2021-sustainability-report-web.pdf",
    },
]


def download(report: dict) -> bool:
    dest = OUT_DIR / f"{report['company']}_{report['year']}.pdf"
    if dest.exists():
        print(f"  SKIP  {dest.name} (already exists)")
        return True
    try:
        resp = requests.get(report["url"], headers=HEADERS, timeout=60, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "pdf" not in content_type and "octet" not in content_type and "stream" not in content_type:
            # Some servers return HTML error pages with 200 status
            first_bytes = b""
            for chunk in resp.iter_content(256):
                first_bytes = chunk
                break
            if first_bytes and first_bytes[:4] != b"%PDF":
                print(f"  FAIL  {report['company']} — not a PDF (got {content_type})")
                return False
            # Re-open with fresh request since we consumed the stream check
            resp = requests.get(report["url"], headers=HEADERS, timeout=60, stream=True)

        size = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
                size += len(chunk)
        kb = size // 1024
        print(f"  OK    {dest.name}  ({kb} KB)  — {report['label']}")
        return True
    except Exception as e:
        print(f"  FAIL  {report['company']} — {e}")
        return False


def main() -> None:
    print(f"Downloading {len(REPORTS)} reports to {OUT_DIR}/\n")
    failed = []
    for r in REPORTS:
        ok = download(r)
        if not ok:
            failed.append(r)
        time.sleep(1.5)

    print(f"\n{'='*50}")
    print(f"Downloaded: {len(REPORTS) - len(failed)}/{len(REPORTS)}")
    if failed:
        print("\nFailed — need manual download:")
        for r in failed:
            print(f"  {r['company']:15} {r['label']}")
            print(f"  {'':15} {r['url']}")


if __name__ == "__main__":
    main()
