import pytest

from resumelens.normalization import (
    SKILL_VARIANTS,
    build_transducer,
    normalize,
    normalize_all,
    sort_for_profile,
)
from resumelens.extraction import extract
from resumelens.profiles import FULL_STACK_DEVELOPER, MACHINE_LEARNING_ENGINEER, PROFILES


@pytest.mark.parametrize(
    ("surface", "canonical"),
    [
        ("JS", "JAVASCRIPT"),
        ("JavaScript", "JAVASCRIPT"),
        ("React.js", "REACT"),
        ("React js", "REACT"),
        ("React . js", "REACT"),
        ("AngularJS", "ANGULAR"),
        ("Vue.js", "VUE"),
        ("NodeJS", "NODE_JS"),
        ("Node js", "NODE_JS"),
        ("Postgres", "POSTGRESQL"),
        ("My SQL", "MYSQL"),
        ("Scikit-learn", "SCIKIT_LEARN"),
        ("sklearn", "SCIKIT_LEARN"),
        ("Tensor Flow", "TENSORFLOW"),
        ("Py Torch", "PYTORCH"),
        ("Predictive models", "ML_MODEL_DEVELOPMENT"),
        ("Amazon Web Services", "AWS"),
        ("K8S", "KUBERNETES"),
        ("GitHubActions", "GITHUB_ACTIONS"),
        ("GitLabCI", "GITLAB_CI"),
    ],
)
def test_normalize_supported_skill_variants(surface, canonical):
    assert normalize(surface) == canonical


def test_normalize_ignores_case_and_surrounding_whitespace():
    assert normalize("  rEaCt.Js  ") == "REACT"


@pytest.mark.parametrize("unknown", ["", "   ", "Rust", "React Native"])
def test_normalize_returns_none_for_unknown_skills(unknown):
    assert normalize(unknown) is None


def test_normalize_all_deduplicates_and_preserves_first_occurrence_order():
    assert normalize_all(["JS", "javascript", "Unknown", "React.js", "REACT"]) == [
        "JAVASCRIPT",
        "REACT",
    ]


def test_every_profile_token_has_a_normalization_variant():
    supported_tokens = set(SKILL_VARIANTS.values())
    assert all(token in supported_tokens for profile in PROFILES for token in profile.alphabet)


@pytest.mark.parametrize(
    ("surface", "canonical"),
    [
        ("JS", "JAVASCRIPT"),
        ("Javascript", "JAVASCRIPT"),
        ("JavaScript", "JAVASCRIPT"),
        ("React.js", "REACT"),
        ("ReactJS", "REACT"),
        ("React", "REACT"),
        ("NodeJS", "NODE_JS"),
        ("Node.js", "NODE_JS"),
        ("Node js", "NODE_JS"),
        ("Postgres", "POSTGRESQL"),
        ("PostgreSQL", "POSTGRESQL"),
        ("sklearn", "SCIKIT_LEARN"),
        ("scikit learn", "SCIKIT_LEARN"),
        ("Scikit-learn", "SCIKIT_LEARN"),
        ("Tensor Flow", "TENSORFLOW"),
        ("TensorFlow", "TENSORFLOW"),
        ("Py Torch", "PYTORCH"),
        ("PyTorch", "PYTORCH"),
        ("Pandas", "PANDAS"),
        ("NumPy", "NUMPY"),
        ("Spring Boot", "SPRING_BOOT"),
        ("MongoDB", "MONGODB"),
        ("GitHub Actions", "GITHUB_ACTIONS"),
    ],
)
def test_extracted_surface_forms_can_be_normalized(surface, canonical):
    raw_skills = extract(f"Skills: {surface}, Git.").raw_skills()
    assert normalize(raw_skills[0]) == canonical


def test_sort_for_profile_projects_and_orders_by_category_stably():
    tokens = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT", "TYPESCRIPT", "AWS"]

    assert sort_for_profile(tokens, FULL_STACK_DEVELOPER) == [
        "JAVASCRIPT",
        "TYPESCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]
    assert sort_for_profile(tokens, MACHINE_LEARNING_ENGINEER) == ["POSTGRESQL", "GIT"]


def test_build_transducer_translates_casefolded_input():
    transducer = build_transducer({"React": "REACT"})

    assert list(transducer.translate("react")) == [["REACT"]]
    assert list(transducer.translate("Vue")) == []


def test_build_transducer_rejects_conflicting_case_insensitive_variants():
    with pytest.raises(ValueError, match="conflicting canonical tokens"):
        build_transducer({"JS": "JAVASCRIPT", "js": "OTHER"})
