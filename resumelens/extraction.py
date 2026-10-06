"""Stage 1 - Resume information extraction with regular expressions (``re``).

This stage only *finds* candidate strings in the raw text. It does not decide
whether two strings are equivalent (stage 2) nor whether the candidate fits a
profile (stage 3). Skill strings are therefore returned exactly as written
("React.js", "NodeJS", "Postgres"...), never canonicalized.

Every regular expression below is documented in ``docs/stage1_extraction.md``
(the language it recognizes and why it is written that way).
"""

from __future__ import annotations

import re
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
    # Same raw skill strings, flat and in order of appearance in the text.
    skill_order: list[str] = field(default_factory=list)

    def raw_skills(self) -> list[str]:
        """All raw skill strings in order of appearance (input of stage 2)."""
        return list(self.skill_order)


# --------------------------------------------------------------------------
# Contact information
# --------------------------------------------------------------------------

# A line that is only 2-4 capitalized words: "Wednesday Addams".
NAME_RE = re.compile(
    r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ'’-]+(?:[ \t]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ'’-]+){1,3}"
)

# local-part '@' domain '.' tld
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

# Optional +country code, optional (area), then 3-3-2..4 digits with optional
# separators (space, dot, dash). "(?<!\w)" / "(?!\w)" stop it from matching
# inside longer alphanumeric strings.
PHONE_RE = re.compile(
    r"(?<![\w+])(?:\+\d{1,3}[ .-]?)?(?:\(\d{2,4}\)[ .-]?)?\d{3}[ .-]?\d{3}[ .-]?\d{2,4}(?![\w])"
)

# http(s) URLs, www.* hosts, or bare linkedin/github profiles.
LINK_RE = re.compile(
    r"(?:https?://|www\.)[^\s,;<>()]+|(?<![\w/@.])(?:linkedin\.com|github\.com)/[^\s,;<>()]+",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------
# Education and experience
# --------------------------------------------------------------------------

# A whole line that mentions a degree/institution keyword.
EDUCATION_RE = re.compile(
    r"^[^\n]*\b(?:bachelor|b\.?sc|master|m\.?sc|ph\.?d|degree|diploma|"
    r"ingenier[ií]a|licenciatura|maestr[ií]a|university|universidad|college)\b[^\n]*$",
    re.IGNORECASE | re.MULTILINE,
    )

# "<n> years of experience <description>"  (also "yrs", Spanish "años").
EXPERIENCE_RE = re.compile(
    r"(\d{1,2})\+?[ \t]*(?:years?|yrs?|años?)[ \t]+(?:of[ \t]+)?experience"
    r"[ \t]*(?:(?:in|with|as|on)[ \t]+|:[ \t]*)?([^.\n]*)",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------
# Skills: one alternation of surface forms per family. Variants are listed so
# the stage can *detect* them; deciding they are equivalent is stage 2's job.
# --------------------------------------------------------------------------

_SKILL_FAMILIES: dict[str, str] = {
    "languages": (
        r"java[ ]?script|js|type[ ]?script|ts|python|java|scala|bash"
    ),
    "frameworks": (
        r"react(?:[ ]?\.?[ ]?js)?|angular(?:[ ]?\.?[ ]?js)?|vue(?:[ ]?\.?[ ]?js)?|"
        r"node(?:[ ]?\.?[ ]?js)?|(?-i:Express)(?:[ ]?\.?[ ]?js)?|django|flask|"
        r"spring[ -]?boot|rest(?:ful)?[ ]+apis?|graphql"
    ),
    "libraries": (
        r"pandas|numpy|scikit[ -]?learn|sklearn|tensor[ -]?flow|py[ -]?torch|keras"
    ),
    "databases": (
        r"postgres(?:ql)?|my[ ]?sql|sqlite|sql|mongo[ ]?db|redis|snowflake|big[ ]?query"
    ),
    "tools": (
        r"git|docker|kubernetes|k8s|jenkins|github[ ]?actions|gitlab(?:[ -]?ci)?|"
        r"terraform|ansible|linux|aws|amazon[ ]web[ ]services|azure|gcp|google[ ]cloud|"
        r"(?:apache[ ])?spark|hadoop|(?:apache[ ])?kafka|(?:apache[ ])?airflow|dbt"
    ),
    "practices": (
        r"(?:machine|ml)[ -](?:learning[ ])?model[ ]development|predictive[ ]models?"
    ),
}

# Not preceded or followed by a word character, and not preceded by '.', so
# "js" is not found inside "NodeJS" or "React.js" and "Java" not inside "JavaScript".
SKILL_RES: dict[str, re.Pattern[str]] = {
    family: re.compile(rf"(?<![\w.])(?:{body})(?!\w)", re.IGNORECASE)
    for family, body in _SKILL_FAMILIES.items()
}


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

def _extract_name(text: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line if NAME_RE.fullmatch(line) else None
    return None


def _extract_skills(text: str) -> tuple[dict[str, list[str]], list[str]]:
    spans: list[tuple[int, int, str, str]] = []
    for family, pattern in SKILL_RES.items():
        for m in pattern.finditer(text):
            spans.append((m.start(), m.end(), family, m.group()))
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))

    by_family: dict[str, list[str]] = {}
    order: list[str] = []
    last_end = -1
    for start, end, family, raw in spans:
        if start < last_end:  # overlaps a longer/earlier match
            continue
        last_end = end
        by_family.setdefault(family, []).append(raw)
        order.append(raw)
    return by_family, order


def extract(text: str) -> ExtractionResult:
    """Apply every extraction regex to ``text``.

    Input:  raw resume text.
    Output: an ``ExtractionResult`` with contact data, experience, education
            and raw (non-normalized) skill strings.
    """
    skills, order = _extract_skills(text)
    return ExtractionResult(
        name=_extract_name(text),
        emails=EMAIL_RE.findall(text),
        phones=[p.strip() for p in PHONE_RE.findall(text)],
        links=[m.rstrip(".") for m in LINK_RE.findall(text)],
        education=[m.strip() for m in EDUCATION_RE.findall(text)],
        experience=[
            Experience(int(years), description.strip())
            for years, description in EXPERIENCE_RE.findall(text)
        ],
        skills=skills,
        skill_order=order,
    )