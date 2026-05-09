"""Cross-encoder reranking of SBERT shortlists.

Takes the top 20 from sbert_search and reranks them with a more accurate
cross-encoder. Returns the top 5.
"""

from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None


def get_model() -> CrossEncoder:
    """Load the cross-encoder once."""
    global _model
    if _model is None:
        print(f"Loading {MODEL_NAME} (one-time download on first run)...")
        _model = CrossEncoder(MODEL_NAME)
    return _model


def score_pairs(claim_text: str, candidates: list[tuple[dict, float]]) -> list[float]:
    """Score each (claim, candidate.text) pair with the cross-encoder."""
    pairs = [(claim_text, rec["text"][:512]) for rec, _ in candidates]
    scores = get_model().predict(pairs)
    return [float(s) for s in scores]


def rerank(claim_text: str, candidates: list[tuple[dict, float]], top_n: int = 5) -> list[tuple[dict, float]]:
    """Re-rank SBERT candidates with the cross-encoder. Return top_n."""
    if not candidates:
        return []
    cross_scores = score_pairs(claim_text, candidates)
    paired = list(zip([rec for rec, _ in candidates], cross_scores))
    paired.sort(key=lambda x: -x[1])
    return paired[:top_n]