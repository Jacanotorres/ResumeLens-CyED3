# 3. Formalization

## 3.1 Stage 1 — Regular expressions

Stage 1 applies Python's `re` patterns to the résumé text. Contact, education,
experience, and skill patterns use `findall` or `finditer`; the name pattern
uses `fullmatch` on the first non-empty line. `LINK_RE`, `EDUCATION_RE`,
`EXPERIENCE_RE`, and the skill patterns are compiled with `re.IGNORECASE`;
`Express` is the exception within the skill patterns and is case-sensitive.

| Information | Pattern in `resumelens/extraction.py` | Language recognized; example accepted / not recognized |
|-------------|------------------------------------------|--------------------------------------------------------|
| Name | `NAME_RE` (below) | Two to four capitalized name words, including supported Spanish accents, apostrophes, and hyphens. `Wednesday Addams` / `curriculum vitae 2026`. |
| Email | `EMAIL_RE` (below) | ASCII alphanumeric and permitted punctuation in the local part, followed by a dotted domain and a final 2+ letter suffix. `mj.watson@example.com` / `mj@example`. |
| Phone | `PHONE_RE` (below) | Optional country code and parenthesized area code, followed by digit groups with optional spaces, dots, or hyphens; digit boundaries prevent matching inside longer words. `+57 300 123 4567` / `12 34`. |
| Links | `LINK_RE` (below), case-insensitive | HTTP(S) URLs, `www.` URLs, or bare `github.com/...` and `linkedin.com/...` paths. `https://github.com/mj` / `example.com/mj`. |
| Education | `EDUCATION_RE` (below), case-insensitive | A whole line containing a supported degree or institution keyword. `B.Sc. in Computer Science` / `Software Engineer` (no listed keyword). |
| Experience | `EXPERIENCE_RE` (below), case-insensitive | One or two digits, optional `+`, a supported English or Spanish duration unit, and the phrase `experience`; the optional description ends at the next period or newline. `3 years of experience developing apps` / `three years of experience`. |
| Programming languages | `SKILL_RES["languages"]` (below) | Listed language names and abbreviations, matched case-insensitively as standalone skills. `JavaScript` / `JavaScript` does not produce an additional `Java` match. |
| Frameworks and APIs | `SKILL_RES["frameworks"]` (below) | Listed front-end and back-end names, Spring Boot, REST/RESTful APIs, and GraphQL. `React.js` / `ReactNative` (no standalone match). `Express` is intentionally case-sensitive. |
| Libraries | `SKILL_RES["libraries"]` (below) | Pandas, NumPy, supported Scikit-learn spellings, TensorFlow, PyTorch, and Keras. `scikit-learn` / `scikit`. |
| Databases | `SKILL_RES["databases"]` (below) | Listed SQL and NoSQL database names, including Snowflake and BigQuery variants. `PostgreSQL` / `NoSQL` (the `SQL` substring is not matched). |
| Tools and technologies | `SKILL_RES["tools"]` (below) | Listed version-control, CI/CD, infrastructure, operating-system, cloud, and data-platform terms. `GitHub Actions` / `GitHub` (the `Git` substring is not matched). |
| Practices | `SKILL_RES["practices"]` (below) | Machine-learning model-development phrases and predictive model(s). `predictive models` / `model development` (without `machine` or `ml`). |

The contact, education, and experience patterns are:

```python
NAME_RE = r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ'’-]+(?:[ \t]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ'’-]+){1,3}"
EMAIL_RE = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
PHONE_RE = r"(?<![\w+])(?:\+\d{1,3}[ .-]?)?(?:\(\d{2,4}\)[ .-]?)?\d{3}[ .-]?\d{3}[ .-]?\d{2,4}(?![\w])"
LINK_RE = r"(?:https?://|www\.)[^\s,;<>()]+|(?<![\w/@.])(?:linkedin\.com|github\.com)/[^\s,;<>()]+"
EDUCATION_RE = r"^[^\n]*\b(?:bachelor|b\.?sc|master|m\.?sc|ph\.?d|degree|diploma|ingenier[ií]a|licenciatura|maestr[ií]a|university|universidad|college)\b[^\n]*$"
EXPERIENCE_RE = r"(\d{1,2})\+?[ \t]*(?:years?|yrs?|años?)[ \t]+(?:of[ \t]+)?experience[ \t]*(?:(?:in|with|as|on)[ \t]+|:[ \t]*)?([^.\n]*)"
```

