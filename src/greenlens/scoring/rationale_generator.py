"""Generate user-facing rationales and decision traces for scored claims.

Takes the classifier's output and produces:
- A 2-3 sentence rationale for display
- A decision trace of 2-4 numbered steps, each grounded in the claim text or evidence
"""

import json

from openai import OpenAI

from greenlens.config import CONFIG, get_api_key

MODEL = CONFIG["pipeline"]["llm_model"]

SYSTEM_PROMPT = """You produce structured rationales for greenwashing risk classifications of oil and gas sustainability claims.

Your output will be read by compliance officers, ESG analysts, and journalists. Every step must be grounded in what is actually in the claim text or in the retrieved evidence. Do not invent elements.

You will receive:
- CLAIM: the exact claim text
- CLASSIFICATION: the predicted class (well_substantiated / weakly_substantiated / contradicted)
- RISK_SCORE: 0.0 (low greenwashing risk) to 1.0 (high risk)
- RETRIEVED EVIDENCE: numbered items [1]–[5] with source names

GROUNDING RULES (strictly enforced):
1. Before saying an element is absent from the claim, re-read the claim text and quote the relevant excerpt. If the element exists in the claim, do not say it is absent.
2. Specific check for years: if the claim contains any year (e.g. 2030, 2050, 2025), that year IS a deadline or timeline. Do not say "no timeline" or "no deadline" if a year appears in the claim.
3. Each decision_trace step with an evidence_ref must describe something actually in that evidence item.
4. Steps based purely on the claim text (not on evidence) must have evidence_ref set to null.

Return JSON with exactly these keys:

"rationale": 2-3 sentence plain-English summary of why the claim received this classification.
"key_factors": list of 2-4 short phrases citing decisive elements, e.g. ["quantified figure: 125ktCO2e", "evidence neutral", "Scope 2 defined"].
"decision_trace": list of 2-4 step objects, each with:
  - "step": integer starting at 1
  - "title": 3-6 word heading describing what was checked
  - "finding": one sentence — what was found in the claim text or evidence. Quote specific values or phrases from the claim where relevant.
  - "rule": one sentence — the scoring principle being applied
  - "verdict": one of "supports", "neutral", "contradicts" — how this step affects the classification
  - "evidence_ref": integer 1-5 if grounded in that evidence item, or null if grounded in the claim text alone

CLASS-SPECIFIC GUIDANCE:

well_substantiated: Steps should identify the concrete elements present in the claim (specific numbers, named deadlines, defined scopes, named projects/partners). Evidence steps should note whether evidence corroborates, contradicts, or is unrelated.

weakly_substantiated: Steps should identify what is absent. CRITICAL: quote the claim text first. If the claim says "90%" or "by 2030", do NOT say those elements are absent. Only flag as absent if you confirmed the element is genuinely not there after re-reading.

contradicted: Steps should identify the specific factual mismatch between a claim element and specific evidence. Quote both the claim and the evidence.
"""


def _build_user_prompt(
    claim_text: str,
    evidence: list[dict],
    predicted_class: str,
    risk_score: float,
    classifier_reasoning: str,
) -> str:
    ev_lines = []
    for i, e in enumerate(evidence):
        source = e.get("source", "")
        date = e.get("date", "")
        source_label = f"{source} {date}".strip() if date else source
        ev_lines.append(f"[{i+1}] ({source_label}) {e.get('text', '')[:300]}")
    ev_text = "\n".join(ev_lines)
    return (
        f"CLAIM:\n{claim_text}\n\n"
        f"CLASSIFICATION: {predicted_class}\n"
        f"RISK_SCORE: {risk_score:.2f}\n"
        f"CLASSIFIER_REASONING: {classifier_reasoning}\n\n"
        f"RETRIEVED EVIDENCE:\n{ev_text}"
    )


def generate_rationale(
    client: OpenAI,
    claim_text: str,
    evidence: list[dict],
    predicted_class: str,
    risk_score: float,
    classifier_reasoning: str,
) -> dict:
    """Return {rationale, key_factors, decision_trace} for one scored claim."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(
                    claim_text, evidence, predicted_class, risk_score, classifier_reasoning
                ),
            },
        ],
    )
    return json.loads(response.choices[0].message.content)
