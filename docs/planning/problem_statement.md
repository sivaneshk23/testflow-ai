# Problem Statement

## User problem

Beginner developers and small development teams can run Python tests, but often struggle to interpret failures, distinguish evidence from guesses, and decide what to investigate next. Test output is usually optimized for experienced developers rather than guided validation.

## Target users

- Beginner Python developers learning test-driven development.
- Solo developers validating a small project before sharing it.
- Small teams that need a repeatable, understandable test-check workflow.
- Hackathon judges and reviewers who need a safe, deterministic demonstration.

## Current workflow

1. Open a Python project in an editor or terminal.
2. Decide which tests to run.
3. Run pytest manually.
4. Read terminal output and tracebacks.
5. Search for likely causes.
6. Re-run tests after making changes.
7. Record results informally or not at all.

## Limitations of the current workflow

- Test selection may be inconsistent or unsafe.
- Beginners may confuse a symptom, a suspected cause, and a confirmed cause.
- Raw tracebacks can be difficult to interpret.
- Results are not consistently structured for comparison or review.
- Manual notes can omit environment, test scope, or failure evidence.
- Running arbitrary project code creates security and reliability risks.

## Proposed improvement

TestFlow AI will provide a controlled Streamlit interface for inspecting an approved, self-created Python demo project, selecting from an explicit pytest allowlist, running approved tests, and displaying a structured validation report. Deterministic rules will classify basic outcomes, while any optional AI explanation will remain clearly labeled as a suggestion that must not replace observed evidence.

