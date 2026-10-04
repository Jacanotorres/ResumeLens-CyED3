"""Command line interface: ``python -m resumelens <resume.txt> [--html out.html]``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from resumelens.pipeline import screen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="resumelens",
        description="Formal language-based resume screening.",
    )
    parser.add_argument("resume", type=Path, help="plain-text resume file")
    parser.add_argument("--html", type=Path, help="write the HTML visualization here")
    parser.add_argument("--dsl", type=Path, help="write the candidate profile DSL here")
    args = parser.parse_args(argv)

    result = screen(args.resume.read_text(encoding="utf-8"))

    print("Normalized:", ", ".join(result.normalized) or "-")
    for match in result.matches:
        status = "ACCEPTED" if match.accepted else "REJECTED"
        print(f"{match.profile_key:<28} {status:<9} {', '.join(match.sequence)}")

    if args.dsl or args.html:
        raise NotImplementedError("Stage 4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
