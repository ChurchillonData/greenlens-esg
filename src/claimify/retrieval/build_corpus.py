"""Consolidate evidence sources into a single corpus file.

Run as a script:
    python -m claimify.retrieval.build_corpus
"""

import json
from pathlib import Path

from claimify.config import CONFIG
from claimify.retrieval import load_guardian, load_ngo


def build() -> list[dict]:
    """Run all loaders and return the combined evidence records."""
    evidence_dir = Path(CONFIG["paths"]["evidence"])
    records = []

    print("Guardian:")
    g = load_guardian.load_all(evidence_dir / "guardian")
    print(f"  {len(g)} articles")
    records.extend(g)

    print("ClientEarth:")
    ce = load_ngo.load_press_releases(evidence_dir / "clientearth.json", "ClientEarth")
    print(f"  {len(ce)} releases")
    records.extend(ce)

    print("Global Witness:")
    gw = load_ngo.load_press_releases(evidence_dir / "global_witness.json", "Global Witness")
    print(f"  {len(gw)} releases")
    records.extend(gw)

    print("InfluenceMap:")
    im = load_ngo.load_pdf_folder(evidence_dir / "influencemap", "InfluenceMap", pdf_urls={
        "sector_methane-emissions_2025": "https://influencemap.org/briefing/EU-Methane-Regulation-Investor-Briefing-37683",
    })
    print(f"  {len(im)} PDFs")
    records.extend(im)

    print("Carbon Tracker:")
    ct = load_ngo.load_pdf_folder(evidence_dir / "carbon_tracker", "Carbon Tracker", pdf_urls={
        "net-zero":              "https://carbontracker.org/reports/regulating-unburnable-carbon/",
        "Paris-maligned-2026":   "https://carbontracker.org/reports/absolute-impact-2026/",
        "Paris-maligned-III-2025": "https://carbontracker.org/reports/paris-maligned-iii/",
    })
    print(f"  {len(ct)} PDFs")
    records.extend(ct)

    print("Reclaim Finance (press releases):")
    rf = load_ngo.load_press_releases(evidence_dir / "reclaim_finance.json", "Reclaim Finance")
    print(f"  {len(rf)} releases")
    records.extend(rf)

    print("Reclaim Finance (PDFs):")
    rf_pdf = load_ngo.load_pdf_folder(evidence_dir / "reclaim_finance", "Reclaim Finance", pdf_urls={
        "bp":    "https://reclaimfinance.org/site/wp-content/uploads/2025/04/BP-Assessment-2025.pdf",
        "shell": "https://reclaimfinance.org/site/wp-content/uploads/2025/05/202504_Shell_Climate-Strategy-Assessment.pdf",
    })
    print(f"  {len(rf_pdf)} PDFs")
    records.extend(rf_pdf)

    print("TPI:")
    tpi = load_ngo.load_press_releases(evidence_dir / "tpi.json", "TPI")
    print(f"  {len(tpi)} releases")
    records.extend(tpi)

    return [r for r in records if r.get("text", "").strip()]


def write_corpus(records: list[dict], out_path: Path) -> None:
    """Write records as one JSON object per line."""
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def main() -> None:
    """Build the corpus and write it to disk."""
    records = build()
    out_path = Path(CONFIG["paths"]["evidence"]) / "corpus.jsonl"
    write_corpus(records, out_path)
    print(f"\nWrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()