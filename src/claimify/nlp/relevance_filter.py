"""Filter sentences using ClimateBERT to keep only climate-relevant ones.

Run as a script:
    python -m claimify.nlp.relevance_filter

Reads from data/processed/reports/<company>_sentences.jsonl
Writes to data/processed/reports/<company>_relevant.jsonl
"""

import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from claimify.config import CONFIG

MODEL_NAME = "climatebert/distilroberta-base-climate-detector"
BATCH_SIZE = 32

_tokenizer = None
_model = None


def get_model() -> tuple:
    """Load ClimateBERT once and cache it."""
    global _tokenizer, _model
    if _model is None:
        print(f"Loading {MODEL_NAME} (one-time download on first run)...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.eval()
    return _tokenizer, _model


def predict_batch(sentences: list[str]) -> list[bool]:
    """Return True for each sentence that is climate-relevant."""
    tokenizer, model = get_model()
    inputs = tokenizer(
        sentences, padding=True, truncation=True, max_length=256, return_tensors="pt"
    )
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=-1).tolist()
    # Label 1 = "yes" (climate-related), 0 = "no"
    return [p == 1 for p in predictions]


def filter_file(in_path: Path, out_path: Path) -> tuple[int, int]:
    """Filter one company's sentences. Return (kept, total)."""
    with open(in_path, encoding="utf-8-sig") as f:
        records = [json.loads(line) for line in f if line.strip()]

    kept: list[dict] = []
    total = len(records)

    for start in range(0, total, BATCH_SIZE):
        batch = records[start : start + BATCH_SIZE]
        sentences = [r["sentence"] for r in batch]
        relevant = predict_batch(sentences)
        for record, is_relevant in zip(batch, relevant):
            if is_relevant:
                kept.append(record)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r) + "\n")

    return len(kept), total


def filter_all() -> None:
    """Filter every company's sentences."""
    in_dir = Path(CONFIG["paths"]["reports_processed"])
    sentence_files = sorted(in_dir.glob("*_sentences.jsonl"))

    if not sentence_files:
        print(f"No sentence files in {in_dir}. Run split_sentences.py first.")
        return

    for in_path in sentence_files:
        company_id = in_path.stem.replace("_sentences", "")
        out_path = in_dir / f"{company_id}_relevant.jsonl"
        print(f"[filter] {company_id}")
        try:
            kept, total = filter_file(in_path, out_path)
            pct = (kept / total * 100) if total else 0
            print(f"[ok    ] {company_id}: {kept}/{total} kept ({pct:.0f}%)")
        except Exception as e:
            print(f"[fail  ] {company_id}: {e}")


if __name__ == "__main__":
    filter_all()