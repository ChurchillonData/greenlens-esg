"""Interactive CLI for labelling claims.

Usage:
    python -m claimify.eval.label_tool data/eval/claims_to_label.jsonl

Reads claims from the input file. Prompts you for a label per claim.
Saves to data/eval/labels.jsonl. Re-running skips already-labelled claims.
"""

import json
import sys
import uuid
from pathlib import Path

from claimify.config import CONFIG

LABELS_FILE = Path(CONFIG["paths"]["eval"]) / "labels.jsonl"
CLASSES = ["well_substantiated", "weakly_substantiated", "contradicted", "skip"]


def load_claims(path: Path) -> list[dict]:
    """Read claims from a JSONL file. Tolerates UTF-8 BOM from Windows tools."""
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def already_labelled() -> set[str]:
    """Return claim_ids that are already in the labels file."""
    if not LABELS_FILE.exists():
        return set()
    with open(LABELS_FILE, encoding="utf-8-sig") as f:
        return {json.loads(line)["claim_id"] for line in f if line.strip()}

def show_evidence(claim: dict) -> None:
    """Print the top retrieved evidence for the claim."""
    evidence = claim.get("evidence", [])
    if not evidence:
        print("No evidence retrieved.")
        return
    print(f"\nTop {len(evidence)} retrieved evidence items:")
    for i, ev in enumerate(evidence, start=1):
        snippet = ev.get("text", "")[:300].replace("\n", " ")
        print(f"\n  [{i}] (score {ev.get('score', 0):.2f}) {ev.get('evidence_id', '')}")
        print(f"      {snippet}...")


def ask_for_label(claim: dict) -> dict | None:
    """Ask the user to label one claim. Return label, or None to skip."""
    print("\n" + "=" * 70)
    print(f"Company: {claim['company_id']}")
    print(f"Category (extracted): {claim.get('category', 'unknown')}")
    print(f"Claim:   {claim['claim_text']}")
    print("=" * 70)

    show_evidence(claim)

    print()
    judgement = input(f"Judgement ({'/'.join(CLASSES)}): ").strip()
    if judgement == "skip" or judgement not in CLASSES:
        print("Skipped.")
        return None

    category = input("Category (e.g. net_zero, methane, scope_3): ").strip()
    note = input("Rationale note (1 sentence): ").strip()

    return {
        "claim_id": claim.get("claim_id") or str(uuid.uuid4())[:8],
        "company_id": claim["company_id"],
        "claim_text": claim["claim_text"],
        "category": category,
        "judgement": judgement,
        "rationale_note": note,
    }


def save_label(label: dict) -> None:
    """Append one label as a JSON line."""
    LABELS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LABELS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(label) + "\n")


def main() -> None:
    """Run the labelling session."""
    if len(sys.argv) != 2:
        print("Usage: python -m claimify.eval.label_tool <input.jsonl>")
        sys.exit(1)

    claims = load_claims(Path(sys.argv[1]))
    done = already_labelled()
    todo = [c for c in claims if c.get("claim_id") not in done]

    print(f"Loaded {len(claims)} claims. {len(done)} already labelled. {len(todo)} to do.")
    print("Press Ctrl-C to stop. Progress is saved as you go.\n")

    for i, claim in enumerate(todo, start=1):
        print(f"[{i}/{len(todo)}]")
        try:
            label = ask_for_label(claim)
        except KeyboardInterrupt:
            print("\nStopped. Progress saved.")
            return
        if label:
            save_label(label)
            print(f"Saved: {label['judgement']} ({label['category']})")

    print("\nAll done.")


if __name__ == "__main__":
    main()
    