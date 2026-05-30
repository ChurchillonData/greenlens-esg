"""Run retrieval on every claim. Save matched evidence per claim.

Run as a script:
    python -m claimify.retrieval.run_retrieval

Reads embedded claims and corpus from data/outputs/embeddings/.
Writes data/outputs/retrieval.jsonl with one record per claim.
"""

import json
from pathlib import Path

import numpy as np

from claimify.config import CONFIG
from claimify.retrieval import rerank, sbert_search


def load_claims_with_vectors() -> tuple[list[dict], np.ndarray]:
    """Load claims and their embedding vectors."""
    base = Path(CONFIG["paths"]["outputs"]) / "embeddings"
    records = sbert_search.load_records(base / "claims_records.jsonl")
    vectors = np.load(base / "claims_vectors.npy")
    return records, vectors


def retrieve_for_claim(claim: dict, claim_vector: np.ndarray) -> dict:
    """Return the claim with its top-5 reranked evidence attached."""
    shortlist = sbert_search.search(claim_vector, claim["company_id"], k=20)
    top5 = rerank.rerank(claim["claim_text"], shortlist, top_n=5)
    return {
        **claim,
        "evidence": [
            {
                "evidence_id": ev["evidence_id"],
                "source": ev.get("source", ""),
                "source_credibility": ev.get("source_credibility", 0.0),
                "url": ev.get("url", ""),
                "date": ev.get("date", ""),
                "score": score,
                "text": ev["text"][:500],
            }
            for ev, score in top5
        ],
    }


def write_output(records: list[dict], out_path: Path) -> None:
    """Write retrieval results as JSONL."""
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def main() -> None:
    """Run retrieval over all claims."""
    claims, claim_vectors = load_claims_with_vectors()
    print(f"Retrieving evidence for {len(claims)} claims...")

    results = []
    for i, claim in enumerate(claims):
        if i % 100 == 0:
            print(f"  {i}/{len(claims)}")
        results.append(retrieve_for_claim(claim, claim_vectors[i]))

    out_path = Path(CONFIG["paths"]["outputs"]) / "retrieval.jsonl"
    write_output(results, out_path)
    print(f"\nWrote {len(results)} retrieval records to {out_path}")


if __name__ == "__main__":
    main()