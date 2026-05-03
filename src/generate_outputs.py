"""
generate_outputs.py

Reads a candidate CSV produced by scan_for_candidates.py and uses a local
Ollama instance to draft the Output/Fix column for each row. The drafts
are written into a new column. Existing rows are preserved.

The model produces a draft. The student is expected to review every draft,
edit it where it is wrong or vague, and discard rows where the candidate
turns out not to be a real style issue.

Default model: codellama:instruct (the 7B variant, which is what was used
to produce the original dataset). Ollama must be running locally with this
model pulled.

Usage:
    python generate_outputs.py --input candidates.csv --output candidates_with_drafts.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:instruct"
REQUEST_TIMEOUT = 120  # seconds per call


PROMPT_TEMPLATE = """You are a code reviewer specialising in Move smart contracts.

The following Move code snippet has been flagged as a candidate for the style category: {label}

Write a single short corrective comment (one to three sentences) that:
- starts by naming the kind of issue,
- identifies the specific construct affected (function name, identifier, operator, etc.) using backticks,
- states what to change in concrete terms.

Do not include line numbers. Do not write a compiler-style error message. Write it as a code review note a developer would leave for a colleague.

CODE:
{code}

Output only the corrective comment, nothing else."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draft Output/Fix comments via Ollama for candidate snippets.")
    parser.add_argument("--input", type=Path, required=True, help="Candidate CSV from scan_for_candidates.py.")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV with drafted Output/Fix column.")
    parser.add_argument("--model", default=MODEL, help=f"Ollama model name (default: {MODEL}).")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional cap on number of candidates to process (default: 0 = all).",
    )
    return parser.parse_args()


def call_ollama(model: str, prompt: str) -> str:
    """Send a prompt to the local Ollama instance and return the model's response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"[OLLAMA ERROR: {exc}]"

    try:
        data = response.json()
    except json.JSONDecodeError:
        return "[OLLAMA ERROR: non-JSON response]"

    return (data.get("response") or "").strip()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        sys.exit(f"Input CSV not found: {args.input}")

    with args.input.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        sys.exit("No rows found in input CSV.")

    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    print(f"Drafting Output/Fix for {len(rows)} candidates using model '{args.model}'...")
    print("This will take a while: each candidate is one call to the local Ollama instance.\n")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) + ["draft_output_fix"]
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        start = time.time()
        for i, row in enumerate(rows, start=1):
            prompt = PROMPT_TEMPLATE.format(label=row.get("suggested_label", ""), code=row.get("code", ""))
            draft = call_ollama(args.model, prompt)
            row["draft_output_fix"] = draft
            writer.writerow(row)

            if i % 10 == 0 or i == len(rows):
                elapsed = time.time() - start
                rate = i / elapsed if elapsed > 0 else 0.0
                print(f"  {i}/{len(rows)} done ({rate:.2f}/s, {elapsed:.0f}s elapsed)")

    print(f"\nWrote drafts to {args.output}")
    print("Next step: review each row by hand, edit the draft where needed, discard false positives, and submit your final batch to Sui.")


if __name__ == "__main__":
    main()
