from pathlib import Path

import pytest
from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from resumelens.classification import accepts, build_automaton
from resumelens.pipeline import screen
from resumelens.profiles import (
    DATA_ENGINEER,
    DEVOPS_ENGINEER,
    FULL_STACK_DEVELOPER,
    MACHINE_LEARNING_ENGINEER,
    PROFILES,
)


@pytest.mark.parametrize(
    ("profile", "tokens"),
    [
        (
            FULL_STACK_DEVELOPER,
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
        ),
        (
            MACHINE_LEARNING_ENGINEER,
            ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"],
        ),
        (
            DEVOPS_ENGINEER,
            ["LINUX", "BASH", "DOCKER", "GITHUB_ACTIONS", "AWS", "GIT"],
        ),
        (
            DATA_ENGINEER,
            ["PYTHON", "POSTGRESQL", "APACHE_SPARK", "APACHE_AIRFLOW", "GIT"],
        ),
    ],
)
def test_accepts_valid_pattern_for_each_profile(profile, tokens):
    assert accepts(profile, tokens)


@pytest.mark.parametrize("profile", PROFILES)
def test_rejects_pattern_missing_each_required_category(profile):
    for missing_index, missing_category in enumerate(profile.categories):
        if not missing_category.required:
            continue

        tokens = [
            next(iter(category.tokens))
            for index, category in enumerate(profile.categories)
            if index != missing_index and category.required
        ]
        assert not accepts(profile, tokens)


def test_optional_categories_can_be_omitted_and_category_can_have_multiple_tokens():
    assert accepts(
        MACHINE_LEARNING_ENGINEER,
        ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "SQL", "GIT"],
    )
    assert accepts(
        FULL_STACK_DEVELOPER,
        ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "REST_API", "GIT"],
    )


def test_rejects_tokens_outside_profile_and_out_of_order_tokens():
    assert not accepts(FULL_STACK_DEVELOPER, ["JAVASCRIPT", "RUST", "GIT"])
    assert not accepts(
        FULL_STACK_DEVELOPER,
        ["REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL", "GIT"],
    )


def test_build_automaton_returns_a_deterministic_finite_automaton():
    assert isinstance(
        build_automaton(FULL_STACK_DEVELOPER), DeterministicFiniteAutomaton
    )


@pytest.mark.parametrize(
    ("resume_name", "profile_key"),
    [
        ("wednesday_addams", "FULL_STACK_DEVELOPER"),
        ("mary_jane_watson", "MACHINE_LEARNING_ENGINEER"),
    ],
)
def test_screen_classifies_assignment_resumes(resume_name, profile_key):
    resume_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "resumes"
        / f"{resume_name}.txt"
    )
    result = screen(resume_path.read_text(encoding="utf-8"))

    assert profile_key in result.accepted_profiles
