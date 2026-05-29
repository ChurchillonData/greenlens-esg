"""Score historical climate pledges against current evidence.

Pipeline:
  1. Load historical claims from data/historical/claims/*.jsonl
  2. Embed with SBERT (reuses same model as main pipeline)
  3. Retrieve top evidence from existing corpus
  4. LLM gap scoring: fulfilled / partially_fulfilled / reversed / too_early
  5. Write data/historical/gap_scores.jsonl

Usage:
    python scripts/run_gap_scoring.py               # all companies
    python scripts/run_gap_scoring.py bp shell      # specific companies
"""

import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from greenlens.config import CONFIG, get_api_key
from greenlens.retrieval import rerank, sbert_search

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CLAIMS_DIR = Path("data/historical/claims")
OUT_PATH = Path("data/historical/gap_scores.jsonl")
SBERT_MODEL = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = "gpt-4o-mini"

# Claims to score per company: prioritise by deadline proximity + specificity.
# We score all claims with deadline_year set; the LLM filters noise.
MAX_CLAIMS_PER_COMPANY = 999  # no cap — all go through retrieval

GAP_SYSTEM_PROMPT = """You assess whether an oil and gas company has followed through on a climate commitment made in their 2021 sustainability report.

You will receive:
1. A historical pledge from 2021
2. Current evidence (2023–2025) from independent sources (NGO reports, investigative journalism)

Your job: assign one of four verdicts:
- "fulfilled": strong evidence the target was met or substantially on track
- "partially_fulfilled": some progress but clearly not meeting the stated commitment
- "reversed": evidence the company has weakened, abandoned, or contradicted the pledge
- "too_early": deadline not yet reached and insufficient evidence to judge — use sparingly

Return a JSON object:
{
  "verdict": "fulfilled" | "partially_fulfilled" | "reversed" | "too_early",
  "confidence": 0.0-1.0,
  "rationale": "2-3 sentence explanation citing specific evidence numbers [1], [2] etc.",
  "key_evidence_idx": [0, 1]
}

Be direct. If evidence is sparse, lean toward "too_early" over a forced verdict. If the company has clearly retreated from a pledge (e.g., dropped net-zero target, cut capex), use "reversed" even without a direct statement.
"""


# ---------------------------------------------------------------------------
# Step 1: Load historical claims
# ---------------------------------------------------------------------------

def load_historical_claims(company_filter: list[str] | None = None) -> list[dict]:
    claims = []
    for path in sorted(CLAIMS_DIR.glob("*_claims.jsonl")):
        company_id = path.stem.rsplit("_", 2)[0]
        if company_filter and company_id not in company_filter:
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    claims.append(json.loads(line))
    return claims


# ---------------------------------------------------------------------------
# Step 2: Embed historical claims
# ---------------------------------------------------------------------------

def embed_claims(claims: list[dict]) -> np.ndarray:
    print(f"Loading SBERT ({SBERT_MODEL})...")
    model = SentenceTransformer(SBERT_MODEL)
    texts = [c["claim_text"] for c in claims]
    print(f"Embedding {len(texts)} historical claims...")
    return model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)


# ---------------------------------------------------------------------------
# Step 3: Retrieve evidence per claim
# ---------------------------------------------------------------------------

def retrieve_evidence(claim: dict, vector: np.ndarray) -> list[dict]:
    shortlist = sbert_search.search(vector, claim["company_id"], k=20)
    top5 = rerank.rerank(claim["claim_text"], shortlist, top_n=5)
    return [
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
    ]


# ---------------------------------------------------------------------------
# Step 4: LLM gap scoring
# ---------------------------------------------------------------------------

def format_claim(claim: dict) -> str:
    parts = [f'"{claim["claim_text"]}"']
    parts.append(f'Category: {claim.get("category", "unknown")}')
    if claim.get("target_value") is not None:
        parts.append(f'Target: {claim["target_value"]} {claim.get("target_unit", "")}')
    if claim.get("deadline_year"):
        parts.append(f'Deadline: {claim["deadline_year"]}')
    if claim.get("scope"):
        parts.append(f'Scope: {claim["scope"]}')
    return "\n".join(parts)


def score_gap(client: OpenAI, claim: dict, evidence: list[dict]) -> dict:
    numbered_evidence = "\n".join(
        f"[{i+1}] ({ev.get('source', '')}, {ev.get('date', 'n.d.')}) {ev['text']}"
        for i, ev in enumerate(evidence)
    )
    user_content = (
        f"HISTORICAL PLEDGE (2021 — {claim.get('company_id', '').upper()}):\n"
        f"{format_claim(claim)}\n\n"
        f"CURRENT EVIDENCE (2023–2025):\n{numbered_evidence}"
    )
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": GAP_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    company_filter = sys.argv[1:] if len(sys.argv) > 1 else None
    client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))

    # Load and optionally filter claims
    claims = load_historical_claims(company_filter)
    print(f"Loaded {len(claims)} historical claims")

    # Skip already-scored claims
    scored_texts: set[str] = set()
    if OUT_PATH.exists():
        with open(OUT_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    scored_texts.add(r["claim_text"])
        print(f"  ({len(scored_texts)} already scored — skipping)")

    to_score = [c for c in claims if c["claim_text"] not in scored_texts]
    if not to_score:
        print("Nothing to score.")
        return

    # Embed
    vectors = embed_claims(to_score)

    # Retrieve + score
    results = []
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "a", encoding="utf-8") as out_f:
        for i, (claim, vec) in enumerate(zip(to_score, vectors)):
            if i % 50 == 0:
                print(f"  {i}/{len(to_score)}  [{claim.get('company_id')}]")
            try:
                evidence = retrieve_evidence(claim, vec)
                gap = score_gap(client, claim, evidence)
                record = {
                    **claim,
                    "evidence": evidence,
                    "verdict": gap.get("verdict"),
                    "confidence": gap.get("confidence"),
                    "rationale": gap.get("rationale"),
                    "key_evidence_idx": gap.get("key_evidence_idx", []),
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                results.append(record)
            except Exception as e:
                print(f"    FAILED [{claim.get('company_id')} / {claim.get('claim_text', '')[:60]}]: {e}")

    # Summary
    verdicts = [r["verdict"] for r in results if r.get("verdict")]
    from collections import Counter
    counts = Counter(verdicts)
    print(f"\nDone. Scored {len(results)} claims:")
    for v, n in sorted(counts.items()):
        print(f"  {v:25} {n}")
    print(f"\nWrote to {OUT_PATH}")


if __name__ == "__main__":
    main()
