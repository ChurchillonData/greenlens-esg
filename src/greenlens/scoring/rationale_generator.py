"""Generate user-facing rationales for scored claims.

Takes the classifier's output and produces a defensible 2-3 sentence explanation
suitable for compliance officers, ESG analysts, and journalists.
"""

import json

from openai import OpenAI

from greenlens.config import CONFIG, get_api_key

MODEL = CONFIG["pipeline"]["llm_model"]

_CLASS_FRAMING = {
    "well_substantiated": (
        "This claim is well-substantiated. "
        "Explain what specific concrete element(s) make it testable "
        "(numbers, named targets, specific dates, named projects). "
        "Note what the retrieved evidence says or does not say about it."
    ),
    "weakly_substantiated": (
        "This claim is weakly substantiated and carries greenwashing risk. "
        "Explain what concrete elements are absent (no specific number, no deadline, "
        "no defined scope, or named entities without quantified outcomes). "
        "Note that the absence of contradiction does not make the claim credible."
    ),
    "contradicted": (
        "This claim is contradicted by retrieved evidence. "
        "Explain precisely what the evidence says and how it contradicts "
        "the specific commitment or figure in the claim. "
        "Name the source type (investigative journalism, NGO report, etc.) if evident."
    ),
}

SYSTEM_PROMPT = """You write clear, defensible rationales for greenwashing risk classifications of oil and gas sustainability claims.

Your output will be read by compliance officers, ESG analysts, and journalists who need to understand and verify automated classifications. They will act on your reasoning, so be specific and accurate.

You will receive:
- CLAIM: the exact claim text from a sustainability report
- CLASSIFICATION: the predicted class
- RISK_SCORE: 0.0 (low greenwashing risk) to 1.0 (high risk)
- CLASSIFIER_REASONING: a one-sentence note from the classifier
- INSTRUCTION: what angle to take for this class

Write a rationale that:
1. States what drives the classification (what IS or IS NOT present in the claim text)
2. Notes what the retrieved evidence does or does not establish
3. Is 2-3 sentences, plain English, no hedging, no filler phrases like "it is important to note"

Return JSON with exactly these keys:
- "rationale": string, 2-3 sentences
- "key_factors": list of 2-4 short phrases summarising the decisive elements (e.g. ["quantified figure: 125ktCO2e", "evidence neutral", "Scope 2 defined"])
"""


def _build_user_prompt(
    claim_text: str,
    evidence: list[dict],
    predicted_class: str,
    risk_score: float,
    classifier_reasoning: str,
) -> str:
    ev_text = "\n".join(
        f"[{i+1}] {e.get('text', '')[:300]}" for i, e in enumerate(evidence)
    )
    instruction = _CLASS_FRAMING.get(predicted_class, "")
    return (
        f"CLAIM:\n{claim_text}\n\n"
        f"CLASSIFICATION: {predicted_class}\n"
        f"RISK_SCORE: {risk_score:.2f}\n"
        f"CLASSIFIER_REASONING: {classifier_reasoning}\n\n"
        f"RETRIEVED EVIDENCE:\n{ev_text}\n\n"
        f"INSTRUCTION: {instruction}"
    )


def generate_rationale(
    client: OpenAI,
    claim_text: str,
    evidence: list[dict],
    predicted_class: str,
    risk_score: float,
    classifier_reasoning: str,
) -> dict:
    """Return {rationale: str, key_factors: list[str]} for one scored claim."""
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
