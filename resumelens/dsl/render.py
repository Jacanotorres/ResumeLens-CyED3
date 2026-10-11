"""Stage 4 - render a validated candidate profile as an HTML page."""

from __future__ import annotations

from html import escape


def _badge(verdict: str) -> str:
    color = "#2e7d32" if verdict == "ACCEPTED" else "#c62828"
    return (
        f'<span style="background:{color};color:#fff;padding:2px 10px;'
        f'border-radius:10px;font-size:0.85em">{escape(verdict)}</span>'
    )


def render_html(model) -> str:
    """Return a standalone HTML page for a textX candidate model."""
    contact = "".join(
        f"<li><b>{escape(item.kind)}:</b> {escape(item.value)}</li>"
        for item in model.contact.items
    )
    education = "".join(f"<li>{escape(e.degree)}</li>" for e in model.education)
    experience = "".join(
        f"<li>{e.years} year(s)"
        + (f" - {escape(e.description)}" if e.description else "")
        + "</li>"
        for e in model.experience
    )
    skills = " ".join(
        f'<span style="background:#e3f2fd;padding:2px 8px;border-radius:8px;'
        f'margin:2px;display:inline-block">{escape(token)}</span>'
        for token in model.skills.tokens
    )
    rows = "".join(
        f"<tr><td>{escape(r.profile.replace('_', ' ').title())}</td>"
        f"<td>{_badge(r.verdict)}</td></tr>"
        for r in model.classification.results
    )
    return (
        "<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\">"
        f"<title>{escape(model.name)} - ResumeLens</title></head>\n"
        '<body style="font-family:Arial,sans-serif;max-width:720px;margin:2em auto">\n'
        f"<h1>{escape(model.name)}</h1>\n"
        f"<h2>Contact</h2><ul>{contact}</ul>\n"
        f"<h2>Education</h2><ul>{education}</ul>\n"
        f"<h2>Experience</h2><ul>{experience}</ul>\n"
        f"<h2>Skills</h2><p>{skills}</p>\n"
        f"<h2>Profile classification</h2>\n"
        f'<table style="border-collapse:collapse;width:100%">{rows}</table>\n'
        "</body></html>\n"
    )