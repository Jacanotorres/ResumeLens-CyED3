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
| S8 | Invalid candidate profile DSL | S8 | Invalid candidate profile DSL | Profile text with lexical or syntax errors (`tests/test_dsl_validator.py`) |

## Test cases

| Id | Stage | Scenario | Input | Expected output |
|----|-------|----------|-------|-----------------|
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
