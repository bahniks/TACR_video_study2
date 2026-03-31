#! python3
"""Extract top TEXTS blocks from Python files into texts.txt.

The script scans .py files in a folder, finds the first block enclosed by lines
containing 3 or more '#' characters, and keeps the block only if it contains a
marker line exactly matching: # TEXTS <filename_without_py>
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

HASH_LINE_RE = re.compile(r"^\s*#{3,}\s*$")
TEXT_MARK_RE = re.compile(r"^\s*#\s*TEXTS\s+([A-Za-z0-9_\-]+)\s*$")


def find_text_block(lines: list[str], stem: str) -> list[str] | None:
    """Return the first valid TEXTS block for file stem, else None."""
    search_limit = min(len(lines), 200)

    for i in range(search_limit):
        if not HASH_LINE_RE.match(lines[i]):
            continue

        for j in range(i + 1, search_limit):
            if HASH_LINE_RE.match(lines[j]):
                block = lines[i + 1 : j]
                if not block:
                    break

                marker = None
                for raw in block:
                    line = raw.strip()
                    if not line:
                        continue
                    marker = line
                    break

                if marker is None:
                    break

                match = TEXT_MARK_RE.match(marker)
                if match and match.group(1) == stem:
                    # Drop leading/trailing empty lines for clean output.
                    while block and not block[0].strip():
                        block.pop(0)
                    while block and not block[-1].strip():
                        block.pop()
                    return block
                break

    return None


def extract_texts(folder: Path) -> tuple[list[str], int]:
    """Extract text blocks from all .py files in folder."""
    output_parts: list[str] = []
    found = 0

    for py_file in sorted(folder.glob("*.py")):
        lines = py_file.read_text(encoding="utf-8").splitlines()
        block = find_text_block(lines, py_file.stem)
        if block is None:
            continue

        found += 1
        output_parts.append(f"##### {py_file.name} #####")
        output_parts.extend(block)
        output_parts.append("")

    return output_parts, found


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect # TEXTS blocks from Python files.")
    parser.add_argument(
        "folder",
        nargs="?",
        default="Stuff",
        help="Folder with .py files (default: Stuff)",
    )
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        raise SystemExit(f"Folder does not exist: {folder}")

    lines, found = extract_texts(folder)
    output_file = folder / "texts.txt"
    output_text = "\n".join(lines).rstrip() + "\n"
    output_file.write_text(output_text, encoding="utf-8")

    print(f"Saved {found} section(s) to {output_file}")


if __name__ == "__main__":
    main()
