# Hackathon Compliance Checklist

## IBM Bob IDE usage

- [ ] Bob was used for planning and meaningful implementation work.
- [ ] Bob session evidence exists for major tasks.
- [ ] Bob review and debugging evidence is attributable to actual completed actions.
- [ ] No Bob contribution is claimed without supporting evidence.

## Data compliance

- [ ] The demo project and fixtures are self-created synthetic data.
- [ ] No confidential, client, personal, social-media, or secret data is present.
- [ ] Files, logs, screenshots, and reports were reviewed before sharing.
- [ ] Any third-party dependency or asset has permitted use.

## Project documentation

- [ ] All eleven planning documents are present and internally consistent.
- [ ] Execution limitations and evidence boundaries are documented.
- [ ] Assumptions and unresolved decisions are identified before coding.

## Session screenshots

- [ ] Screenshot of Bob planning/review activity.
- [ ] Screenshot of controlled test selection and execution.
- [ ] Screenshot of representative pass and failure reports.
- [ ] Screenshot of a blocked unsafe action or documented security boundary.
- [ ] Screenshots contain no secrets or personal information.

## Testing evidence

- [ ] Unit tests cover policy, AST discovery, planning, evidence, and classification.
- [ ] Integration tests cover the controlled end-to-end flow.
- [ ] Negative and security tests cover traversal, injection-like identifiers, timeouts, output limits, and uploads.
- [ ] Manual UI verification is recorded.
- [ ] Results are actual captured evidence, not estimates.

## Demonstration readiness

- [ ] Demo starts from a known clean state.
- [ ] The controlled project is deterministic.
- [ ] A passing run and an intentional failure run are available.
- [ ] The report distinguishes evidence, classification, suggestions, and limitations.
- [ ] Unsafe execution is clearly blocked and explained.

## Submission materials

- [ ] Project README and setup instructions are current.
- [ ] Planning documents are included.
- [ ] Test commands and actual results are recorded.
- [ ] Bob session evidence is retained in the approved submission location.
- [ ] Screenshots and demo script use only permitted synthetic content.
- [ ] Final review confirms no unverified claims.

## Assumptions and unresolved decisions

**Assumptions:** the MVP runs locally on Python 3.14.6, the version detected for the current environment; pytest is available through the project environment; one controlled calculator project is sufficient for the demonstration; optional AI assistance is not required for core validation.

**Unresolved before coding:** pytest process isolation mechanism on the target OS; report retention policy; whether optional explanation assistance will be included in the hackathon build; required screenshot and session-evidence storage location. The demo layout is resolved as `demo_projects/calculator_project/` with `calculator.py`, `README.md`, and `tests/test_calculator.py`.
