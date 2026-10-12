from pathlib import Path

import pytest

from resumelens.pipeline import screen


RESUMES = Path(__file__).resolve().parent.parent / "data" / "resumes"


@pytest.mark.parametrize(
    ("resume_name", "expected_profile"),
    [
        ("devops_engineer", "DEVOPS_ENGINEER"),
        ("data_engineer", "DATA_ENGINEER"),
    ],
)
def test_team_defined_profile_resumes_are_classified(resume_name, expected_profile):
    resume = (RESUMES / f"{resume_name}.txt").read_text(encoding="utf-8")

    result = screen(resume)

    assert result.accepted_profiles == [expected_profile]


def test_resume_can_match_multiple_profiles():
    resume = """Jordan Lee
Technical Skills:
Linux, Python, Docker, Kubernetes, PostgreSQL, Apache Spark, Apache Airflow,
GitHub Actions, AWS, Terraform, Git.
"""

    result = screen(resume)

    assert result.accepted_profiles == ["DEVOPS_ENGINEER", "DATA_ENGINEER"]


def test_resume_missing_required_devops_category_is_rejected():
    resume = """Alex Morgan
Technical Skills:
Linux, Bash, Kubernetes, GitHub Actions, AWS, Terraform, Git.
"""

    result = screen(resume)
    devops_match = next(
        match for match in result.matches if match.profile_key == "DEVOPS_ENGINEER"
    )

    assert not devops_match.accepted


def test_unusual_skill_order_and_casing_still_match_devops_profile():
    resume = """Alex Morgan
Technical Skills:
GIT, AWS, GITHUB ACTIONS, Docker, BASH, Linux.
"""

    result = screen(resume)
    devops_match = next(
        match for match in result.matches if match.profile_key == "DEVOPS_ENGINEER"
    )

    assert devops_match.accepted
    assert devops_match.sequence == [
        "LINUX",
        "BASH",
        "DOCKER",
        "GITHUB_ACTIONS",
        "AWS",
        "GIT",
    ]
