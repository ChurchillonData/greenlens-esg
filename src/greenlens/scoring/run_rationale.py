"""Generate rationales for all scored claims.

Usage:
    python -m greenlens.scoring.run_rationale                      # all scored claims
    python -m greenlens.scoring.run_rationale --eval-only          # eval-set claims only
    python -m greenlens.scoring.run_rationale --claims-file PATH   # custom claim list

Reads from data/outputs/scored.jsonl
Writes to data/outputs/rationales.jsonl
"""

import json
import sys
from pathlib import Path

from greenlens.config import CONFIG
from greenlens.scoring.llm_scorer import get_client
from greenlens.scoring.rationale_generator import generate_rationale


def _get_claims_file() -> Path | None:
    """Parse --claims-file PATH from sys.argv, return Path or None."""
    for i, arg in enumerate(sys.argv):
        if arg == "--claims-file" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return None


def load_claim_texts_from(path: Path) -> set[str]:
    with open(path, encoding="utf-8-sig") as f:
        return {json.loads(line).get("claim_text", "") for line in f if line.strip()}


def load_scored(eval_only: bool, texts: set[str] | None = None) -> list[dict]:
    path = Path(CONFIG["paths"]["outputs"]) / "scored.jsonl"
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

    if texts is not None:
        filter_set = texts
    elif eval_only:
        eval_path = Path(CONFIG["paths"]["eval"]) / "claims_to_label.jsonl"
        filter_set = load_claim_texts_from(eval_path)
    else:
        return rows

    seen: set[str] = set()
    result = []
    for r in rows:
        ct = r.get("claim_text", "")
        if ct in filter_set and ct not in seen:
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
    claims_file = _get_claims_file()
    eval_only = "--eval-only" in sys.argv

    if claims_file:
        texts = load_claim_texts_from(claims_file)
        claims = load_scored(eval_only=False, texts=texts)
        print(f"Generating rationales for {len(claims)} claims from {claims_file.name}...")
    elif eval_only:
        claims = load_scored(eval_only=True)
        print(f"Generating rationales for {len(claims)} eval-set claims...")
    else:
        claims = load_scored(eval_only=False)
        print(f"Generating rationales for {len(claims)} scored claims...")

    run(claims)
    print("\nDone. Written to data/outputs/rationales.jsonl")


if __name__ == "__main__":
    main()
