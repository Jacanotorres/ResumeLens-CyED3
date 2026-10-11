"""Stage 4 tests - CLI output options (--dsl and --html)."""

from resumelens import __main__ as cli
from resumelens.extraction import ExtractionResult
from resumelens.pipeline import ProfileMatch, ScreeningResult


def fake_screen(_text):
    return ScreeningResult(
        ExtractionResult(name="Wednesday Addams", emails=["wed@nevermore.edu"]),
        ["JAVASCRIPT", "GIT"],
        [ProfileMatch("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "GIT"], False)],
    )


def test_cli_writes_dsl_and_html(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "screen", fake_screen)
    resume = tmp_path / "resume.txt"
    resume.write_text("any text", encoding="utf-8")
    dsl_file, html_file = tmp_path / "out.rl", tmp_path / "out.html"

    code = cli.main([str(resume), "--dsl", str(dsl_file), "--html", str(html_file)])

    assert code == 0
    assert dsl_file.read_text(encoding="utf-8").startswith('candidate "Wednesday Addams"')
    assert "<h1>Wednesday Addams</h1>" in html_file.read_text(encoding="utf-8")


def test_cli_fails_cleanly_without_skills(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        cli, "screen", lambda _t: ScreeningResult(ExtractionResult(), [], [])
    )
    resume = tmp_path / "resume.txt"
    resume.write_text("any text", encoding="utf-8")

    code = cli.main([str(resume), "--dsl", str(tmp_path / "out.rl")])

    assert code == 1
    assert "Could not build the candidate profile" in capsys.readouterr().err