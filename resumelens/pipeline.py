"""Glue code that runs the four stages over one resume."""

from __future__ import annotations

from dataclasses import dataclass, field

from resumelens import classification, normalization
from resumelens.extraction import ExtractionResult, extract
from resumelens.profiles import PROFILES


@dataclass
class ProfileMatch:
    profile_key: str
    sequence: list[str]
    accepted: bool


@dataclass
class ScreeningResult:
    extraction: ExtractionResult
    normalized: list[str]
    matches: list[ProfileMatch] = field(default_factory=list)

    @property
    def accepted_profiles(self) -> list[str]:
        return [m.profile_key for m in self.matches if m.accepted]


def screen(text: str) -> ScreeningResult:
    """Extraction -> normalization -> per-profile sorting -> automaton check."""
    extraction = extract(text)
    normalized = normalization.normalize_all(extraction.raw_skills())
    result = ScreeningResult(extraction, normalized)
    for profile in PROFILES:
        sequence = normalization.sort_for_profile(normalized, profile)
        result.matches.append(
            ProfileMatch(profile.key, sequence, classification.accepts(profile, sequence))
        )
    return result
