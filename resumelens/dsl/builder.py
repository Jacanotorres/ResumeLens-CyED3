"""Stage 4 - build the candidate profile DSL text from a screening result."""

from __future__ import annotations

from resumelens.pipeline import ScreeningResult


def _quote(value: str) -> str:
    """Return value as a DSL STRING literal (single line, escaped)."""
    flat = " ".join(value.split())
    return '"' + flat.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_dsl(result: ScreeningResult) -> str:
    """Convert a ScreeningResult into text written in the candidate profile DSL.

    The grammar requires at least one skill, so a result with no recognized
    skills cannot be expressed and raises ValueError.
    """
    if not result.normalized:
        raise ValueError("cannot build a candidate profile without recognized skills")

    extraction = result.extraction
    lines = [f"candidate {_quote(extraction.name or 'Unknown')} {{"]

    lines.append("  contact {")
    for kind, values in (
        ("email", extraction.emails),
        ("phone", extraction.phones),
        ("link", extraction.links),
    ):
        lines.extend(f"    {kind}: {_quote(value)}" for value in values)
    lines.append("  }")

    lines.extend(f"  education: {_quote(degree)}" for degree in extraction.education)

    for item in extraction.experience:
        lines.append("  experience {")
        lines.append(f"    years: {item.years}")
        if item.description:
            lines.append(f"    description: {_quote(item.description)}")
        lines.append("  }")

    lines.append(f"  skills: {', '.join(result.normalized)}")

    lines.append("  classification {")
    for match in result.matches:
        verdict = "ACCEPTED" if match.accepted else "REJECTED"
        lines.append(f"    {match.profile_key}: {verdict}")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"