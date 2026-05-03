"""
scan_for_candidates.py

Walks a directory tree of cloned repositories, finds every .move file, and
flags candidate snippets that look like they might match each of the six
style categories defined in rules/categories.md.

The output is a CSV with columns: code, suggested_label, source_path,
context_line. Each row is a *candidate*. The student reviewing this CSV is
expected to discard false positives and keep only the snippets that
genuinely represent a style issue.

The heuristics are deliberately permissive. They use simple regex patterns
on raw text rather than parsing Move source code, so they will flag both
real violations and code that happens to look like one. Filtering false
positives is the human's job.

Categories detected:
    StyleError/InconsistentNaming
    StyleError/Spacing
    StyleError/IncorrectIndentation
    StyleError/MissingDocumentation
    StyleError/InconsistentImportOrdering
    StyleError/InconsistentFunctionSignature

Usage:
    python scan_for_candidates.py --input ./cloned/ --output candidates.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


# ---------- snippet helpers ----------------------------------------------------

@dataclass(frozen=True)
class Candidate:
    code: str
    suggested_label: str
    source_path: str
    context_line: int


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, UnicodeError):
        return None


def snippet_around(lines: list[str], idx: int, before: int = 1, after: int = 6) -> str:
    """Return a short snippet centred on lines[idx] for the candidate."""
    start = max(0, idx - before)
    end = min(len(lines), idx + after + 1)
    return "\n".join(lines[start:end])


# ---------- per-category detectors ---------------------------------------------

# Function declarations: public fun, fun, entry fun, native public fun, etc.
FUNC_DECL_RE = re.compile(
    r"""^\s*
    (?:\#\[[^\]]*\]\s*)?
    (?:public(?:\([^)]+\))?\s+)?
    (?:entry\s+)?
    (?:native\s+)?
    fun\s+([A-Za-z_][A-Za-z0-9_]*)
    """,
    re.VERBOSE,
)

PUBLIC_FUNC_RE = re.compile(
    r"""^\s*
    (?:\#\[[^\]]*\]\s*)?
    (?:entry\s+)?
    public(?:\([^)]+\))?\s+
    (?:native\s+)?
    fun\s+([A-Za-z_][A-Za-z0-9_]*)
    """,
    re.VERBOSE,
)

PUBLIC_STRUCT_RE = re.compile(r"^\s*public\s+struct\s+([A-Za-z_][A-Za-z0-9_]*)")
STRUCT_RE = re.compile(r"^\s*struct\s+([A-Za-z_][A-Za-z0-9_]*)")
MODULE_RE = re.compile(r"^\s*module\s+[A-Za-z0-9_:]+\s*\{")
CONST_RE = re.compile(r"^\s*const\s+([A-Za-z_][A-Za-z0-9_]*)\s*:")
USE_RE = re.compile(r"^\s*use\s+([A-Za-z_][A-Za-z0-9_:]+)")


def is_snake_case(name: str) -> bool:
    return name == name.lower() and bool(re.fullmatch(r"[a-z][a-z0-9_]*", name))


def is_pascal_case(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Za-z0-9]*", name))


def is_upper_snake(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Z0-9_]*", name))


def is_e_prefixed_upper_snake(name: str) -> bool:
    return bool(re.fullmatch(r"E_[A-Z][A-Z0-9_]*", name))


def detect_naming(lines: list[str], path: str) -> Iterator[Candidate]:
    """Flag identifiers whose case does not match the convention for their kind."""
    for i, line in enumerate(lines):
        # Function names should be snake_case
        m = FUNC_DECL_RE.match(line)
        if m:
            name = m.group(1)
            if not is_snake_case(name) and not name.startswith("_"):
                yield Candidate(
                    snippet_around(lines, i),
                    "StyleError/InconsistentNaming",
                    path,
                    i + 1,
                )
            continue

        # Structs should be PascalCase
        m = STRUCT_RE.match(line)
        if m:
            name = m.group(1)
            if not is_pascal_case(name):
                yield Candidate(
                    snippet_around(lines, i),
                    "StyleError/InconsistentNaming",
                    path,
                    i + 1,
                )
            continue

        # Constants: error constants get E_ + UPPER_SNAKE; others get UPPER_SNAKE
        m = CONST_RE.match(line)
        if m:
            name = m.group(1)
            looks_like_error = name.startswith("E") and (len(name) > 1 and name[1].isupper() or name.startswith("E_"))
            if looks_like_error:
                # Should be E_UPPER_SNAKE_CASE
                if not is_e_prefixed_upper_snake(name):
                    yield Candidate(
                        snippet_around(lines, i),
                        "StyleError/InconsistentNaming",
                        path,
                        i + 1,
                    )
            else:
                if not is_upper_snake(name):
                    yield Candidate(
                        snippet_around(lines, i),
                        "StyleError/InconsistentNaming",
                        path,
                        i + 1,
                    )


# Spacing: operators with no spaces, commas with no following space, missing
# spaces in type constraint expressions like "copy+ drop+ store".
NO_SPACE_AROUND_EQ = re.compile(r"[A-Za-z0-9_)\]]=[A-Za-z0-9_(\[]")
NO_SPACE_AFTER_COMMA = re.compile(r",[A-Za-z0-9_]")
TIGHT_PLUS_IN_CONSTRAINT = re.compile(r"\b(?:copy|drop|store|key)\+\s*(?:copy|drop|store|key)")


def detect_spacing(lines: list[str], path: str) -> Iterator[Candidate]:
    for i, line in enumerate(lines):
        # Skip strings and comments to reduce false positives
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("///") or stripped.startswith("/*"):
            continue
        if TIGHT_PLUS_IN_CONSTRAINT.search(line):
            yield Candidate(
                snippet_around(lines, i),
                "StyleError/Spacing",
                path,
                i + 1,
            )
            continue
        if NO_SPACE_AROUND_EQ.search(line) and "==" not in line and "!=" not in line and ">=" not in line and "<=" not in line:
            yield Candidate(
                snippet_around(lines, i),
                "StyleError/Spacing",
                path,
                i + 1,
            )
            continue
        if NO_SPACE_AFTER_COMMA.search(line):
            yield Candidate(
                snippet_around(lines, i),
                "StyleError/Spacing",
                path,
                i + 1,
            )


def detect_indentation(lines: list[str], path: str) -> Iterator[Candidate]:
    """Flag lines whose leading whitespace is not a multiple of four spaces."""
    for i, line in enumerate(lines):
        if not line or not line.strip():
            continue
        leading = len(line) - len(line.lstrip(" "))
        if leading == 0:
            continue
        if "\t" in line[:leading]:
            yield Candidate(
                snippet_around(lines, i),
                "StyleError/IncorrectIndentation",
                path,
                i + 1,
            )
            continue
        if leading % 4 != 0:
            yield Candidate(
                snippet_around(lines, i),
                "StyleError/IncorrectIndentation",
                path,
                i + 1,
            )


def detect_missing_docs(lines: list[str], path: str) -> Iterator[Candidate]:
    """Flag public functions, public structs, and modules without a /// comment above."""
    for i, line in enumerate(lines):
        is_public_decl = (
            PUBLIC_FUNC_RE.match(line)
            or PUBLIC_STRUCT_RE.match(line)
            or MODULE_RE.match(line)
        )
        if not is_public_decl:
            continue
        # Walk upward through blank lines and attributes; the first non-blank,
        # non-attribute line above must be a /// comment for documentation to count.
        j = i - 1
        while j >= 0 and (lines[j].strip() == "" or lines[j].lstrip().startswith("#[")):
            j -= 1
        if j < 0 or not lines[j].lstrip().startswith("///"):
            yield Candidate(
                snippet_around(lines, i, before=0, after=4),
                "StyleError/MissingDocumentation",
                path,
                i + 1,
            )


