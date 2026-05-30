"""Sample 150 claims for the eval set, stratified by company.

Run as a script:
    python -m claimify.eval.sample_claims

Reads claims with retrieved evidence from data/outputs/retrieval.jsonl.
Writes 150 sampled claims to data/eval/claims_to_label.jsonl.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

from claimify.config import CONFIG

CLAIMS_PER_COMPANY = 6
RANDOM_SEED = 42  # reproducibility


def load_claims_with_evidence() -> list[dict]:
    """Load claims with retrieved evidence."""
    path = Path(CONFIG["paths"]["outputs"]) / "retrieval.jsonl"
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def group_by_company(claims: list[dict]) -> dict[str, list[dict]]:
    """Group claims into a dict of company_id -> list of claims."""
    groups = defaultdict(list)
    for claim in claims:
        groups[claim["company_id"]].append(claim)
    return dict(groups)


def sample_one_company(claims: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Sample n claims from one company, or all if fewer exist."""
    if len(claims) <= n:
        return claims
    return rng.sample(claims, n)


def stratified_sample(claims_by_company: dict, n_per_company: int) -> list[dict]:
    """Sample n claims per company across all companies."""
    rng = random.Random(RANDOM_SEED)
    sampled = []
    for company_id in sorted(claims_by_company):
        sampled.extend(sample_one_company(claims_by_company[company_id], n_per_company, rng))
    return sampled


def write_sample(claims: list[dict], out_path: Path) -> None:
    """Write sampled claims as JSONL."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for c in claims:
            f.write(json.dumps(c) + "\n")


def main() -> None:
    """Sample claims and save to disk."""
    claims = load_claims_with_evidence()
    by_company = group_by_company(claims)

    print("Claims per company:")
    for cid in sorted(by_company):
        print(f"  {cid}: {len(by_company[cid])}")

    sampled = stratified_sample(by_company, CLAIMS_PER_COMPANY)
    out_path = Path(CONFIG["paths"]["eval"]) / "claims_to_label.jsonl"
    write_sample(sampled, out_path)

    print(f"\nSampled {len(sampled)} claims to {out_path}")
    print("Per-company sample size:")
    sampled_groups = group_by_company(sampled)
    for cid in sorted(sampled_groups):
        print(f"  {cid}: {len(sampled_groups[cid])}")


if __name__ == "__main__":
    main()