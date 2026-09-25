# Testing Strategy

## Unit testing strategy

Test pure functions for:

- Path containment and policy validation.
- AST test discovery, including malformed and unusual Python syntax.
- Test identifier normalization and allowlist enforcement.
- Command-plan construction from validated data.
- Output truncation and sensitive-value filtering.
- JSON schema construction and validation.
- Deterministic outcome classification.

## Integration testing strategy

Use the controlled synthetic project to verify the complete flow from inspection through report rendering inputs. Cover passing tests, failing tests, skipped tests, collection errors, timeout behavior, empty selections, and runner-start failures.

## Negative tests

- Path traversal and symlink escape attempts.
- Test identifiers containing shell metacharacters.
- Unapproved directories and file extensions.
- Malformed Python files.
- Missing pytest executable or invalid configuration.
- Excessive output and long-running tests.
- Invalid or incomplete runner results.
- Attempts to submit arbitrary command text.
- Stale-result reuse after reset.

## Edge cases

- No eligible tests.
- Duplicate test names.
- Unicode and long filenames.
- Empty files and files with only comments.
- Collection-time import errors.
- A mixture of passed, failed, and skipped tests.
- Process termination without a normal exit code.
- Output containing markup, escape sequences, or secret-like text.
- User refresh or repeated clicks during a run.

## Security-related tests

Verify that no user-controlled value reaches a shell interpreter, that all paths remain within the workspace, that timeouts terminate the controlled process, that output limits are enforced, and that blocked inputs never execute. Verify that AST analysis does not import project modules.

## Manual UI verification

For each release candidate, manually verify the happy path and at least one blocked path in Streamlit. Confirm that status is understandable without color, evidence and suggestions are visually separate, controls show the selected scope, errors are actionable, and no sensitive or host-specific information appears in the report.

## Evidence expectations

Test results must come from executed tests or explicit blocked/error states. Do not fabricate pass counts, screenshots, Bob contributions, or performance claims.

