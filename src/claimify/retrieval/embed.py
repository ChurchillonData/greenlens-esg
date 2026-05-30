"""Embed claims and evidence with SBERT, save vectors to disk.

Run as a script:
    python -m claimify.retrieval.embed

Reads claims from data/outputs/<company>_claims.jsonl
Reads corpus from data/evidence/corpus.jsonl
Writes vectors to data/outputs/embeddings/.
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from claimify.config import CONFIG

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


def get_model() -> SentenceTransformer:
    """Load SBERT once."""
    print(f"Loading {MODEL_NAME} (one-time download on first run)...")
    return SentenceTransformer(MODEL_NAME)


def load_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file into a list of records."""
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_all_claims() -> list[dict]:
    """Load every company's claims into one list."""
    out_dir = Path(CONFIG["paths"]["outputs"])
    records = []
    for jsonl in sorted(out_dir.glob("*_claims.jsonl")):
        records.extend(load_jsonl(jsonl))
    return records


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """Convert a list of strings into an array of embeddings."""
    return model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)


def save_embeddings(records: list[dict], vectors: np.ndarray, name: str) -> None:
    """Save records and their vectors to data/outputs/embeddings/."""
    out_dir = Path(CONFIG["paths"]["outputs"]) / "embeddings"
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / f"{name}_vectors.npy", vectors)
    with open(out_dir / f"{name}_records.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"Saved {len(records)} records and vectors to {out_dir}/{name}_*")


def main() -> None:
    """Embed claims and corpus, save to disk."""
    model = get_model()

    claims = load_all_claims()
    print(f"\nEmbedding {len(claims)} claims...")
    claim_texts = [c["claim_text"] for c in claims]
    claim_vectors = embed_texts(model, claim_texts)
    save_embeddings(claims, claim_vectors, "claims")

    corpus_path = Path(CONFIG["paths"]["evidence"]) / "corpus.jsonl"
    corpus = load_jsonl(corpus_path)
    print(f"\nEmbedding {len(corpus)} evidence records...")
    corpus_texts = [r["text"] for r in corpus]
    corpus_vectors = embed_texts(model, corpus_texts)
    save_embeddings(corpus, corpus_vectors, "corpus")


if __name__ == "__main__":
    main()