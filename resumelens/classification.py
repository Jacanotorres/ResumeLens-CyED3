"""Stage 3 - Qualification pattern recognition with finite automata (pyformlang).

One automaton per profile, built generically from the profile's categories.
Its alphabet Σ is the set of canonical tokens of the profile and it accepts the
sorted token sequences that satisfy the profile pattern.
"""

from __future__ import annotations

from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    Epsilon,
    EpsilonNFA,
)

from resumelens.profiles import Profile


def build_epsilon_nfa(profile: Profile) -> EpsilonNFA:
    """Build the ε-NFA for the ordered qualification categories in ``profile``.

    State ``i`` is reached after reading category ``i``. Each required category
    must contribute one or more tokens; optional categories may be skipped
    through an ε-transition. Tokens within a category may repeat.
    """
    automaton = EpsilonNFA()
    automaton.add_start_state(0)

    for state, category in enumerate(profile.categories, start=1):
        previous_state = state - 1
        for token in category.tokens:
            automaton.add_transition(previous_state, token, state)
            automaton.add_transition(state, token, state)
        if not category.required:
            automaton.add_transition(previous_state, Epsilon(), state)

    automaton.add_final_state(len(profile.categories))
    return automaton


def build_automaton(profile: Profile) -> DeterministicFiniteAutomaton:
    """Build the minimal DFA equivalent to the profile's ε-NFA."""
    return build_epsilon_nfa(profile).to_deterministic().minimize()


def accepts(profile: Profile, sorted_tokens: list[str]) -> bool:
    """Run the profile automaton over a sequence already sorted for that profile."""
    return build_automaton(profile).accepts(sorted_tokens)
