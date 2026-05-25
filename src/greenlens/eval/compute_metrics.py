"""Compare model predictions against the hand-labelled eval set.

Usage:
    python -m greenlens.eval.compute_metrics

Reads labels from data/eval/labels.jsonl
Reads predictions from data/outputs/scored.jsonl
Prints precision, recall, and confusion matrix.
"""

import json
from collections import Counter
from pathlib import Path

from greenlens.config import CONFIG


def load_labels() -> dict[str, str]:
    """Load hand labels, keyed by claim_text."""
    path = Path(CONFIG["paths"]["eval"]) / "labels.jsonl"
    labels: dict[str, str] = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                labels[row["claim_text"]] = row["judgement"]
    return labels


def load_predictions() -> dict[str, str]:
    """Load model predictions, keyed by claim_text."""
    path = Path(CONFIG["paths"]["outputs"]) / "scored.jsonl"
    preds: dict[str, str] = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                key = row.get("claim_text", "")
                preds[key] = row.get("predicted", {}).get("class", "")
    return preds


def build_confusion(labels: dict[str, str], preds: dict[str, str]) -> dict[tuple[str, str], int]:
    """Count (true, predicted) pairs."""
    pairs = Counter()
    for cid, true_label in labels.items():
        if cid in preds:
            pairs[(true_label, preds[cid])] += 1
    return pairs


def print_confusion(confusion: dict[tuple[str, str], int]) -> None:
    """Print the confusion matrix as a table."""
    classes = ["well_substantiated", "weakly_substantiated", "contradicted"]
    print(f"\n{'true vs pred':<22} " + " ".join(f"{c:<22}" for c in classes))
    for true_class in classes:
        row = [str(confusion.get((true_class, pred), 0)) for pred in classes]
        print(f"{true_class:<22} " + " ".join(f"{v:<22}" for v in row))


def print_per_class_metrics(confusion: dict, classes: list[str]) -> None:
    """Print precision and recall per class."""
    for cls in classes:
        tp = confusion.get((cls, cls), 0)
        fp = sum(confusion.get((other, cls), 0) for other in classes if other != cls)
        fn = sum(confusion.get((cls, other), 0) for other in classes if other != cls)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        print(f"  {cls}: precision={precision:.2f}, recall={recall:.2f} (tp={tp}, fp={fp}, fn={fn})")


def main() -> None:
    """Compute and display metrics."""
    labels = load_labels()
    preds = load_predictions()
    matched = sum(1 for cid in labels if cid in preds)
    print(f"Hand-labelled: {len(labels)}")
    print(f"Predicted: {len(preds)}")
    print(f"Matched (in both): {matched}")

    confusion = build_confusion(labels, preds)
    print_confusion(confusion)

    print("\nPer-class metrics:")
    print_per_class_metrics(confusion, ["well_substantiated", "weakly_substantiated", "contradicted"])

    correct = sum(confusion.get((c, c), 0) for c in ["well_substantiated", "weakly_substantiated", "contradicted"])
    if matched > 0:
        print(f"\nOverall accuracy: {correct}/{matched} = {correct/matched:.2%}")
    else:
        print("\nOverall accuracy: no matched claims")


if __name__ == "__main__":
    main()