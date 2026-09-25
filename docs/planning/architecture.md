# Architecture

## Components

1. **Streamlit presentation layer** — displays project state, test selection, progress, report sections, and limitations.
2. **Configuration and policy layer** — defines the single demo project, approved paths, test allowlist, limits, and report schema version.
3. **Project inspector** — performs containment checks and reads approved files.
4. **AST analyzer** — parses Python files with `ast` and returns test/module metadata without importing project code.
5. **Test-plan validator** — converts UI selections into a validated internal plan.
6. **Controlled pytest runner** — starts only the approved test command with fixed process policy.
7. **Evidence normalizer** — bounds output, records process facts, and writes JSON evidence.
8. **Deterministic classifier** — maps evidence to a documented outcome.
9. **Report presenter** — renders evidence, classification, limitations, and optional suggestions separately.
10. **Optional explanation adapter** — may produce clearly labeled suggestions; it cannot modify evidence or status.

## Responsibilities

Each component owns one validation boundary. The UI never builds commands, the AST analyzer never executes code, the runner never decides root cause, and the explanation adapter never changes observed results.

## Data flow

1. Load fixed configuration.
2. Validate the configured project path and policy.
3. Inspect approved files.
4. Parse eligible Python files with `ast`.
5. Discover allowlisted tests.
6. Accept and validate a user selection.
7. Display the final test plan for confirmation.
8. Execute the fixed pytest runner under limits.
9. Normalize process output into versioned JSON evidence.
10. Classify the outcome deterministically.
11. Render evidence and classification.
12. Optionally render suggestions in a separate section.

## Error-handling flow

Every stage returns either a typed success value or a typed failure category. Failures are displayed with a safe message, recorded in the report when a report can be produced, and stop downstream execution. Unknown exceptions are surfaced as runner/application errors rather than converted to a pass or empty result.

## Security boundaries

- **Workspace boundary:** project paths must remain under the configured workspace.
- **File boundary:** only approved extensions, directories, and file sizes are inspected.
- **Parsing boundary:** AST inspection does not import or execute the project.
- **Process boundary:** the runner receives fixed executable and arguments, fixed working directory, restricted environment, timeout, and output cap.
- **Display boundary:** output is escaped/rendered safely and treated as untrusted text.
- **Explanation boundary:** optional AI or heuristic text is advisory and cannot affect evidence.

## Why each component exists

The separation prevents a beginner-friendly UI from becoming an arbitrary code execution tool, makes results testable in isolation, and preserves the distinction between observed test facts and interpretation. A single controlled project keeps the MVP feasible for a solo developer and safe for a hackathon demonstration.

The evidence normalizer recognizes only pytest summary lines composed of comma-separated
counts (`passed`, `failed`, `skipped`, `xfailed`, `xpassed`, and `error/errors`) followed
by `in <duration>s`. It uses the last recognized summary when multiple lines are present.
Other pytest versions, plugins, warnings, and malformed or truncated output may remain
partially unknown; counts are left unset rather than inferred from keywords.
