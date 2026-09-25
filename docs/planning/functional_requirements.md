# Functional Requirements

## Numbered requirements

### FR-01: Load a controlled project

- **Input:** A configured project directory within the approved workspace.
- **Output:** Project identity, allowed paths, discovered Python files, and configuration status.
- **Validation:** The path must resolve within the configured workspace, be a directory, and contain only supported project content.
- **Errors:** Show a user-readable blocked status; do not execute tests when validation fails.

### FR-02: Parse supported Python files

- **Input:** Python source files selected by the project configuration.
- **Output:** AST-derived module and test metadata.
- **Validation:** Use `ast.parse`; reject files that cannot be parsed and record the file-specific error.
- **Errors:** A parse failure must not be silently treated as an empty file.

### FR-03: Discover approved pytest tests

- **Input:** AST metadata and configured test allowlist.
- **Output:** Test identifiers that meet naming, path, and allowlist rules.
- **Validation:** Tests must reside in approved directories and use approved identifier formats.
- **Errors:** If no tests are eligible, report an explicit empty-selection state.

### FR-04: Accept a test selection

- **Input:** User selection from discovered tests or an approved predefined subset.
- **Output:** A normalized immutable test plan.
- **Validation:** Every selected item must match the current discovery result; duplicate and malformed identifiers are rejected.
- **Errors:** Do not pass unvalidated user text into a process command.

### FR-05: Execute approved tests

- **Input:** A validated test plan.
- **Output:** Process status, bounded stdout/stderr, exit status, and timing.
- **Validation:** Use a fixed pytest executable strategy, fixed safe arguments, fixed working directory, environment allowlist, timeout, and output limit.
- **Errors:** Handle timeout, process start failure, non-zero exit, collection error, and unexpected runner errors distinctly.

### FR-06: Produce structured evidence

- **Input:** Runner result.
- **Output:** JSON report containing schema version, project identifier, selected tests, start/end time, duration, counts, outcome, exit status, bounded output, and error category.
- **Validation:** Required fields and types must be present; sensitive values must not be included.
- **Errors:** Invalid report construction is a validation failure, not a successful run.

### FR-07: Classify outcomes deterministically

- **Input:** Exit status, pytest result signals, timeout state, and collection state.
- **Output:** One primary status: `passed`, `failed`, `skipped`, `collection_error`, `timeout`, or `blocked`.
- **Validation:** Classification rules are ordered and documented; ambiguous results retain an uncertainty note.
- **Errors:** Never label a result as passed when execution evidence is missing or incomplete.

### FR-08: Display a validation report

- **Input:** Valid JSON evidence and deterministic classification.
- **Output:** Streamlit views for summary, selected scope, evidence, limitations, and next investigation suggestions.
- **Validation:** Suggested causes are visually and textually labeled as suggestions.
- **Errors:** A report rendering error must identify the failed section without hiding the underlying result.

### FR-09: Preserve evidence boundaries

- **Input:** Observed runner data and optional explanation text.
- **Output:** Separate evidence and explanation sections.
- **Validation:** Explanations cannot alter status, counts, or raw evidence.
- **Errors:** Missing explanation is acceptable; missing evidence is not.

### FR-10: Reset and repeat safely

- **Input:** User request to clear the current run or start another approved run.
- **Output:** A new isolated run context.
- **Validation:** Previous output is not reused as current evidence.
- **Errors:** If reset fails, keep the prior report marked as historical and block a misleading new result.

## Cross-cutting input rules

- Accept only configured paths, identifiers, and enumerated options.
- Normalize paths and reject traversal outside the workspace.
- Treat all project files and test output as untrusted content.
- Do not accept command-line fragments, shell operators, or executable code through the UI.

## Cross-cutting output rules

- Reports must be deterministic for the same project state and test selection, apart from timestamps and environment metadata.
- Reports must state scope, limitations, and whether an outcome is complete or partial.
- User-visible errors must be actionable and must not expose secrets or unnecessary host details.

