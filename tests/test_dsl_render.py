"""Stage 4 tests - HTML rendering of a candidate profile."""

from resumelens.dsl.render import render_html
from resumelens.dsl.validator import validate

DSL = """candidate "Ann <Admin> Lee" {
  contact {
    email: "ann@example.com"
  }
  education: "B.Sc. Computer Science"
  experience {
    years: 2
    description: "backend work"
  }
  skills: PYTHON, GIT
  classification {
    FULL_STACK_DEVELOPER: REJECTED
    DATA_ENGINEER: ACCEPTED
  }
}
"""


def test_html_contains_main_sections():
    html = render_html(validate(DSL))
    assert html.startswith("<!DOCTYPE html>")
    assert "ann@example.com" in html
    assert "PYTHON" in html
    assert "Data Engineer" in html


def test_verdicts_are_shown():
    html = render_html(validate(DSL))
    assert "ACCEPTED" in html and "REJECTED" in html


def test_text_is_html_escaped():
    html = render_html(validate(DSL))
    assert "Ann &lt;Admin&gt; Lee" in html
    assert "<Admin>" not in html