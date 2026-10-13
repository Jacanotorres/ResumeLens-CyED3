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

The automaton diagrams in `docs/diagrams/profile-automata.md` are written in
Mermaid and render directly on GitHub. Graphviz is optional; it is only needed
to render the transducer example `docs/diagrams/fst-javascript.dot` with `dot`.

## Usage

Run commands from the repository root. The input must be a UTF-8 plain-text
résumé. The CLI prints normalized skills and an `ACCEPTED` or `REJECTED`
result for each supported profile.

```powershell
python -m resumelens data/resumes/wednesday_addams.txt
python -m resumelens data/resumes/mary_jane_watson.txt
python -m resumelens data/resumes/devops_engineer.txt
python -m resumelens data/resumes/data_engineer.txt
python -m resumelens data/resumes/frontend_developer.txt
python -m resumelens data/resumes/platform_data_engineer.txt
```

The last two are edge cases: a frontend-only résumé that no profile accepts,
and a résumé accepted by both DevOps Engineer and Data Engineer.

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
module architecture, formal models, test scenarios, results, and AI usage log.

The research poster is [`docs/poster/poster.pdf`](docs/poster/poster.pdf) (48 × 36 in) and the
presentation is [`docs/presentation/presentation.pdf`](docs/presentation/presentation.pdf).

Two documents are generated from the code and checked by the tests; regenerate
them after changing a profile, the pipeline or the sample résumés:

```bash
python -m resumelens.diagrams   # docs/diagrams/profile-automata.md
python -m resumelens.results    # docs/06-results.md and docs/examples/
```

## Repository layout

```
resumelens/            source code for the four pipeline stages
  extraction.py        Stage 1: regular expressions
  normalization.py     Stage 2: finite-state transducer and profile sorting
  classification.py    Stage 3: ε-NFA per profile and its minimal DFA
  dsl/                 Stage 4: textX grammar, validator, builder, HTML renderer
  profiles.py          the four profiles as data (categories + canonical order)
  pipeline.py          runs extraction, normalization, and classification
  diagrams.py          generates the automata definitions and diagrams
  results.py           generates the results report and examples
  __main__.py          command-line interface
data/resumes/          sample résumés (one per profile plus two edge cases)
docs/                  design documents, diagrams, results
  examples/            validated candidate profiles (.rl) and HTML pages
tests/                 pytest test suite
```

## Team

| Member                  | GitHub        |
|-------------------------|---------------|
| Juan Andrés Cano Torres | @Jacanotorres |
| Samuel Cardoso Martinez | @samuel230674 |
| Juan Felipe Martinez    | @JUANFIX1     |

| Course code | Group | Professor | IDE | Language |
|-------------|-------|-----------|-----|----------|
| 09834 | 3 | Andrés | Visual Studio Code | Python 3.11+ (tested with 3.14) |