The six skill families share the boundary `(?<![\w.])` before the alternative
and `(?!\w)` after it, with `re.IGNORECASE`. These boundaries prevent
substrings such as `js` inside `NodeJS` and `SQL` inside `PostgreSQL` from
being reported as separate skills. Matches preserve the original spelling and
are returned in text order; normalization and deduplication belong to Stage 2.

```python
languages = r"java[ ]?script|js|type[ ]?script|ts|python|java|scala|bash"
frameworks = (
    r"react(?:[ ]?\.?[ ]?js)?|angular(?:[ ]?\.?[ ]?js)?|vue(?:[ ]?\.?[ ]?js)?|"
    r"node(?:[ ]?\.?[ ]?js)?|(?-i:Express)(?:[ ]?\.?[ ]?js)?|django|flask|"
    r"spring[ -]?boot|rest(?:ful)?[ ]+apis?|graphql"
)
libraries = r"pandas|numpy|scikit[ -]?learn|sklearn|tensor[ -]?flow|py[ -]?torch|keras"
databases = r"postgres(?:ql)?|my[ ]?sql|sqlite|sql|mongo[ ]?db|redis|snowflake|big[ ]?query"
tools = (
    r"git|docker|kubernetes|k8s|jenkins|github[ ]?actions|gitlab(?:[ -]?ci)?|"
    r"terraform|ansible|linux|aws|amazon[ ]web[ ]services|azure|gcp|google[ ]cloud|"
    r"(?:apache[ ])?spark|hadoop|(?:apache[ ])?kafka|(?:apache[ ])?airflow|dbt"
)
practices = r"(?:machine|ml)[ -](?:learning[ ])?model[ ]development|predictive[ ]models?"
```

## 3.2 Stage 2 — Finite-state transducers

`build_transducer` constructs one finite-state transducer from the entries in
`SKILL_VARIANTS`. Before translation, `normalize` strips surrounding
whitespace and applies Unicode case folding. For a variant `v` of length
`m`, the transducer follows a separate character-by-character path and emits
the canonical token only on its last transition.

For the current variant table, the transducer is
`M = (Q, Σ, Γ, δ, ω, q₀, F)`:

- `Q = {q₀} ∪ {qᵥ,ᵢ | v ∈ V, 1 ≤ i ≤ |v|}`, where `V` is the set of distinct,
  stripped and case-folded surface forms. Each variant has its own path states.
- `Σ = ⋃ᵥ chars(v)`, the characters appearing in the surface forms.
- `Γ = {SKILL_VARIANTS[v] | v ∈ V}`, the set of canonical skill tokens.
- `q₀` is the shared initial state.
- `F = {qᵥ,|v| | v ∈ V}`, the last state on each variant path.
- For each variant `v = c₁…cₘ`, `δ` has the transitions
  `(q₀, c₁, qᵥ,₁)` and `(qᵥ,ᵢ₋₁, cᵢ, qᵥ,ᵢ)` for `2 ≤ i ≤ m`.
- `ω` outputs the empty string on all but the last transition of a path;
  on the last transition it outputs `SKILL_VARIANTS[v]`. In the `pyformlang`
  implementation, that output is represented as an empty list or a
  single-token list, respectively.

The diagram shows two actual entries from the table. `eps` on an edge means
that the transition emits no output; the last edge emits `JAVASCRIPT`.
Other variants have their own paths constructed by the same rule.

```text
                         j/eps  s/JAVASCRIPT
                        ┌───→ q(JS,1) → ((q(JS,2)))
                       /
                     → q₀
                       \
                        └───→ q(javascript,1) → … → ((q(javascript,10)))
                         j/eps   a/eps  v/eps  a/eps  s/eps  c/eps  r/eps  i/eps  p/eps  t/JAVASCRIPT
```

