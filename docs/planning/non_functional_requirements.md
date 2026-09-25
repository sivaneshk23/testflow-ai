# Non-Functional Requirements

## Security

- Execute only the configured synthetic demo project and allowlisted pytest targets.
- Do not execute uploaded scripts automatically.
- Do not construct shell commands from user input.
- Apply path containment checks, timeout limits, output-size limits, and environment allowlists.
- Treat source, filenames, tracebacks, and test output as untrusted display content.
- Do not collect or store secrets, credentials, personal information, client data, or social-media data.
- Document the trust boundary and all execution limitations in the UI and project documentation.
- The MVP runner is limited to the trusted synthetic demo project. Projects containing
  `conftest.py`, `pytest_plugins`, `sitecustomize.py`, or `usercustomize.py` are rejected
  before pytest starts. The runner disables user-site imports when pytest is available
  in the interpreter site-packages; otherwise it preserves only the Windows variables
  needed for the supported interpreter to locate its installed pytest package. This is
  policy enforcement, not OS-level sandboxing.

## Reliability

- A failed test must produce a valid report whenever the runner itself completed.
- Runner failures, timeouts, parse errors, and blocked actions must be distinguishable.
- A partial or stale result must never be presented as a current successful result.
- Repeated runs must not share mutable result state.
- The application must fail closed when configuration or validation is missing.

## Maintainability

- Keep the execution engine, AST inspection, reporting, UI, and optional explanation logic separated.
- Use standard-library and existing fixed-stack components only.
- Version the JSON report schema.
- Keep deterministic classification rules small, documented, and unit-testable.
- Avoid hidden global state and duplicated validation logic.

## Usability

- Use plain language suitable for beginners.
- Show the selected scope before execution and the result status prominently afterward.
- Explain what was observed, what is suggested, and what remains unknown.
- Provide actionable next steps without claiming certainty.
- Make blocked actions explainable rather than silently disabled.

## Performance

- A normal demo run should return promptly on the supported hardware and project size.
- Enforce configurable upper bounds for file count, source size, output size, and test duration.
- AST inspection should avoid repeated parsing of unchanged files within a run.
- The UI must remain responsive while a bounded test run is active.

## Accessibility considerations

- Provide sufficient color contrast and do not use color as the only status signal.
- Use meaningful headings, labels, and focus order in Streamlit controls.
- Make status and error text available to assistive technologies.
- Avoid unexplained icons and provide text alternatives.
- Keep interactions keyboard-accessible where Streamlit permits.
