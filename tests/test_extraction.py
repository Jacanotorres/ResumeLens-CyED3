from pathlib import Path

import pytest

from resumelens.extraction import Experience, extract

RESUMES = Path(__file__).resolve().parent.parent / "data" / "resumes"


def read(name: str) -> str:
    return (RESUMES / f"{name}.txt").read_text(encoding="utf-8")


# ---- the two résumés given in the assignment ------------------------------

def test_wednesday_addams_matches_assignment_example():
    r = extract(read("wednesday_addams"))
    assert r.name == "Wednesday Addams"
    assert r.experience == [Experience(3, "developing web applications")]
    assert r.raw_skills() == ["JS", "React.js", "NodeJS", "Postgres", "Git"]


def test_mary_jane_watson_skills():
    r = extract(read("mary_jane_watson"))
    assert r.name == "Mary Jane Watson"
    assert r.experience[0].years == 2
    assert r.raw_skills() == [
        "predictive models", "Python", "Pandas", "NumPy",
        "Scikit-learn", "TensorFlow", "SQL", "Git",
    ]


def test_skills_grouped_by_family():
    r = extract(read("wednesday_addams"))
    assert r.skills["languages"] == ["JS"]
    assert r.skills["frameworks"] == ["React.js", "NodeJS"]
    assert r.skills["databases"] == ["Postgres"]
    assert r.skills["tools"] == ["Git"]


# ---- surface-form variants are detected exactly as written ----------------

@pytest.mark.parametrize("variant", [
    "JS", "Javascript", "JavaScript", "React.js", "ReactJS", "React",
    "NodeJS", "Node.js", "Node js", "Postgres", "PostgreSQL",
    "sklearn", "scikit learn", "Scikit-learn", "Tensor Flow", "TensorFlow",
    "Py Torch", "PyTorch", "pandas", "Spring Boot", "MongoDB", "GitHub Actions",
])
def test_variants_are_extracted_unchanged(variant):
    assert extract(f"Skills: {variant}, Git.").raw_skills()[0] == variant


def test_extraction_does_not_normalize_or_deduplicate():
    r = extract("Skills: JS, Javascript, js")
    assert r.raw_skills() == ["JS", "Javascript", "js"]


# ---- boundaries: no false positives inside longer words -------------------

def test_js_not_found_inside_nodejs_or_react_js():
    assert extract("NodeJS, React.js").raw_skills() == ["NodeJS", "React.js"]


def test_java_not_found_inside_javascript():
    assert extract("JavaScript").raw_skills() == ["JavaScript"]


def test_sql_not_found_inside_postgresql_mysql_nosql():
    assert extract("PostgreSQL, MySQL, NoSQL").raw_skills() == ["PostgreSQL", "MySQL"]


def test_git_not_found_inside_github_and_express_word_ignored():
    assert extract("I like GitHub and want to express interest").raw_skills() == []


def test_express_framework_recognized_when_capitalized():
    assert extract("Express, Express.js").raw_skills() == ["Express", "Express.js"]


# ---- contact information --------------------------------------------------

CONTACT = """Mary Jane Watson
mj.watson@example.com | +57 300 123 4567
https://github.com/mjwatson, linkedin.com/in/mj-watson.
"""


def test_email_phone_links():
    r = extract(CONTACT)
    assert r.emails == ["mj.watson@example.com"]
    assert r.phones == ["+57 300 123 4567"]
    assert r.links == ["https://github.com/mjwatson", "linkedin.com/in/mj-watson"]


def test_years_of_experience_is_not_a_phone():
    assert extract("3 years of experience developing web applications.").phones == []


def test_name_rejected_when_first_line_is_not_a_name():
    assert extract("curriculum vitae 2026\nPython").name is None
    assert extract("").name is None


# ---- education and experience ---------------------------------------------

def test_education_lines():
    text = "Education:\nB.Sc. in Computer Science, Universidad Icesi, 2024\nMaster in AI\n"
    r = extract(text)
    assert r.education == [
        "B.Sc. in Computer Science, Universidad Icesi, 2024",
        "Master in AI",
    ]


def test_multiple_experiences():
    r = extract("5 yrs of experience in backend services. 2 years of experience with ML.")
    assert r.experience == [
        Experience(5, "backend services"),
        Experience(2, "ML"),
    ]


def test_empty_resume_gives_empty_result():
    r = extract("")
    assert r.raw_skills() == [] and r.emails == [] and r.experience == []