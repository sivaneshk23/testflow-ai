# Implementation Sequence

## Ordered implementation tasks

1. **Create the synthetic controlled demo project and pytest cases.**
   - Depends on: approved scope and data policy.
   - Verification gate: all demo tests and intentional failure cases are understood and reproducible.

2. **Create configuration and policy validation.**
   - Depends on: task 1.
   - Verification gate: valid configuration is accepted; traversal, missing paths, and disallowed settings are blocked.

3. **Implement read-only project inspection and AST discovery.**
   - Depends on: task 2.
   - Verification gate: discovery tests cover valid, malformed, empty, and adversarial files without importing project code.

4. **Implement test-plan validation.**
   - Depends on: task 3.
   - Verification gate: only discovered allowlisted tests can enter a plan; invalid identifiers never reach execution.

5. **Implement the controlled pytest runner.**
   - Depends on: task 4.
   - Verification gate: pass, fail, skip, collection error, startup failure, output cap, and timeout cases are captured distinctly.

6. **Implement versioned JSON evidence and deterministic classification.**
   - Depends on: task 5.
   - Verification gate: schema and classification unit tests pass, including incomplete and ambiguous results.

7. **Implement the Streamlit workflow and report.**
   - Depends on: task 6.
   - Verification gate: manual happy-path and blocked-path UI verification confirms scope, evidence, status, limitations, and advisory separation.

8. **Add optional explanation presentation without execution authority.**
   - Depends on: task 7.
   - Verification gate: explanation text cannot alter evidence, status, counts, or command selection.

9. **Complete security, compliance, and regression review.**
   - Depends on: tasks 1-8.
   - Verification gate: all required tests pass, data review is clean, Bob evidence exists, and checklist items are supported by actual artifacts.

## Stop conditions when a task fails

- Stop downstream implementation when a verification gate fails.
- Stop immediately on any suspected unrestricted execution path, secret exposure, or path escape.
- Do not mark a task complete based on a partial run or an invented result.
- Record the failure, preserve evidence, fix or narrow the task, and rerun the gate.
- Escalate unresolved design decisions before coding beyond the affected boundary.

