"""Stage 3 - Qualification pattern recognition with finite automata (pyformlang).

One automaton per profile, built generically from the profile's categories.
Its alphabet Σ is the set of canonical tokens of the profile and it accepts the
sorted token sequences that satisfy the profile pattern.
"""

from __future__ import annotations

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from resumelens.profiles import Profile


def build_automaton(profile: Profile) -> DeterministicFiniteAutomaton:
    """Build the automaton M = (Q, Σ, δ, q0, F) that recognizes ``profile``'s pattern."""
    raise NotImplementedError("Stage 3")


def accepts(profile: Profile, sorted_tokens: list[str]) -> bool:
    """Run the profile automaton over a sequence already sorted for that profile."""
    raise NotImplementedError("Stage 3")
