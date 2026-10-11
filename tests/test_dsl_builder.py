"""Stage 4 tests - building DSL text from a screening result."""

import pytest

from resumelens.dsl.builder import to_dsl
from resumelens.dsl.validator import validate
from resumelens.extraction import ExtractionResult, Experience
from resumelens.pipeline import ProfileMatch, ScreeningResult


def make_result(**overrides):
    extraction = ExtractionResult(
        name="Wednesday Addams",
        emails=["wed@nevermore.edu"],
        phones=["+57 300 123 4567"],
        links=["github.com/wed"],
        education=["B.Sc. Computer Science"],
        experience=[Experience(years=3, description="web development")],
    )
    matches = [
        ProfileMatch("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT"], True),
        ProfileMatch("MACHINE_LEARNING_ENGINEER", [], False),
        ProfileMatch("DEVOPS_ENGINEER", [], False),
        ProfileMatch("DATA_ENGINEER", [], False),
    ]
    values = dict(extraction=extraction, normalized=["JAVASCRIPT", "REACT", "GIT"], matches=matches)
    values.update(overrides)
    return ScreeningResult(**values)


def test_output_is_valid_dsl():
    model = validate(to_dsl(make_result()))
    assert model.name == "Wednesday Addams"
    assert model.skills.tokens == ["JAVASCRIPT", "REACT", "GIT"]
    assert model.education[0].degree == "B.Sc. Computer Science"
    assert model.experience[0].years == 3


def test_classification_reflects_matches():
    model = validate(to_dsl(make_result()))
    verdicts = {r.profile: r.verdict for r in model.classification.results}
    assert verdicts["FULL_STACK_DEVELOPER"] == "ACCEPTED"
    assert verdicts["DATA_ENGINEER"] == "REJECTED"


def test_missing_name_uses_unknown():
    result = make_result(extraction=ExtractionResult())
    assert validate(to_dsl(result)).name == "Unknown"


def test_quotes_in_text_are_escaped():
    extraction = ExtractionResult(name='Ann "AJ" Lee')
    model = validate(to_dsl(make_result(extraction=extraction)))
    assert "AJ" in model.name


def test_no_skills_raises_value_error():
    with pytest.raises(ValueError):
        to_dsl(make_result(normalized=[]))