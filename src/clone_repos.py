"""
clone_repos.py

Clones a list of Sui ecosystem repositories into a local directory so the
scanner can read their .move files. Reads URLs from a text file (one per
line, '#' comments allowed) and runs git clone for each.

Existing clones are skipped. Failures are reported but do not abort the run.

Usage:
    python clone_repos.py --input repos.txt --output ./cloned/
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clone Sui repositories listed in a text file.")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a text file with one repo URL per line. Lines starting with '#' are ignored.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory to clone repositories into. Will be created if it does not exist.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Git clone depth. Default is 1 (shallow). Use 0 for a full clone.",
    )
    return parser.parse_args()


def read_repo_list(path: Path) -> list[str]:
    if not path.exists():
        sys.exit(f"Input file not found: {path}")
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.append(stripped)
    return urls


def repo_dir_name(url: str) -> str:
    # Strip trailing slash and .git suffix, take the last path segment as the directory name.
    cleaned = url.rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[: -len(".git")]
    return cleaned.rsplit("/", 1)[-1]


def clone_one(url: str, output_dir: Path, depth: int) -> bool:
    target = output_dir / repo_dir_name(url)
    if target.exists():
        print(f"  skip (already cloned): {target}")
        return True

    cmd = ["git", "clone"]
    if depth and depth > 0:
        cmd.extend(["--depth", str(depth)])
    cmd.extend([url, str(target)])

    print(f"  cloning {url} -> {target}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FAILED: {url}\n    {result.stderr.strip()}")
        return False
    return True


def main() -> None:
    args = parse_args()
    urls = read_repo_list(args.input)
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(urls)} repositories to process.")
    successes = 0
    for url in urls:
        if clone_one(url, args.output, args.depth):
            successes += 1

    print(f"\nDone. {successes}/{len(urls)} repositories ready in {args.output}/")
    print("Run scan_for_candidates.py next.")


if __name__ == "__main__":
    main()
