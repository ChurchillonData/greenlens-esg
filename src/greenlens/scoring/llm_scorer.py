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

TWO-STEP CLASSIFICATION: First decide well_substantiated vs weakly_substantiated based on the CLAIM TEXT ALONE. Then, and only then, check whether evidence meets the high bar for "contradicted". Evidence that is critical or negative does NOT change well_substantiated → weakly_substantiated.

Decide which class the claim belongs to:

- "well_substantiated": the claim text contains at least one concrete specific element. A concrete element is a QUANTIFIED MEASUREMENT or CHANGE the company itself achieved or committed to (e.g. "reduced by 37%", "74 ktCO2e", "34 TWh"), OR a COMPANY DEADLINE for a named commitment (e.g. "net-zero by 2050"), OR a COMPLETED DEAL the company signed (e.g. "signed a 50:50 JV with Iberdrola at Castellón refinery"). One such element is enough to qualify.

- "weakly_substantiated": the claim text lacks concrete elements. This includes: (a) pure aspiration with no number, no deadline, no scope; (b) four or more bundled goals with no quantities; (c) named entities (organisations, partners, programmes) without any quantified outcome, investment amount, or binding deadline.

- "contradicted": ONLY when retrieved evidence makes a specific factual statement that directly contradicts the specific commitment in the claim. The evidence must name the company AND the specific commitment AND show it is false, walked back, or numerically wrong. This is a very high bar.