Here `q₀` is the initial state and double parentheses mark accepting states.
The source diagram for this example is
[`diagrams/fst-javascript.dot`](diagrams/fst-javascript.dot). It represents
the two illustrated paths, not the full variant table.

## 3.3 Stage 3 — Finite automata

The classifier builds one ε-NFA from each profile's ordered categories. For a
profile with categories `C₁, …, Cₙ`, each required category contributes
`Cᵢ⁺` and each optional category contributes `Cᵢ*`, where `Cᵢ` is the set of
canonical tokens for that category. The ε-NFA is converted to a minimized DFA
by `pyformlang`; both forms recognize the same language.

For the ε-NFA `M = (Q, Σ, δ, q₀, F)`:

- `Q = {q₀, …, qₙ}`, with one state at each category boundary.
- `Σ` is the profile's canonical token alphabet.
- `δ` maps a state and an input token (or ε) to a set of states.
- For each category `Cᵢ` and token `a ∈ Cᵢ`, add
  `qᵢ₋₁ --a--> qᵢ` and a self-loop `qᵢ --a--> qᵢ`.
- For an optional category `Cᵢ`, also add `qᵢ₋₁ --ε--> qᵢ`.
- The initial state is `q₀`; the only accepting state is `qₙ`.

The transition schema is repeated for every category:

```text
q(i-1) -- a ∈ Cᵢ --> q(i) -- a ∈ Cᵢ --> q(i)
   |                     (self-loop for additional tokens)
   +---- ε ------------> q(i)     (optional category only)
```

The profile-specific patterns are the category sequences defined in
`resumelens/profiles.py`:

| Profile | Required categories in order | Optional categories |
|---------|------------------------------|--------------------|
| Full Stack Developer | Frontend language, frontend framework, backend, database, version control | API |
| Machine Learning Engineer | Language, data processing, ML library, database, version control | ML practice |
| DevOps Engineer | Operating system, scripting, containers, CI/CD, cloud, version control | Orchestration, infrastructure as code |
| Data Engineer | Language, database, big data, orchestration, version control | Cloud / warehouse |

Each category accepts any token in its set (for example, the Full Stack
frontend-framework category accepts `REACT`, `ANGULAR`, or `VUE`). Inputs are
the canonical tokens sorted by profile category; missing required categories,
out-of-order tokens, and tokens outside the profile alphabet are rejected.

### Per-profile definitions and diagrams

The complete 5-tuple, the δ table and the transition diagram of each of the
four automata are in [`diagrams/profile-automata.md`](diagrams/profile-automata.md).
That file is generated from `resumelens/profiles.py` with
`python -m resumelens.diagrams`, so the documentation and the implemented
automata cannot diverge (`tests/test_diagrams.py` checks it).

| Profile | Pattern | \|Q\| (ε-NFA) | \|Σ\| | ε-transitions | \|Q\| (minimal DFA) |
|---------|---------|-------------|-----|---------------|--------------------|
| Full Stack Developer | `C1⁺ C2⁺ C3⁺ C4⁺ C5* C6⁺` | 7 | 19 | 1 | 7 |
| Machine Learning Engineer | `C1⁺ C2⁺ C3⁺ C4* C5⁺ C6⁺` | 7 | 12 | 1 | 7 |
| DevOps Engineer | `C1⁺ C2⁺ C3⁺ C4* C5⁺ C6⁺ C7* C8⁺` | 9 | 14 | 2 | 9 |
| Data Engineer | `C1⁺ C2⁺ C3⁺ C4⁺ C5* C6⁺` | 7 | 18 | 1 | 7 |

### Type of automaton

The four automata, as constructed, are **ε-NFAs**:

- Every profile has at least one optional category, and skipping it is
  modeled with a transition `δ(qᵢ₋₁, ε) = {qᵢ}`. A DFA cannot have
  ε-transitions, so the constructed machine is not a DFA.
- Apart from ε, the machine has no nondeterministic choice. The categories of
  a profile are disjoint (`tests/test_profiles.py`), so in each state a token
  `a` has at most one move: the self-loop if `a ∈ Cᵢ`, or the step to `qᵢ₊₁`
  if `a ∈ Cᵢ₊₁`. If ε were removed, the machine would be a (partial) DFA.
