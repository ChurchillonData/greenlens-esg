"""SBERT-based shortlist retrieval.

Given a claim, returns the top-K evidence records that apply to that
company, ranked by cosine similarity to the claim's embedding.
"""

import json
from pathlib import Path

import numpy as np

from claimify.config import CONFIG


def load_records(path: Path) -> list[dict]:
    """Load JSONL records into a list."""
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_index() -> tuple[list[dict], np.ndarray]:
    """Load corpus records and their vectors."""
    base = Path(CONFIG["paths"]["outputs"]) / "embeddings"
    records = load_records(base / "corpus_records.jsonl")
    vectors = np.load(base / "corpus_vectors.npy")
    return records, vectors


def cosine_scores(claim_vector: np.ndarray, corpus_vectors: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between one claim and every corpus vector."""
    claim_norm = claim_vector / np.linalg.norm(claim_vector)
    corpus_norms = corpus_vectors / np.linalg.norm(corpus_vectors, axis=1, keepdims=True)
    return corpus_norms @ claim_norm


def filter_by_company(records: list[dict], scores: np.ndarray, company_id: str) -> tuple[list[dict], np.ndarray]:
    """Keep only records that apply to this company. Return filtered records and scores."""
    keep_indices = [i for i, r in enumerate(records) if company_id in r.get("applies_to", [])]
    kept_records = [records[i] for i in keep_indices]
    kept_scores = scores[keep_indices]
    return kept_records, kept_scores


def top_k(records: list[dict], scores: np.ndarray, k: int = 20) -> list[tuple[dict, float]]:
    """Return the top K (record, score) pairs sorted by descending score."""
    if len(records) == 0:
        return []
    actual_k = min(k, len(records))
    top_indices = np.argsort(-scores)[:actual_k]
    return [(records[i], float(scores[i])) for i in top_indices]


def search(claim_vector: np.ndarray, company_id: str, k: int = 20) -> list[tuple[dict, float]]:
    """Find the top K evidence records for one claim."""
    records, vectors = load_index()
    scores = cosine_scores(claim_vector, vectors)
    filtered_records, filtered_scores = filter_by_company(records, scores, company_id)
    return top_k(filtered_records, filtered_scores, k)