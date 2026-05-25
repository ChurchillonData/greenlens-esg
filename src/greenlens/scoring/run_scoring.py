"""Run LLM scoring on all claims with retrieved evidence.

Usage:
    python -m greenlens.scoring.run_scoring                # all claims
    python -m greenlens.scoring.run_scoring --eval-only    # only eval set claims

Reads from data/outputs/retrieval.jsonl
Writes to data/outputs/scored.jsonl
"""

import json
import sys
from pathlib import Path

from greenlens.config import CONFIG
from greenlens.scoring.llm_scorer import get_client, score_claim


def load_retrieval() -> list[dict]:
    """Load claims with their retrieved evidence."""
    path = Path(CONFIG["paths"]["outputs"]) / "retrieval.jsonl"
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_eval_claim_texts() -> set[str]:
    """Return the set of claim_texts in the eval set, for --eval-only mode."""
    path = Path(CONFIG["paths"]["eval"]) / "claims_to_label.jsonl"
    with open(path, encoding="utf-8-sig") as f:
        return {json.loads(line).get("claim_text", "") for line in f if line.strip()}


def filter_to_eval(claims: list[dict], eval_texts: set[str]) -> list[dict]:
    """Keep only claims whose claim_text is in the eval set, one row per unique claim_text."""
    seen: set[str] = set()
    result = []
    for c in claims:
        ct = c.get("claim_text", "")
        if ct in eval_texts and ct not in seen:
            seen.add(ct)
            result.append(c)
    return result


def score_all(claims: list[dict]) -> list[dict]:
    """Score every claim. Save progress to disk as we go."""
    client = get_client()
    out_path = Path(CONFIG["paths"]["outputs"]) / "scored.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scored: list[dict] = []

    with open(out_path, "w", encoding="utf-8") as f:
        for i, claim in enumerate(claims):
            if i % 20 == 0:
                print(f"  {i}/{len(claims)}")
            try:
                result = score_claim(client, claim["claim_text"], claim.get("evidence", []))
                claim_with_score = {**claim, "predicted": result}
                scored.append(claim_with_score)
                f.write(json.dumps(claim_with_score) + "\n")
                f.flush()
            except Exception as e:
                print(f"  claim {i} failed: {e}")
    return scored


def main() -> None:
    """Score either all claims or just the eval set."""
    claims = load_retrieval()
    if "--eval-only" in sys.argv:
        eval_texts = load_eval_claim_texts()
        claims = filter_to_eval(claims, eval_texts)
        print(f"Scoring {len(claims)} eval-set claims...")
    else:
        print(f"Scoring {len(claims)} claims...")

    score_all(claims)
    print("\nDone.")


if __name__ == "__main__":
    main()