EXAMPLES OF "well_substantiated":
- "We reduced operational emissions by 37% against the 2019 baseline" (company's own number + baseline)
- "Our 2050 net-zero target covers operations" (company deadline + scope)
- "Signed a 50:50 JV with Iberdrola at Castellon refinery for green hydrogen" (named partner + named location + specific COMPLETED deal)
- "Reduced freshwater withdrawal by 15% vs 2020" (company's own number + baseline)
- "Reported oil spills increased to 110 compared with 96 in 2024" (company's own factual data)
- "Total energy consumption from own operations was 34 TWh, a change of -3% compared to 2024" (company's own number + change)
- "Delivered Lower 48 drilling and completion efficiencies >15% year over year" (company's own percentage + scope)
- "Venezuela NOJV emissions have not been included for emissions reporting since 2021" (company scope + year)
- "The associated decrease in fuel usage is anticipated to reduce GHG emissions by approximately 26,000 tonnes" (company's own tonne estimate)
- "reducing carbon intensity approximately 71,000 tonnes annually of CO2e" (company's own tonne figure)
- "Archaea Energy purchased RECs generating 125ktCO2e in Scope 2 emissions savings" (company's own purchase + tonne figure)
- "first-of-its-kind plastic waste processing facility with capacity to process 300 million pounds per year" (company's own specific capacity)
- "extensions and new discoveries of 14 mmbbl" (company's own volume)
- "The LNG is being sold to Sinopec under a 20-year sales agreement for 7.6 MTPA" (company's own contract quantity + term)
- "SAF production in Gela: inaugurated the first plant dedicated to SAF production" (completed action + named location)

EXAMPLES OF "weakly_substantiated":
- "We aim to support biodiversity where we operate" (no number, no deadline, no scope)
- "We are committed to the energy transition" (pure aspiration)
- "We aim to grow oil and gas, lower carbon intensity, invest in renewables, and develop hydrogen" (4+ bundled goals, no numbers)
- "In 2025 we focused on delivering two green hydrogen projects sanctioned in 2024, including our 50:50 JV with Iberdrola at our Castellón refinery" (execution-focus on previously-announced project; no quantified 2025 output; Rule 4c applies even though named partner+location appear)
- "Joined Pipeline Research Council International in 2024" (joining an org + year is not a quantified outcome; Rule 4e)
- "In 2024, Oxy joined Pipeline Research Council International which seeks to enhance the safety of pipelines" (same pattern — joining + year, no company commitment; Rule 4e)
- "Invested in SwissDrones, a startup developing uncrewed helicopters" (named entity but no investment amount, scope, or timeline)
- "The C1 scenarios envisage a global reduction of 40-50% by 2030" (external scenario, not company data; Rule 4a)
- "The European Council agreed on a 90% emission-reduction target by 2040" (external body's target, not the company's; Rule 4a)
- "A recent U.S.-based study found that polyethylene packaging generates up to 70% lower emissions than glass" (external study finding, not company data; Rule 4a)
- "Storage levels comfortably reached the EU mandatory targets by October 2025" (EU external threshold; Rule 4a/4d)
- "Revised from 293 to 402 tonnes for 2024 due to a reporting omission" (data correction, no forward commitment; Rule 4b)
- "Our standards require new assets and existing assets modified after July 1, 2024, to use best available techniques (BAT)" (compliance standard, not a company quantity commitment; Rule 4d)
- "In September 2025, Google selected Shell as its renewable energy manager in the UK" (third-party selected the company; no company-initiated quantity commitment; Rule 4e)
- "Our Power Team works to provide power delivery across three cogeneration facilities, a solar plant, and in 16 states and Canada" (listing existing infrastructure without quantified output; Rule 4e)
- "We have set targets to reduce our Scope 1 and 2 emissions and our net carbon intensity" (says targets were set but does not state what the targets are; 0 concrete elements)

EXAMPLES OF "contradicted":
- Claim: "We will achieve net-zero by 2050." Evidence: "BP weakened its 2050 net-zero target in 2025." → contradicted because evidence names the company AND the specific commitment AND shows it walked back.

CRITICAL RULES:

1. Generic sector criticism (e.g. "oil majors aren't Paris-aligned", "fossil fuel firms misleadingly advertise") is NOT contradiction. It is background commentary.

2. Evidence about a different company is NOT contradiction.

3. Evidence raising concerns about the broader category (e.g. "CCS often underperforms") is NOT contradiction of a specific named CCS project.

4. ABSOLUTE RULE — evidence does NOT affect the well_substantiated vs weakly_substantiated choice:
   If the claim text has 1+ concrete elements, classify well_substantiated regardless of whether evidence is positive, neutral, negative, or critical. Negative or skeptical evidence only matters for the "contradicted" determination.
   EXCEPTIONS — classify as weakly_substantiated despite containing numbers or dates when:
   (a) The number/target belongs to an external body, study, or scenario — NOT the company's own data or commitment. Examples: "A study found X%", "The EU target is 90%", "IPCC C1 scenarios envisage 40-50%", "The European Council agreed on 90% by 2040", "Storage levels reached EU mandatory targets". The test: is the company the source of this figure? If no, it is external. Note: a study or scenario finding cited by the company is still NOT the company's own data.
   (b) The number is a data correction or audit revision with no forward commitment — e.g. "Revised from 293 to 402 tonnes due to reporting omission." Pure corrections are not commitments.
   (c) The claim describes only what the company is FOCUSED ON DELIVERING from a previously-announced project, with no quantified output for the current period. This applies even when specific project names, partners, or locations appear — the key signal is "focused on delivering", "working to deliver", or similar execution-focus language for a project that was already announced.
   (d) The number is a regulatory threshold or third-party compliance standard the company must meet, not a quantity the company itself produced, achieved, or committed to beyond what is legally required. Example: "Our standards require assets modified after July 1, 2024 to use best available techniques."
   (e) The claim describes an event where a third party acted on the company (e.g. the company joined an organization, was selected by another entity, won an award, became a member) without stating a quantified company commitment or outcome. A year alongside such events is NOT a concrete element. Counts of existing infrastructure (number of facilities, states, plants) without a quantified output are also not concrete elements. Examples: "Joined Pipeline Research Council International in 2024" (year + membership → weakly), "Google selected Shell as its renewable energy manager" (third-party selection → weakly), "Our Power Team works across three cogeneration facilities, a solar plant, and in 16 states" (infrastructure inventory → weakly).
   (f) A year or date alone is not a concrete element. A date only qualifies as a concrete element when the company has a named specific commitment DUE BY that date. A date when a compliance regulation takes effect (e.g. "assets modified after July 1, 2024 must use BAT"), a date when the company joined something, or a date that an external body agreed on a target are NOT company commitments.
   (g) Vague or unspecified future counts (e.g. "more than ten projects", "multiple initiatives") are not concrete elements unless every named item has an associated quantified output.

5. When in doubt between any class and contradicted, never choose contradicted. The bar for contradicted is high.

Return JSON with these exact keys IN THIS ORDER:

1. "score_reasoning": think step by step before scoring. Write 2-4 sentences covering:
   (a) List every concrete element present IN THE CLAIM TEXT: specific numbers, percentages, named deadlines, defined scope, named partners/locations. Quote them exactly.
   (b) Count the concrete elements: "0 concrete elements", "1 concrete element", "2+ concrete elements". Then check Rule 4 exceptions: does any exception (a)-(d) apply? If yes, treat as 0 elements.
   (c) Based on steps (a)-(b) alone, state the class: well_substantiated (1+ elements, no exception) or weakly_substantiated (0 elements or exception). Then check: does any evidence meet the contradicted bar (names company + specific commitment + shows it is false)?
   (d) State which sub-band score applies.

2. "class": one of {CLASSES}

3. "risk_score": float derived from score_reasoning — use the FULL range, not just midpoints:

   well_substantiated (0.0–0.4):
   - 0.05–0.14: 3+ concrete elements, evidence corroborates or is neutral
   - 0.15–0.25: 2 concrete elements, evidence neutral or unrelated
   - 0.26–0.39: 1 concrete element (evidence quality does not affect this band choice)

   weakly_substantiated (0.4–0.7):
   - 0.40–0.48: 0 concrete elements — pure aspiration, vague pledge
   - 0.49–0.58: 1 vague element, or bundled goals with no quantities, or a Rule 4 exception applied
   - 0.59–0.69: borderline — nearly well_substantiated by form but a Rule 4 exception prevents it

   contradicted (0.7–1.0):
   - 0.70–0.78: evidence indirectly undermines, does not name company+commitment explicitly
   - 0.79–0.89: evidence directly names company and contradicts the specific commitment
   - 0.90–0.99: multiple evidence items explicitly contradict; clear factual falsehood

4. "reasoning": one sentence citing what's specifically in the claim text.
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