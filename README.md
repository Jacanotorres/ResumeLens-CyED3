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

Requires Python 3.11 or later.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run the project commands
with `.\.venv\Scripts\python.exe` instead.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Graphviz is optional. Install it and use the `dot` command to render the
included transducer diagram in `docs/diagrams/`.

## Usage

Run commands from the repository root. The input must be a UTF-8 plain-text
résumé. The CLI prints normalized skills and an `ACCEPTED` or `REJECTED`
result for each supported profile.

```powershell
python -m resumelens data/resumes/wednesday_addams.txt
python -m resumelens data/resumes/mary_jane_watson.txt
python -m resumelens data/resumes/devops_engineer.txt
python -m resumelens data/resumes/data_engineer.txt
```

Use `--dsl` and `--html` to write the validated candidate-profile language and
its HTML visualization. Both options can be used together:

```powershell
New-Item -ItemType Directory -Force output | Out-Null
python -m resumelens data/resumes/wednesday_addams.txt `
  --dsl output/wednesday.rl `
  --html output/wednesday.html
```

On macOS or Linux, create the `output` directory with `mkdir -p output`. The
CLI does not create output directories.

## Tests

```powershell
python -m pytest
```

```bash
python -m pytest
```

## Project documentation

See [`docs/README.md`](docs/README.md) for the design documents, including the
module architecture, formal models, test scenarios, and AI usage log.

## Repository layout

```
resumelens/          source code for the four pipeline stages
  profiles.py        the four profiles as data (categories + canonical order)
  pipeline.py        runs extraction, normalization, and classification
  dsl/               textX grammar, validator, builder, and HTML renderer
data/resumes/        sample résumés for all four profiles
docs/                design documents and diagrams
tests/               pytest test suite
```

## Team

| Member                   | Student ID | GitHub        |
|--------------------------|------------|---------------|
| Juan Andrés Cano Torres  |            | @Jacanotorres |
| Samuel Cardoso Martinez  | A00410894  | @samuel230674 |
|  Juan Felipe Martinez    | A00412033  | @JUANFIX1     |

IDE: _to be filled_ · Course code: _09772 / 09834_ · Group: _1 / 3 / 5_
