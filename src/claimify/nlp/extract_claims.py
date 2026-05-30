"""Extract structured claims from relevant sentences using OpenAI.

Usage:
    python -m claimify.nlp.extract_claims              # all companies
    python -m claimify.nlp.extract_claims bp           # one company

Reads from data/processed/reports/<company>_relevant.jsonl
Writes to data/outputs/<company>_claims.jsonl
"""

import json
import sys
from pathlib import Path

from openai import OpenAI

from claimify.config import CONFIG, get_api_key

BATCH_SIZE = 15  # sentences sent per API call
MODEL = CONFIG["pipeline"]["llm_model"]

CATEGORIES = [
    "net_zero", "emissions_reduction", "methane",
    "renewables_investment", "scope_3", "just_transition",
    "biodiversity", "climate_lobbying", "other",
]

SYSTEM_PROMPT = f"""You extract structured climate claims from oil and gas sustainability reports.

For each input sentence, decide if it contains a CONCRETE claim about the company's climate, emissions, or sustainability commitments. A concrete claim has at least ONE of: a specific number, a deadline year, a scope (e.g. "operated assets"), or a named programme. Aspirational language without specifics is NOT a claim.

Return a JSON object with key "claims" containing a list. Each claim has:
- "sentence_idx": the index of the input sentence (0-based)
- "category": one of {CATEGORIES}
- "claim_text": the sentence cleaned of extraneous formatting
- "target_value": numeric value if any (e.g. 50 for "50%"), else null
- "target_unit": unit string if any (e.g. "percent_reduction", "Mt_CO2e", "USD_billion"), else null
- "scope": scope qualifier if any (e.g. "operations", "operated_assets", "scope_3", "value_chain"), else null
- "baseline_year": baseline year if mentioned (e.g. 2019), else null
- "deadline_year": target year if any (e.g. 2030, 2050), else null

Skip sentences that are headers, navigation, or aspirational without specifics. If no sentences contain claims, return {{"claims": []}}.
"""


def get_client() -> OpenAI:
    """Initialise the OpenAI client with the key from .env."""
    return OpenAI(api_key=get_api_key("OPENAI_API_KEY"))


def build_user_prompt(sentences: list[str]) -> str:
    """Format a batch of sentences for the LLM."""
    numbered = "\n".join(f"[{i}] {s}" for i, s in enumerate(sentences))
    return f"Extract claims from these sentences:\n\n{numbered}"


def call_llm(client: OpenAI, sentences: list[str]) -> list[dict]:
    """Send one batch to the LLM, return list of claim objects."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(sentences)},
        ],
    )
    payload = json.loads(response.choices[0].message.content)
    return payload.get("claims", [])




def attach_metadata(claims: list[dict], records: list[dict]) -> list[dict]:
    """Attach company_id and page from the source records to each claim."""
    enriched: list[dict] = []
    for claim in claims:
        idx = claim.get("sentence_idx")
        if idx is None or idx >= len(records):
            continue
        source = records[idx]
        enriched.append({
            "company_id": source["company_id"],
            "page": source["page"],
            "source_sentence": source["sentence"],
            "category": claim.get("category"),
            "claim_text": claim.get("claim_text"),
            "target_value": claim.get("target_value"),
            "target_unit": claim.get("target_unit"),
            "scope": claim.get("scope"),
            "baseline_year": claim.get("baseline_year"),
            "deadline_year": claim.get("deadline_year"),
        })
    return enriched


def extract_for_company(company_id: str, client: OpenAI) -> int:
    """Extract claims for one company. Return the number of claims found."""
    in_path = Path(CONFIG["paths"]["reports_processed"]) / f"{company_id}_relevant.jsonl"
    out_path = Path(CONFIG["paths"]["outputs"]) / f"{company_id}_claims.jsonl"

    with open(in_path, encoding="utf-8-sig") as f:
        records = [json.loads(line) for line in f if line.strip()]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    all_claims: list[dict] = []

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start : start + BATCH_SIZE]
        sentences = [r["sentence"] for r in batch]
        try:
            raw_claims = call_llm(client, sentences)
        except Exception as e:
            print(f"  batch {start} failed: {e}")
            continue
        # remap sentence_idx from batch-local to absolute
        for c in raw_claims:
            if c.get("sentence_idx") is not None:
                c["sentence_idx"] += start
        enriched = attach_metadata(raw_claims, records)
        all_claims.extend(enriched)
        print(f"  batch {start // BATCH_SIZE + 1}/{(len(records) - 1) // BATCH_SIZE + 1}: {len(enriched)} claims")

    with open(out_path, "w", encoding="utf-8") as f:
        for claim in all_claims:
            f.write(json.dumps(claim) + "\n")

    return len(all_claims)


def main() -> None:
    """Extract claims for one company (arg) or all that are not yet extracted."""
    client = get_client()

    if len(sys.argv) == 2:
        company_ids = [sys.argv[1]]
    else:
        in_dir = Path(CONFIG["paths"]["reports_processed"])
        out_dir = Path(CONFIG["paths"]["outputs"])
        all_ids = [p.stem.replace("_relevant", "") for p in in_dir.glob("*_relevant.jsonl")]
        company_ids = [cid for cid in all_ids if not (out_dir / f"{cid}_claims.jsonl").exists()]

    for cid in sorted(company_ids):
        print(f"[extract] {cid}")
        try:
            n = extract_for_company(cid, client)
            print(f"[ok     ] {cid}: {n} claims")
        except Exception as e:
            print(f"[fail   ] {cid}: {e}")


if __name__ == "__main__":
    main()