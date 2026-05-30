"""Run LLM scoring on all claims with retrieved evidence.

Usage:
    python -m claimify.scoring.run_scoring                              # all claims
    python -m claimify.scoring.run_scoring --eval-only                  # eval set (60)
    python -m claimify.scoring.run_scoring --claims-file PATH           # custom claim list

Reads from data/outputs/retrieval.jsonl
Writes to data/outputs/scored.jsonl
"""

import json
import sys
from pathlib import Path

from claimify.config import CONFIG
from claimify.scoring.llm_scorer import get_client, score_claim


def load_retrieval() -> list[dict]:
    """Load claims with their retrieved evidence."""
    path = Path(CONFIG["paths"]["outputs"]) / "retrieval.jsonl"
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_claim_texts_from(path: Path) -> set[str]:
    """Return claim texts from a JSONL file (any file with a claim_text field)."""
    with open(path, encoding="utf-8-sig") as f:
        return {json.loads(line).get("claim_text", "") for line in f if line.strip()}


def filter_to_claims(claims: list[dict], texts: set[str]) -> list[dict]:
    """Keep only claims whose claim_text is in texts, deduplicating."""
    seen: set[str] = set()
    result = []
    for c in claims:
        ct = c.get("claim_text", "")
        if ct in texts and ct not in seen:
            seen.add(ct)
            result.append(c)
    return result


def _get_claims_file() -> Path | None:
    """Parse --claims-file PATH from sys.argv, return Path or None."""
    for i, arg in enumerate(sys.argv):
        if arg == "--claims-file" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return None


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
    """Score either all claims, the eval set, or a custom claim list."""
    claims = load_retrieval()

    claims_file = _get_claims_file()
    if claims_file:
        texts = load_claim_texts_from(claims_file)
        claims = filter_to_claims(claims, texts)
        print(f"Scoring {len(claims)} claims from {claims_file.name}...")
    elif "--eval-only" in sys.argv:
        eval_path = Path(CONFIG["paths"]["eval"]) / "claims_to_label.jsonl"
        texts = load_claim_texts_from(eval_path)
        claims = filter_to_claims(claims, texts)
        print(f"Scoring {len(claims)} eval-set claims...")
    else:
        print(f"Scoring {len(claims)} claims...")

    score_all(claims)
    print("\nDone.")


if __name__ == "__main__":
    main()