def detect_import_ordering(lines: list[str], path: str) -> Iterator[Candidate]:
    """
    Flag a use-block in which std::* and sui::* (and project) imports are
    interleaved without blank-line separation between groups.
    """
    in_block = False
    block_start = -1
    seen_groups: list[str] = []  # ordered list of group keys as encountered, "std" / "sui" / "other"
    for i, line in enumerate(lines):
        m = USE_RE.match(line)
        if m:
            if not in_block:
                in_block = True
                block_start = i
                seen_groups = []
            target = m.group(1)
            if target.startswith("std::"):
                group = "std"
            elif target.startswith("sui::"):
                group = "sui"
            else:
                group = "other"
            if seen_groups and group != seen_groups[-1]:
                # Group transition without preceding blank line is a flag.
                # We mark it once when we see the second group emerge.
                if group not in seen_groups[:-1]:
                    seen_groups.append(group)
            elif not seen_groups:
                seen_groups.append(group)
        else:
            if in_block:
                # End of block; if more than one group seen and at least one transition was tight, flag it.
                if len(seen_groups) > 1:
                    yield Candidate(
                        "\n".join(lines[block_start : i + 1]).rstrip(),
                        "StyleError/InconsistentImportOrdering",
                        path,
                        block_start + 1,
                    )
                in_block = False
                seen_groups = []


def detect_long_signatures(lines: list[str], path: str) -> Iterator[Candidate]:
    """Flag function declarations longer than 100 chars on a single line."""
    for i, line in enumerate(lines):
        if FUNC_DECL_RE.match(line) and len(line) > 100 and "(" in line and ")" in line:
            # If the closing paren is on the same line, the signature was forced into one line.
            yield Candidate(
                snippet_around(lines, i, before=0, after=2),
                "StyleError/InconsistentFunctionSignature",
                path,
                i + 1,
            )


# ---------- driver -------------------------------------------------------------

DETECTORS = [
    detect_naming,
    detect_spacing,
    detect_indentation,
    detect_missing_docs,
    detect_import_ordering,
    detect_long_signatures,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan cloned Move repos for style-issue candidates.")
    parser.add_argument("--input", type=Path, required=True, help="Directory containing cloned repos.")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path.")
    parser.add_argument(
        "--max-per-category",
        type=int,
        default=300,
        help="Soft cap on candidates per category (default 300). Reduces output size.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        sys.exit(f"Input directory not found: {args.input}")

    counts: dict[str, int] = {}
    rows: list[Candidate] = []

    move_files = list(args.input.rglob("*.move"))
    print(f"Scanning {len(move_files)} .move files under {args.input}...")

    for path in move_files:
        lines = read_lines(path)
        if lines is None:
            continue
        rel_path = str(path.relative_to(args.input))
        for detector in DETECTORS:
            for candidate in detector(lines, rel_path):
                count = counts.get(candidate.suggested_label, 0)
                if count >= args.max_per_category:
                    continue
                rows.append(candidate)
                counts[candidate.suggested_label] = count + 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["code", "suggested_label", "source_path", "context_line"])
        for c in rows:
            writer.writerow([c.code, c.suggested_label, c.source_path, c.context_line])

    print(f"\nWrote {len(rows)} candidates to {args.output}")
    for label, n in sorted(counts.items()):
        print(f"  {label}: {n}")
    print("\nNext step: run generate_outputs.py to draft the Output/Fix column.")


if __name__ == "__main__":
    main()
