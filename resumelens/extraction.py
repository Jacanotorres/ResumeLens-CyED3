"""Stage 1 - Resume information extraction with regular expressions (``re``).

This stage only *finds* candidate strings in the raw text. It does not decide
whether two strings are equivalent (stage 2) nor whether the candidate fits a
profile (stage 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Experience:
    years: int
    description: str


@dataclass
class ExtractionResult:
    name: str | None = None
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience: list[Experience] = field(default_factory=list)
    # Raw skill strings exactly as written in the resume, grouped by the
    # regex family that matched them, e.g. {"languages": ["JS"], ...}.
    skills: dict[str, list[str]] = field(default_factory=dict)

    def raw_skills(self) -> list[str]:
        """All raw skill strings in order of appearance (input of stage 2)."""
        raise NotImplementedError("Stage 1")


def extract(text: str) -> ExtractionResult:
    """Apply every extraction regex to ``text``.

    Input:  raw resume text.
    Output: an ``ExtractionResult`` with contact data, experience, education
            and raw (non-normalized) skill strings.
    """
    raise NotImplementedError("Stage 1")
