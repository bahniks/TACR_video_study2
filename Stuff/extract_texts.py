#! python3
"""Extract text content from files in a folder.

- Python mode: scans .py files, finds the first block enclosed by lines
    containing 3 or more '#' characters, and keeps it only if it contains
    marker line: # TEXTS <filename_without_py>.
- TXT mode: collects contents of all .txt files in the folder, excluding
    output files produced by this script.
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
        output_parts.extend(["", "", ""])

    return output_parts, found


def extract_txt_files(folder: Path, excluded_names: set[str]) -> tuple[list[str], int]:
    """Extract full contents from .txt files in folder, excluding selected names."""
    output_parts: list[str] = []
    found = 0

    for txt_file in sorted(folder.glob("*.txt")):
        if txt_file.name in excluded_names:
            continue

        found += 1
        output_parts.append(f"##### {txt_file.name} #####")
        output_parts.extend(txt_file.read_text(encoding="utf-8").splitlines())
        output_parts.extend(["", "", ""])

    return output_parts, found


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect text blocks from Python files and/or contents of TXT files."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Folder to scan (default: directory of this script)",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "py", "txt"],
        default="both",
        help="What to extract (default: both)",
    )
    args = parser.parse_args()

    folder = Path(args.folder).resolve() if args.folder else Path(__file__).resolve().parent
    if not folder.is_dir():
        raise SystemExit(f"Folder does not exist: {folder}")

    py_output_name = "texts.txt"
    txt_output_name = "texts_from_txt_files.txt"

    if args.mode in ("both", "py"):
        lines, found = extract_texts(folder)
        output_file = folder / py_output_name
        output_text = "\n".join(lines)
        output_file.write_text(output_text, encoding="utf-8")
        print(f"Saved {found} Python section(s) to {output_file}")

    if args.mode in ("both", "txt"):
        txt_lines, txt_found = extract_txt_files(folder, {py_output_name, txt_output_name})
        txt_output_file = folder / txt_output_name
        txt_output_text = "\n".join(txt_lines)
        txt_output_file.write_text(txt_output_text, encoding="utf-8")
        print(f"Saved {txt_found} TXT file(s) to {txt_output_file}")


if __name__ == "__main__":
    main()
