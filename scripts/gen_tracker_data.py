"""Generate frontend JSON for the Commitment Tracker feature.

Reads data/historical/gap_scores.jsonl and outputs ALL scored pledges per
company, sorted by verdict priority (reversed first, then partially_fulfilled,
fulfilled, too_early) and confidence descending within each group.

Output: frontend/src/data/tracker.json
"""

import json
from collections import defaultdict
from pathlib import Path

IN_PATH  = Path("data/historical/gap_scores.jsonl")
OUT_PATH = Path("frontend/src/data/tracker.json")

COMPANY_LABELS = {
    "bp":             "BP",
    "chevron":        "Chevron",
    "conoco":         "ConocoPhillips",
    "eni":            "Eni",
    "equinor":        "Equinor",
    "exxon":          "ExxonMobil",
    "occidental":     "Occidental",
    "repsol":         "Repsol",
    "shell":          "Shell",
    "totalenergies":  "TotalEnergies",
}

VERDICT_ORDER = {"reversed": 0, "partially_fulfilled": 1, "fulfilled": 2, "too_early": 3}

# Category weights for accountability scoring.
# High-materiality pledges (net_zero, scope_3) count more when broken.
CATEGORY_WEIGHT = {
    "net_zero":              2.0,
    "scope_3":               1.8,
    "climate_lobbying":      1.6,
    "emissions_reduction":   1.5,
    "methane":               1.4,
    "renewables_investment": 1.2,
    "biodiversity":          1.1,
    "just_transition":       1.0,
    "other":                 1.0,
}

VERDICT_PENALTY = {"reversed": 1.0, "partially_fulfilled": 0.5, "fulfilled": 0.0}


def accountability_score(items: list[dict]) -> float | None:
    """0 = all high-materiality pledges reversed, 1 = all fulfilled.
    Returns None if no definitively scored pledges exist."""
    scored = [r for r in items if r.get("verdict") in VERDICT_PENALTY]
    if not scored:
        return None
    total_w = penalty_w = 0.0
    for r in scored:
        w    = CATEGORY_WEIGHT.get(r.get("category"), 1.0)
        conf = r.get("confidence") or 0.5
        wc   = w * conf
        total_w   += wc
        penalty_w += VERDICT_PENALTY[r["verdict"]] * wc
    if total_w == 0:
        return None
    return round(1.0 - penalty_w / total_w, 3)


def load_scores() -> list[dict]:
    if not IN_PATH.exists():
        raise FileNotFoundError(f"{IN_PATH} not found — run scripts/run_gap_scoring.py first")
    with open(IN_PATH, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def sort_pledges(items: list[dict]) -> list[dict]:
    return sorted(
        items,
        key=lambda r: (
            VERDICT_ORDER.get(r.get("verdict", "too_early"), 99),
            -(r.get("confidence") or 0.0),
        ),
    )


def format_record(r: dict) -> dict:
    evidence = r.get("evidence", [])
    key_idxs = r.get("key_evidence_idx") or []
    if key_idxs:
        ordered = sorted(key_idxs, key=lambda i: -(evidence[i]["score"] if i < len(evidence) else 0))
        ordered_evidence = [evidence[i] for i in ordered if i < len(evidence)]
        rest = [e for i, e in enumerate(evidence) if i not in key_idxs]
        ordered_evidence += rest
    else:
        ordered_evidence = sorted(evidence, key=lambda e: -e.get("score", 0))

    top_evidence = [
        {
            "source": e.get("source", ""),
            "url":    e.get("url", ""),
            "date":   e.get("date", ""),
            "text":   e["text"][:300].strip(),
        }
        for e in ordered_evidence[:2]
    ]

    return {
        "company_id":   r["company_id"],
        "report_year":  r.get("report_year", 2021),
        "category":     r.get("category"),
        "claim_text":   r["claim_text"],
        "target_value": r.get("target_value"),
        "target_unit":  r.get("target_unit"),
        "deadline_year":r.get("deadline_year"),
        "scope":        r.get("scope"),
        "verdict":      r.get("verdict"),
        "confidence":   r.get("confidence"),
        "rationale":    r.get("rationale"),
        "evidence":     top_evidence,
    }


def main() -> None:
    records = load_scores()
    print(f"Loaded {len(records)} scored claims")

    by_company: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_company[r["company_id"]].append(r)

    output = []
    for company_id in sorted(by_company.keys()):
        all_items = by_company[company_id]
        label = COMPANY_LABELS.get(company_id, company_id)
        counts = {
            "reversed":            sum(1 for r in all_items if r.get("verdict") == "reversed"),
            "partially_fulfilled": sum(1 for r in all_items if r.get("verdict") == "partially_fulfilled"),
            "too_early":           sum(1 for r in all_items if r.get("verdict") == "too_early"),
            "fulfilled":           sum(1 for r in all_items if r.get("verdict") == "fulfilled"),
        }
        acc = accountability_score(all_items)
        print(f"  {label:20} {len(all_items)} pledges  rev={counts['reversed']}  partial={counts['partially_fulfilled']}  upcoming={counts['too_early']}  fulfilled={counts['fulfilled']}  accountability={acc}")
        output.append({
            "company_id":          company_id,
            "company_label":       label,
            "total_analyzed":      len(all_items),
            "verdict_counts":      counts,
            "accountability_score": acc,
            "pledges":             [format_record(r) for r in sort_pledges(all_items)],
        })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total = sum(len(c["pledges"]) for c in output)
    print(f"\nWrote {total} pledges across {len(output)} companies -> {OUT_PATH}")


if __name__ == "__main__":
    main()
