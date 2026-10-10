"""Stage 4 tests - candidate profile DSL validation (scenario S8)."""

import pytest

from resumelens.dsl.validator import DSLValidationError, validate

VALID = """candidate "Wednesday Addams" {
  contact {
    email: "wed@nevermore.edu"
  }
  experience {
    years: 3
    description: "developing web applications"
  }
  skills: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
  classification {
    FULL_STACK_DEVELOPER: ACCEPTED
    MACHINE_LEARNING_ENGINEER: REJECTED
    DEVOPS_ENGINEER: REJECTED
    DATA_ENGINEER: REJECTED
  }
}
"""


def test_valid_profile_is_accepted():
    model = validate(VALID)
    assert model.name == "Wednesday Addams"
    assert model.skills.tokens == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert model.experience[0].years == 3


def test_classification_results_are_parsed():
    model = validate(VALID)
    results = {r.profile: r.verdict for r in model.classification.results}
    assert results["FULL_STACK_DEVELOPER"] == "ACCEPTED"
    assert results["DATA_ENGINEER"] == "REJECTED"


def test_education_and_contact_are_optional_items():
    text = VALID.replace('email: "wed@nevermore.edu"', "")
    assert validate(text).contact.items == []


@pytest.mark.parametrize(
    "old, new",
    [
        ("JAVASCRIPT", "javascript"),                    # lexical: token must be uppercase
        ("FULL_STACK_DEVELOPER: ACCEPTED", "FULL_STACK_DEVELOPER: MAYBE"),  # invalid verdict
        ("FULL_STACK_DEVELOPER", "FRONTEND_DEVELOPER"),  # unknown profile
        ("years: 3", "years: three"),                    # years must be an integer
        ('candidate "Wednesday Addams"', 'candidate Wednesday'),  # name must be a string
        ("skills: JAVASCRIPT, REACT", "skills: JAVASCRIPT, , REACT"),  # empty list item
    ],
)
def test_invalid_profiles_are_rejected(old, new):
    with pytest.raises(DSLValidationError):
        validate(VALID.replace(old, new, 1))


def test_missing_closing_brace_is_rejected():
    with pytest.raises(DSLValidationError):
        validate(VALID.rstrip().rstrip("}"))


def test_empty_text_is_rejected():
    with pytest.raises(DSLValidationError):
        validate("")


def test_error_message_reports_line_and_column():
    with pytest.raises(DSLValidationError, match=r"line \d+, column \d+"):
        validate(VALID.replace("JAVASCRIPT", "javascript", 1))