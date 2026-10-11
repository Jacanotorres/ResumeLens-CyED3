"""Command line interface: ``python -m resumelens <resume.txt> [--html out.html]``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from resumelens.dsl.builder import to_dsl
from resumelens.dsl.render import render_html
from resumelens.dsl.validator import DSLValidationError, validate
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
        try:
            dsl_text = to_dsl(result)
            model = validate(dsl_text)
        except (ValueError, DSLValidationError) as error:
            print(f"Could not build the candidate profile: {error}", file=sys.stderr)
            return 1
        if args.dsl:
            args.dsl.write_text(dsl_text, encoding="utf-8")
            print(f"DSL written to {args.dsl}")
        if args.html:
            args.html.write_text(render_html(model), encoding="utf-8")
            print(f"HTML written to {args.html}")   
    return 0


if __name__ == "__main__":
    sys.exit(main())
