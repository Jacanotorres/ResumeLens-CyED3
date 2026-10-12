# 4. Test cases and scenarios

## Scenarios

| Id | Scenario | Setup |
|----|----------|-------|
| S1 | Full Stack résumé from the assignment | `data/resumes/wednesday_addams.txt` |
| S2 | ML Engineer résumé from the assignment | `data/resumes/mary_jane_watson.txt` |
| S3 | DevOps Engineer résumé | _TODO_ |
| S4 | Data Engineer résumé | _TODO_ |
| S5 | Résumé matching more than one profile | _TODO_ |
| S6 | Résumé missing a required category | _TODO_ |
| S7 | Skills written in unusual order / casing | _TODO_ |
| S8 | Invalid candidate profile DSL | Profile text with lexical or syntax errors (`tests/test_dsl_validator.py`) |
| S9 | Résumé with unsupported or malformed contact and experience strings | Text with unsupported URL, invalid duration, or non-name first line |

## Test cases

| Id | Stage | Scenario | Input | Expected output |
|----|-------|----------|-------|-----------------|
| T1-01 | 1 | S1 | `Wednesday Addams`, `mj.watson@example.com`, `+57 300 123 4567` | Name, email, and phone are extracted |
| T1-02 | 1 | S1 | `https://github.com/mj`, `linkedin.com/in/mj` | Both supported profile links are extracted without trailing punctuation |
| T1-03 | 1 | S1 | `B.Sc. in Computer Science`; `3 years of experience developing apps.` | Education line and `Experience(3, "developing apps")` are extracted |
| T1-04 | 1 | S7 | `NodeJS`, `React.js`, `JavaScript`, `PostgreSQL`, `NoSQL` | Longer skill matches are preserved; nested `JS`, `Java`, or `SQL` substrings are not emitted separately |
| T1-05 | 1 | S9 | `curriculum vitae 2026`; `example.com/mj`; `three years of experience` | No name, supported link, or experience duration is extracted from these strings |
| T2-01 | 2 | S7 | Surface forms `JS`, `Javascript`, and `JavaScript` | Each form normalizes to `JAVASCRIPT` regardless of case |
| T2-02 | 2 | S7 | `React.js` and an unsupported skill such as `Rust` | `React.js` normalizes to `REACT`; the unsupported skill returns `None` |
| T2-03 | 2 | S7 | `JS`, `javascript`, and `REACT` passed to `normalize_all` | Duplicate canonical output is removed and first-occurrence order is preserved |
| T3-01 | 3 | S1 | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` | Full Stack Developer accepts the sequence |
| T3-02 | 3 | S2 | `PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` | Machine Learning Engineer accepts the sequence |
| T3-03 | 3 | S3 / S4 | One valid ordered sequence for each team-defined profile | DevOps Engineer and Data Engineer accept their sequences |
| T3-04 | 3 | S6 | A sequence missing a required category | The profile rejects the sequence |
| T3-05 | 3 | S7 | Tokens in the wrong category order or outside the profile alphabet | The profile rejects the sequence |
| T3-06 | 3 | S1 / S2 | A sequence omitting optional categories | The profile accepts if all required categories are present |
| T4-01 | 4 | S8 | Valid profile for Wednesday Addams with 5 skills | Accepted; the model has 5 tokens and FULL_STACK_DEVELOPER is ACCEPTED |
| T4-02 | 4 | S8 | `skills: javascript` (lowercase) | Rejected with `Expected TOKEN` and line and column |
| T4-03 | 4 | S8 | `FULL_STACK_DEVELOPER: MAYBE` | Rejected with `Expected 'ACCEPTED' or 'REJECTED'` |
| T4-04 | 4 | S8 | Unknown profile key `FRONTEND_DEVELOPER` | Rejected with a syntax error |
| T4-05 | 4 | S8 | `years: three` | Rejected with a syntax error |
| T4-06 | 4 | S8 | `candidate Wednesday` (name without quotes) | Rejected with a syntax error |
| T4-07 | 4 | S8 | Profile missing the closing brace | Rejected with a syntax error |
| T4-08 | 4 | S8 | Empty text | Rejected with `Expected 'candidate'` |
| T4-09 | 4 | S1 | ScreeningResult built by hand, converted with `to_dsl` | The text is valid DSL and keeps name, skills and verdicts |
| T4-10 | 4 | S1 | ScreeningResult with no recognized skills | `to_dsl` raises ValueError |
| T4-11 | 4 | S8 | Name containing `<Admin>` rendered to HTML | The HTML shows `&lt;Admin&gt;` (escaped) |
| T4-12 | 4 | S1 | CLI run with `--dsl` and `--html` | Both files are written and the exit code is 0 |
