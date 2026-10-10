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

For each of the four profiles, M = (Q, Σ, δ, q₀, F), automaton type (DFA / NFA /
ε-NFA) with justification, transition diagram and the profile pattern it
represents.

### Full Stack Developer
_TODO_

### Machine Learning Engineer
_TODO_

### DevOps Engineer
_TODO_

### Data Engineer
_TODO_

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

_(se completa en el commit 9)_