- A profile with only required categories would therefore be built directly
  as a DFA; the ε-transitions are the only reason the general construction
  needs an ε-NFA.

For execution, `build_automaton` applies the subset construction
(`to_deterministic`) and minimization. For an optional category `Cᵢ`, the
state reached after `Cᵢ₋₁` becomes the subset `ε-closure(qᵢ₋₁) = {qᵢ₋₁, qᵢ}`,
which can either read `Cᵢ` or jump to `Cᵢ₊₁`. The result again has one state
per category boundary (`n + 1` states); undefined transitions (tokens out of
order or outside Σ) go to an implicit dead state. The tests check that the
ε-NFA and the minimal DFA are equivalent for all four profiles.

## 3.4 Stage 4 — Candidate profile grammar (EBNF)

Grammar in EBNF, terminals and non-terminals, and structural characteristics of
the language.

### Grammar (EBNF)

```ebnf
Candidate      = "candidate" STRING "{" Contact { Education } { Experience } Skills Classification "}" ;
Contact        = "contact" "{" { ContactItem } "}" ;
ContactItem    = ( "email" | "phone" | "link" ) ":" STRING ;
Education      = "education" ":" STRING ;
Experience     = "experience" "{" "years" ":" INT [ "description" ":" STRING ] "}" ;
Skills         = "skills" ":" TOKEN { "," TOKEN } ;
Classification = "classification" "{" ProfileResult { ProfileResult } "}" ;
ProfileResult  = PROFILE_KEY ":" VERDICT ;
```

### Terminals and non-terminals

- **Non-terminals:** Candidate, Contact, ContactItem, Education, Experience, Skills, Classification, ProfileResult.
- **Terminals:** the keywords (`candidate`, `contact`, `email`, `phone`, `link`, `education`, `experience`, `years`, `description`, `skills`, `classification`), the symbols `{ } : ,` and the lexical classes:
  - `STRING` = `"` { any character except `"` } `"`
  - `INT` = digit { digit }
  - `TOKEN` = [A-Z] { [A-Z] | [0-9] | `_` } (canonical token, e.g. `NODE_JS`)
  - `PROFILE_KEY` = `FULL_STACK_DEVELOPER` | `MACHINE_LEARNING_ENGINEER` | `DEVOPS_ENGINEER` | `DATA_ENGINEER`
  - `VERDICT` = `ACCEPTED` | `REJECTED`

### Structural characteristics

The candidate profile language has the following structural characteristics:

- **Context-free (Chomsky type 2).** Every production has a single non-terminal on its left-hand side, so the language is specified by a context-free grammar and parsed into a tree (the textX model). The nesting depth is fixed (a `candidate` contains blocks, and blocks contain only flat items), so a finite automaton could also recognize the language; the grammar is used because it gives the hierarchical structure needed to build the model.
- **Hierarchical.** `Candidate` is the root. `Contact`, `Experience` and `Classification` are nested blocks delimited by braces.
- **Repetition.** `ContactItem`, `Education`, `Experience` and `ProfileResult` can repeat, and `TOKEN` repeats separated by commas (at least one skill is required).
- **Optional parts.** Education records, experience records and the `description` of an experience may be omitted. The `contact` block, the skills and the classification are mandatory.
- **Fixed section order.** Sections appear as contact, education, experience, skills, classification. The order of the items inside a repeated section is free.
- **Free layout.** Whitespace and line breaks have no meaning; blocks are delimited by braces, not by indentation.
- **No keyword clashes.** Keywords are lowercase and `TOKEN` must start with an uppercase letter, so a skill can never be mistaken for a keyword.
- **Unambiguous.** Every alternative starts with a different keyword or literal, so each valid text has exactly one derivation.
- **Lexical and syntactic errors are rejected.** Lexical: a lowercase token, a non-integer `years`, a name without quotes. Syntactic: a missing brace or sections out of order. textX reports the line and column of the error.
- **Limits.** The grammar does not check semantic constraints such as duplicated skills or repeated profile keys; the builder (`to_dsl`) guarantees them by construction.
