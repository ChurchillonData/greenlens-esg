"""Sample 20 claims per company from the retrieval corpus for the frontend.

Selects claims with category diversity, skipping fragments.
Writes to data/eval/frontend_claims.jsonl.

Usage:
    python -m greenlens.eval.sample_frontend
    python -m greenlens.eval.sample_frontend --n 20
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from greenlens.config import CONFIG

_MIN_CLAIM_LEN = 80
_DEFAULT_N = 20


def load_retrieval() -> list[dict]:
    path = Path(CONFIG["paths"]["outputs"]) / "retrieval.jsonl"
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def sample_company(claims: list[dict], n: int) -> list[dict]:
    """Round-robin sample across categories to maximise diversity."""
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for c in claims:
        if len(c.get("claim_text", "")) >= _MIN_CLAIM_LEN:
            by_cat[c.get("category", "unknown")].append(c)

    cats = sorted(by_cat)
    selected: list[dict] = []
    cat_pos = 0
    while len(selected) < n:
        found_any = False
        for _ in range(len(cats)):
            cat = cats[cat_pos % len(cats)]
            cat_pos += 1
            if by_cat[cat]:
                selected.append(by_cat[cat].pop(0))
                found_any = True
                if len(selected) >= n:
                    break
        if not found_any:
            break  # exhausted all categories

    return selected[:n]


def main() -> None:
    n = _DEFAULT_N
    for arg in sys.argv[1:]:
        if arg.startswith("--n="):
            n = int(arg.split("=")[1])
        elif arg == "--n":
            idx = sys.argv.index("--n")
            n = int(sys.argv[idx + 1])

    records = load_retrieval()
    print(f"Loaded {len(records)} retrieval records")

    by_company: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_company[r.get("company_id", "unknown")].append(r)

    out_path = Path(CONFIG["paths"]["eval"]) / "frontend_claims.jsonl"
    total = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for company in sorted(by_company):
            sampled = sample_company(by_company[company], n)
            for claim in sampled:
                f.write(json.dumps({"claim_text": claim["claim_text"]}, ensure_ascii=False) + "\n")
            print(f"  {company}: {len(sampled)} claims sampled")
            total += len(sampled)

    print(f"\nWrote {total} claims to {out_path}")


if __name__ == "__main__":
    main()
