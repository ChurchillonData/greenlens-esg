"""Generate rationales for all scored claims.

Usage:
    python -m greenlens.scoring.run_rationale               # all scored claims
    python -m greenlens.scoring.run_rationale --eval-only   # eval-set claims only

Reads from data/outputs/scored.jsonl
Writes to data/outputs/rationales.jsonl
"""

import json
import sys
from pathlib import Path

from greenlens.config import CONFIG
from greenlens.scoring.llm_scorer import get_client
from greenlens.scoring.rationale_generator import generate_rationale


def load_scored(eval_only: bool) -> list[dict]:
    path = Path(CONFIG["paths"]["outputs"]) / "scored.jsonl"
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if not eval_only:
        return rows
    eval_path = Path(CONFIG["paths"]["eval"]) / "claims_to_label.jsonl"
    eval_texts = {
        json.loads(l).get("claim_text", "")
        for l in open(eval_path, encoding="utf-8-sig")
        if l.strip()
    }
    seen: set[str] = set()
    result = []
    for r in rows:
        ct = r.get("claim_text", "")
        if ct in eval_texts and ct not in seen:
            seen.add(ct)
            result.append(r)
    return result


def run(claims: list[dict]) -> None:
    client = get_client()
    out_path = Path(CONFIG["paths"]["outputs"]) / "rationales.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        for i, claim in enumerate(claims):
            if i % 20 == 0:
                print(f"  {i}/{len(claims)}")
            predicted = claim.get("predicted", {})
            try:
                rationale = generate_rationale(
                    client,
                    claim_text=claim.get("claim_text", ""),
                    evidence=claim.get("evidence", []),
                    predicted_class=predicted.get("class", ""),
                    risk_score=predicted.get("risk_score", 0.5),
                    classifier_reasoning=predicted.get("reasoning", ""),
                )
                output = {**claim, "rationale": rationale}
                f.write(json.dumps(output, ensure_ascii=False) + "\n")
                f.flush()
            except Exception as e:
                print(f"  claim {i} failed: {e}")


def main() -> None:
    eval_only = "--eval-only" in sys.argv
    claims = load_scored(eval_only)
    scope = "eval-set" if eval_only else "all scored"
    print(f"Generating rationales for {len(claims)} {scope} claims...")
    run(claims)
    print("\nDone. Written to data/outputs/rationales.jsonl")


if __name__ == "__main__":
    main()
