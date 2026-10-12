import pytest
from pyformlang.finite_automaton import Epsilon

from resumelens.classification import build_automaton, build_epsilon_nfa
from resumelens.diagrams import OUTPUT, formal_definition, render_document, to_mermaid
from resumelens.profiles import PROFILES


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.key)
def test_epsilon_nfa_has_one_state_per_category_boundary(profile):
    nfa = build_epsilon_nfa(profile)
    assert len(nfa.states) == len(profile.categories) + 1
    assert len(nfa.final_states) == 1


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.key)
def test_epsilon_transitions_only_for_optional_categories(profile):
    transitions = build_epsilon_nfa(profile).to_dict()
    epsilon_edges = sum(
        1 for by_symbol in transitions.values() for symbol in by_symbol if symbol == Epsilon()
    )
    optional = sum(1 for c in profile.categories if not c.required)
    assert epsilon_edges == optional


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.key)
def test_epsilon_nfa_and_minimal_dfa_are_equivalent(profile):
    assert build_epsilon_nfa(profile).is_equivalent_to(build_automaton(profile))


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.key)
def test_mermaid_diagram_lists_every_token_and_marks_final_state(profile):
    diagram = to_mermaid(profile)
    final = len(profile.categories)
    assert diagram.startswith("flowchart LR")
    assert f"q{final}(((q{final})))" in diagram
    for token in profile.alphabet:
        assert token in diagram
    optional = sum(1 for c in profile.categories if not c.required)
    assert diagram.count('-.->|"ε"|') == optional


def test_formal_definition_contains_the_five_tuple():
    section = formal_definition(PROFILES[0])
    for part in ("**Q**", "**Σ**", "**δ**", "**q0**", "**F**", "```mermaid"):
        assert part in section


def test_generated_document_is_up_to_date():
    assert OUTPUT.read_text(encoding="utf-8") == render_document(), (
        "Run `python -m resumelens.diagrams` to regenerate the profile automata document"
    )
