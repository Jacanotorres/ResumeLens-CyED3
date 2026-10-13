from pathlib import Path

import pytest

from resumelens.pipeline import screen
from resumelens.profiles import FULL_STACK_DEVELOPER, MACHINE_LEARNING_ENGINEER, get_profile
from resumelens.results import EXAMPLES, OUTPUT, build, missing_required

RESUMES = Path(__file__).resolve().parent.parent / "data" / "resumes"


def _accepted(resume_name):
    return screen((RESUMES / resume_name).read_text(encoding="utf-8")).accepted_profiles


def test_missing_required_lists_only_required_categories():
    tokens = ["JAVASCRIPT", "REACT", "GIT"]
    assert missing_required(FULL_STACK_DEVELOPER, tokens) == ["Backend", "Database"]


def test_missing_required_is_empty_when_pattern_is_covered():
    tokens = ["PYTHON", "NUMPY", "PYTORCH", "SQL", "GIT"]
    assert missing_required(MACHINE_LEARNING_ENGINEER, tokens) == []


def test_frontend_only_resume_is_a_near_miss():
    assert _accepted("frontend_developer.txt") == []


def test_platform_data_engineer_matches_two_profiles():
    assert _accepted("platform_data_engineer.txt") == ["DEVOPS_ENGINEER", "DATA_ENGINEER"]


@pytest.mark.parametrize("resume", sorted(RESUMES.glob("*.txt")), ids=lambda p: p.stem)
def test_rejections_are_explained_by_missing_categories(resume):
    result = screen(resume.read_text(encoding="utf-8"))
    for match in result.matches:
        missing = missing_required(get_profile(match.profile_key), match.sequence)
        assert match.accepted == (missing == [])


def test_generated_results_are_up_to_date():
    document, examples = build()
    assert OUTPUT.read_text(encoding="utf-8") == document, (
        "Run `python -m resumelens.results` to regenerate docs/06-results.md"
    )
    for name, content in examples.items():
        assert (EXAMPLES / name).read_text(encoding="utf-8") == content, name
