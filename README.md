# ResumeLens — Formal Language-Based Resume Screening

Computación y Estructuras Discretas III — Universidad Icesi — 2026-2, Integrative Task 1.

ResumeLens processes plain-text résumés and decides whether the qualifications
explicitly written in them satisfy formally defined qualification patterns for
four professional profiles. It does **not** rank candidates or make hiring
decisions.

| Stage | Formal model | Library | Module |
|-------|--------------|---------|--------|
| 1. Extraction | Regular expressions | `re` | `resumelens/extraction.py` |
| 2. Normalization + sorting | Finite-state transducers | `pyformlang` | `resumelens/normalization.py` |
| 3. Pattern recognition | Finite automata (DFA / NFA / ε-NFA) | `pyformlang` | `resumelens/classification.py` |
| 4. Candidate profile DSL + visualization | Context-free grammar | `textX` | `resumelens/dsl/` |

Supported profiles (`resumelens/profiles.py`):

- Full Stack Developer *(reference)*
- Machine Learning Engineer *(reference)*
- DevOps Engineer *(team-defined, software engineering)*
- Data Engineer *(team-defined, AI/data)*

## Setup

Requires Python 3.11+ (developed with 3.14).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional, to render the automata/transducer diagrams to PNG: install Graphviz
(`brew install graphviz`).

## Usage

```bash
python -m resumelens data/resumes/wednesday_addams.txt --html output/wednesday.html
```

## Tests

```bash
pytest
```

## Repository layout

```
resumelens/          source code (one module per stage)
  profiles.py        the four profiles as data (categories + canonical order)
  pipeline.py        runs the four stages over one résumé
  dsl/               textX grammar, validator and HTML renderer
data/resumes/        sample résumés used in tests and demos
docs/                design documents (Markdown)
tests/               pytest test suite
```

## Team

| Member                   | Student ID | GitHub        |
|--------------------------|------------|---------------|
| Juan Andrés Cano Torres< |            | @Jacanotorres |
| Samuel Cardoso Martinez  | A00410894  | @samuel230674 |
|                          |            |               |
|                          |            |               |

IDE: _to be filled_ · Course code: _09772 / 09834_ · Group: _1 / 3 / 5_
