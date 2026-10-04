"""Stage 2 - Qualification normalization with finite-state transducers (pyformlang).

Each transducer reads a raw skill string character by character and emits its
canonical token, e.g. ``"React.js" -> "REACT"``. The normalized tokens are then
sorted in the canonical order of a given profile.
"""

from __future__ import annotations

from pyformlang.fst import FST

from resumelens.profiles import Profile


def build_transducer(variants: dict[str, str]) -> FST:
    """Build an FST from a ``{surface form: canonical token}`` table.

    Input:  mapping of accepted surface forms to canonical tokens.
    Output: a pyformlang ``FST`` M = (Q, Σ, Γ, δ, ω, q0, F).
    """
    raise NotImplementedError("Stage 2")


def normalize(raw_skill: str) -> str | None:
    """Translate one raw skill string into its canonical token.

    Returns ``None`` when no transducer accepts the string.
    """
    raise NotImplementedError("Stage 2")


def normalize_all(raw_skills: list[str]) -> list[str]:
    """Normalize a list of raw skills, dropping unknown ones and duplicates."""
    raise NotImplementedError("Stage 2")


def sort_for_profile(tokens: list[str], profile: Profile) -> list[str]:
    """Keep the tokens that belong to ``profile`` and sort them by its category order.

    Example (Full Stack): [GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT]
                       -> [JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]
    """
    raise NotImplementedError("Stage 2")
