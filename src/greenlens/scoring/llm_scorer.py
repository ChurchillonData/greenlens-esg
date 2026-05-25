"""LLM-based scoring for claim-evidence pairs.

Sends a claim and its retrieved evidence to GPT-4o-mini with a strict prompt.
Returns the predicted class, risk score, and short reasoning.
"""

import json

from openai import OpenAI

from greenlens.config import CONFIG, get_api_key

CLASSES = ["well_substantiated", "weakly_substantiated", "contradicted"]
MODEL = CONFIG["pipeline"]["llm_model"]

SYSTEM_PROMPT = f"""You judge greenwashing risk in oil and gas company sustainability claims.

You will be given a CLAIM from a company sustainability report and 5 pieces of RETRIEVED EVIDENCE.

Decide which class the claim belongs to:

- "well_substantiated": the claim contains at least one concrete specific element (a specific number, a deadline year, a defined scope, OR a specific completed deal/programme with named partner and location) AND the retrieved evidence does not directly contradict it. A claim does not need ALL of these to qualify — one is enough.

- "weakly_substantiated": the claim lacks concrete elements. This includes: (a) pure aspiration with no number, no deadline, no scope; (b) four or more bundled goals with no quantities; (c) named entities (organisations, partners, programmes) without any quantified outcome, investment amount, or binding deadline — e.g. joining a named body, investing an unspecified amount, or focusing on delivering a previously-announced project.

- "contradicted": ONLY when retrieved evidence makes a specific factual statement that directly contradicts the specific commitment in the claim. The evidence must name the company AND the specific commitment AND show it is false, walked back, or numerically wrong.

EXAMPLES OF "well_substantiated":
- "We reduced operational emissions by 37% against the 2019 baseline" (number + baseline)
- "Our 2050 net-zero target covers operations" (deadline + scope)
- "Signed a 50:50 JV with Iberdrola at Castellon refinery for green hydrogen" (named partner + named location + specific deal completed)
- "Reduced freshwater withdrawal by 15% vs 2020" (number + baseline)
- "Reported oil spills increased to 110 compared with 96 in 2024" (specific numbers in factual data report)
- "Total energy consumption from own operations was 34 TWh, a change of -3% compared to 2024" (specific number + year-on-year change)
- "Delivered Lower 48 drilling and completion efficiencies >15% year over year" (specific percentage + defined operational scope)
- "Venezuela NOJV emissions have not been included for emissions reporting since 2021" (named scope + specific year)

EXAMPLES OF "weakly_substantiated":
- "We aim to support biodiversity where we operate" (no number, no deadline, no scope)
- "We are committed to the energy transition" (pure aspiration)
- "We aim to grow oil and gas, lower carbon intensity, invest in renewables, and develop hydrogen" (4+ bundled goals, no numbers)
- "In 2025 we focused on delivering two green hydrogen projects sanctioned in 2024, including our JV with Iberdrola" (named projects but only an execution-focus statement; no quantified delivery, cost, or output for this year)
- "Joined Pipeline Research Council International in 2024" (named organisation + year but no quantified commitment or outcome)
- "Invested in SwissDrones, a startup developing uncrewed helicopters" (named entity but no investment amount, scope, or timeline)

EXAMPLES OF "contradicted":
- Claim: "We will achieve net-zero by 2050." Evidence: "BP weakened its 2050 net-zero target in 2025." → contradicted because evidence names the company AND the specific commitment AND shows it walked back.

CRITICAL RULES:

1. Generic sector criticism (e.g. "oil majors aren't Paris-aligned", "fossil fuel firms misleadingly advertise") is NOT contradiction. It is background commentary.

2. Evidence about a different company is NOT contradiction.

3. Evidence raising concerns about the broader category (e.g. "CCS often underperforms") is NOT contradiction of a specific named CCS project.

4. ABSOLUTE RULE: If the claim states ANY specific number (a count, percentage, tonne figure, TWh, mmbbl, or ratio), classify as well_substantiated. Do NOT require the claim to explain implications, company actions, or context around the number. A factual report of data is concrete.

5. When in doubt between any class and contradicted, never choose contradicted. The bar for contradicted is high.

Return JSON with these exact keys:
- "class": one of {CLASSES}
- "risk_score": float between 0.0 (low greenwashing risk) and 1.0 (high greenwashing risk)
- "reasoning": one sentence citing what's specifically in the claim text.

Mapping risk_score to class:
- 0.0 to 0.4: well_substantiated
- 0.4 to 0.7: weakly_substantiated
- 0.7 to 1.0: contradicted
"""


def get_client() -> OpenAI:
    """Initialise the OpenAI client."""
    return OpenAI(api_key=get_api_key("OPENAI_API_KEY"))


def build_user_prompt(claim_text: str, evidence: list[dict]) -> str:
    """Format the claim and its evidence for the LLM."""
    ev_text = "\n".join(
        f"[{i+1}] {e.get('text', '')[:400]}" for i, e in enumerate(evidence)
    )
    return f"CLAIM:\n{claim_text}\n\nRETRIEVED EVIDENCE:\n{ev_text}"


def score_claim(client: OpenAI, claim_text: str, evidence: list[dict]) -> dict:
    """Score one claim against its evidence. Returns class, risk_score, reasoning."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(claim_text, evidence)},
        ],
    )
    return json.loads(response.choices[0].message.content)