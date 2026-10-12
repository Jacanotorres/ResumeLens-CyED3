# 3. Formalization

## 3.1 Stage 1 — Regular expressions

For each information type: the regular expression, the language it recognizes,
and examples of accepted / rejected strings.

| Information | Regex | Language described | Examples |
|-------------|-------|--------------------|----------|
| Email | _TODO_ | | |
| Phone | _TODO_ | | |
| Links (GitHub, LinkedIn) | _TODO_ | | |
| Years of experience | _TODO_ | | |
| Academic qualifications | _TODO_ | | |
| Programming languages | _TODO_ | | |
| Frameworks and libraries | _TODO_ | | |
| Databases | _TODO_ | | |
| Tools and technologies | _TODO_ | | |

## 3.2 Stage 2 — Finite-state transducers

For each transducer M = (Q, Σ, Γ, δ, ω, q₀, F):

- Q — set of states
- Σ — input alphabet
- Γ — output alphabet
- δ — transition relation
- ω — output relation
- q₀ — initial state
- F — accepting states
- Diagram (`diagrams/`)

_TODO_

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
