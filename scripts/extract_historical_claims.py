"""Extract structured climate claims from 2021 historical sustainability reports.

Full pipeline: PDF → text → sentences → keyword filter → LLM claim extraction.
Writes one JSONL per company to data/historical/claims/.

Usage:
    python scripts/extract_historical_claims.py          # all 10 companies
    python scripts/extract_historical_claims.py bp       # one company
"""

import json
import re
import sys
from io import StringIO
from pathlib import Path

import nltk
from openai import OpenAI
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from greenlens.config import get_api_key

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HISTORICAL_DIR = Path("data/historical")
CLAIMS_DIR = Path("data/historical/claims")
CLAIMS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
LLM_MODEL = "gpt-4o-mini"
BATCH_SIZE = 15
MIN_SENTENCE_LEN = 30

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

# ---------------------------------------------------------------------------
# Step 1: PDF → text with page markers
# ---------------------------------------------------------------------------

def parse_pdf(pdf_path: Path) -> str:
    laparams = LAParams(line_margin=0.3, char_margin=2.0, word_margin=0.1,
                        boxes_flow=0.5, detect_vertical=False)
    output = StringIO()
    with open(pdf_path, "rb") as f:
        extract_text_to_fp(f, output, laparams=laparams)
    full_text = output.getvalue()
    pages = full_text.split("\f")
    chunks = []
    for i, page_text in enumerate(pages, start=1):
        page_text = page_text.strip()
        if page_text:
            chunks.append(f"\n--- PAGE {i} ---\n{page_text}")
    return "\n".join(chunks)


# ---------------------------------------------------------------------------
# Step 2: text → sentence records
# ---------------------------------------------------------------------------

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def text_to_sentences(text: str, company_id: str, report_year: int) -> list[dict]:
    pattern = r"--- PAGE (\d+) ---"
    parts = re.split(pattern, text)
    records = []
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        page_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sents = nltk.sent_tokenize(page_text)
        for s in sents:
            s = s.strip()
            if len(s) >= MIN_SENTENCE_LEN:
                records.append({"company_id": company_id, "report_year": report_year,
                                 "page": page_num, "sentence": s})
    return records


# ---------------------------------------------------------------------------
# Step 3: Keyword relevance filter
# Sustainability reports are 100% climate-focused, so a keyword pass is
# sufficient — it removes boilerplate (page numbers, legal disclaimers,
# table headers) without the torch/ClimateBERT DLL dependency.
# ---------------------------------------------------------------------------

_CLIMATE_KEYWORDS = re.compile(
    r"\b(emission|carbon|CO2|GHG|greenhouse|net.zero|methane|climat|renewable|"
    r"fossil|decarbon|sustainab|scope\s*[123]|energy\s+transit|flaring|"
    r"offsett|sequestra|CCUS|CCS|hydrogen|Paris|IPCC|temperature|1\.5|2050|2030|"
    r"target|reduction|intensity|baseline|tonne|Mt|barrel|MWh|investment|pledge|"
    r"commit|ambition|goal|milestone|programme)\b",
    re.IGNORECASE,
)


def filter_relevant(records: list[dict]) -> list[dict]:
    return [r for r in records if _CLIMATE_KEYWORDS.search(r["sentence"])]


# ---------------------------------------------------------------------------
# Step 4: LLM claim extraction
# ---------------------------------------------------------------------------

def extract_claims_from_batch(client: OpenAI, batch: list[dict]) -> list[dict]:
    sentences = [r["sentence"] for r in batch]
    numbered = "\n".join(f"[{i}] {s}" for i, s in enumerate(sentences))
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract claims from these sentences:\n\n{numbered}"},
        ],
    )
    raw = json.loads(response.choices[0].message.content).get("claims", [])
    enriched = []
    for claim in raw:
        idx = claim.get("sentence_idx")
        if idx is None or idx >= len(batch):
            continue
        source = batch[idx]
        enriched.append({
            "company_id": source["company_id"],
            "report_year": source["report_year"],
            "page": source["page"],
            "category": claim.get("category"),
            "claim_text": claim.get("claim_text"),
            "target_value": claim.get("target_value"),
            "target_unit": claim.get("target_unit"),
            "scope": claim.get("scope"),
            "baseline_year": claim.get("baseline_year"),
            "deadline_year": claim.get("deadline_year"),
        })
    return enriched


# ---------------------------------------------------------------------------
# Main per-company runner
# ---------------------------------------------------------------------------

def process_company(pdf_path: Path, client: OpenAI) -> int:
    stem = pdf_path.stem                     # e.g. "bp_2021"
    parts = stem.rsplit("_", 1)
    company_id = parts[0]
    report_year = int(parts[1]) if len(parts) == 2 else 2021
    out_path = CLAIMS_DIR / f"{stem}_claims.jsonl"

    if out_path.exists():
        existing = sum(1 for l in open(out_path, encoding="utf-8") if l.strip())
        print(f"  SKIP  {stem} ({existing} claims already extracted)")
        return existing

    print(f"  Parsing {pdf_path.name}...")
    text = parse_pdf(pdf_path)

    print(f"  Splitting sentences...")
    records = text_to_sentences(text, company_id, report_year)
    print(f"    {len(records)} sentences")

    print(f"  Filtering with ClimateBERT...")
    relevant = filter_relevant(records)
    print(f"    {len(relevant)} climate-relevant sentences")

    print(f"  Extracting claims (LLM)...")
    all_claims = []
    total_batches = (len(relevant) - 1) // BATCH_SIZE + 1
    for start in range(0, len(relevant), BATCH_SIZE):
        batch = relevant[start: start + BATCH_SIZE]
        batch_num = start // BATCH_SIZE + 1
        try:
            claims = extract_claims_from_batch(client, batch)
            all_claims.extend(claims)
            print(f"    batch {batch_num}/{total_batches}: {len(claims)} claims")
        except Exception as e:
            print(f"    batch {batch_num} failed: {e}")

    with open(out_path, "w", encoding="utf-8") as f:
        for claim in all_claims:
            f.write(json.dumps(claim, ensure_ascii=False) + "\n")

    return len(all_claims)


def main() -> None:
    client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))

    if len(sys.argv) == 2:
        target = sys.argv[1]
        pdfs = sorted(HISTORICAL_DIR.glob(f"{target}_*.pdf"))
    else:
        pdfs = sorted(HISTORICAL_DIR.glob("*.pdf"))

    if not pdfs:
        print("No PDFs found in data/historical/")
        return

    print(f"Processing {len(pdfs)} historical reports...\n")
    total_claims = 0
    for pdf in pdfs:
        print(f"[{pdf.stem}]")
        try:
            n = process_company(pdf, client)
            print(f"  -> {n} claims total\n")
            total_claims += n
        except Exception as e:
            print(f"  FAILED: {e}\n")

    print(f"Done. {total_claims} historical claims extracted to {CLAIMS_DIR}/")


if __name__ == "__main__":
    main()
