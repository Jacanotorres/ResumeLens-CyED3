# 2. Design of modules

## 2.1 Architecture

ResumeLens is a linear pipeline. Each stage consumes the output of the previous
one and is implemented with a different formal model.

```
 résumé.txt
     │
     ▼
┌──────────────────────┐  ExtractionResult (contact, experience, education,
│ 1. extraction (re)   │  raw skill strings: "JS", "React.js", ...)
└──────────┬───────────┘
           ▼
┌──────────────────────┐  list[str] of canonical tokens, no duplicates
│ 2. normalization     │  ["JAVASCRIPT", "REACT", ...]
│    (FST)             │
└──────────┬───────────┘
           ▼  for each of the 4 profiles
┌──────────────────────┐  tokens of that profile, in its canonical order
│ 2b. sort_for_profile │  [JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]
└──────────┬───────────┘
           ▼
┌──────────────────────┐  ACCEPTED / REJECTED per profile
│ 3. classification    │
│    (finite automata) │
└──────────┬───────────┘
           ▼
┌──────────────────────┐  .rl DSL text → validated textX model → HTML
│ 4. dsl (CFG, textX)  │
└──────────────────────┘
```

**One general solution for the four profiles.** Profiles are data, not code
(`profiles.py`). A profile is an ordered list of *categories*; each category
is a set of canonical tokens and is either *required* or *optional*. Sorting
(stage 2b) and automaton construction (stage 3) are generic functions that
receive a `Profile`, so adding or replacing a profile does not change any
algorithm.

## 2.2 Modules

### `profiles.py`

| Element | Description |
|---------|-------------|
| `Category(name, tokens, required)` | A group of interchangeable canonical tokens, e.g. *Frontend framework* = {REACT, ANGULAR, VUE}. |
| `Profile(key, title, area, categories)` | `categories` is ordered: it is the canonical order of the profile. |
| `Profile.alphabet` | Union of all category tokens → Σ of the profile automaton. |
| `PROFILES` | The four supported profiles. |

### `extraction.py` — Stage 1

| Function | Input | Output |
|----------|-------|--------|
| `extract(text)` | Raw résumé text | `ExtractionResult` |
| `ExtractionResult.raw_skills()` | — | `list[str]` raw skill strings in order of appearance |

`ExtractionResult` fields: `name`, `emails`, `phones`, `links`, `education`,
`experience: list[Experience(years, description)]`,
`skills: dict[family, list[raw string]]`.

### `normalization.py` — Stage 2

| Function | Input | Output |
|----------|-------|--------|
| `build_transducer(variants)` | `{surface form: canonical token}` | pyformlang `FST` |
| `normalize(raw_skill)` | One raw string, e.g. `"React.js"` | `"REACT"` or `None` |
| `normalize_all(raw_skills)` | `list[str]` | `list[str]` canonical, unknowns and duplicates removed |
| `sort_for_profile(tokens, profile)` | Canonical tokens, `Profile` | Tokens of the profile, sorted by category order |

### `classification.py` — Stage 3

| Function | Input | Output |
|----------|-------|--------|
| `build_automaton(profile)` | `Profile` | pyformlang finite automaton |
| `accepts(profile, sorted_tokens)` | `Profile`, sorted tokens | `bool` |

**Pattern construction.** For a profile with categories C₁ … Cₙ the accepted
language is the concatenation

  L(P) = X₁ X₂ … Xₙ, where Xᵢ = Cᵢ⁺ if Cᵢ is required and Xᵢ = Cᵢ\* if optional.

`Cᵢ⁺` lets a résumé list several items of the same category (e.g. PANDAS NUMPY).
Optional categories introduce ε-transitions, so the natural construction is an
ε-NFA that is then converted to an equivalent minimal DFA.

### `pipeline.py`

| Function | Input | Output |
|----------|-------|--------|
| `screen(text)` | Raw résumé text | `ScreeningResult(extraction, normalized, matches)` |

`ProfileMatch(profile_key, sequence, accepted)` holds, for each profile, the
sorted sequence that was fed to its automaton and the verdict.

### `dsl/` — Stage 4

| Function | Input | Output |
|----------|-------|--------|
| `to_dsl(result)` | `ScreeningResult` | Candidate profile text in the DSL |
| `validate(text)` | DSL text | textX model, or a lexical/syntax error |
| `render_html(model)` | textX model | HTML string |

### `__main__.py` — CLI

`python -m resumelens <resume.txt> [--dsl out.rl] [--html out.html]`

## 2.3 Design decisions

| Decision | Rationale |
|----------|-----------|
| Profiles as data | The assignment requires one general solution for all profiles. |
| Projection before recognition | Each automaton only sees the tokens of its own alphabet; skills irrelevant to a profile neither help nor hurt. |
| Deduplicate after normalization | "JS" and "JavaScript" in the same résumé produce a single JAVASCRIPT. |
| Canonical order by category | Makes the verdict independent of the order in which the candidate wrote their skills. |
| Required vs optional categories | Models "must have" vs "nice to have" qualifications without extra code. |
