"""Streamlit entry point for the controlled TestFlow AI demonstration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from app.models.validation_models import ReportStatus, ValidationReport
from app.services.explanation_presenter import present_advisory_guidance
from app.services.integration_service import run_controlled_validation
from app.services.report_presenter import present_validation_report

_DEMO_PROJECTS_ROOT = _REPOSITORY_ROOT / "demo_projects"
_CALCULATOR_PROJECT = _DEMO_PROJECTS_ROOT / "calculator_project"
_PROJECT_LABEL = "Controlled calculator demo"

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_DEMO_PROJECTS_ROOT = _REPOSITORY_ROOT / "demo_projects"
_CALCULATOR_PROJECT = _REPOSITORY_ROOT / "demo_projects" / "calculator_project"
_PROJECT_LABEL = "Controlled calculator demo"


def _status_message(status: ReportStatus) -> tuple[str, str]:
    """Return stable display text and a Streamlit message level."""
    messages = {
        ReportStatus.SUCCESSFUL: ("Validation successful", "success"),
        ReportStatus.TEST_FAILURES: ("Test failures observed", "error"),
        ReportStatus.COLLECTION_ERROR: ("Test collection error", "error"),
        ReportStatus.BLOCKED: ("Validation blocked", "warning"),
        ReportStatus.INSPECTION_ERROR: ("Project inspection error", "error"),
        ReportStatus.RUNNER_ERROR: ("Test runner error", "error"),
        ReportStatus.TIMEOUT: ("Validation timed out", "error"),
        ReportStatus.MALFORMED: ("Malformed validation report", "error"),
        ReportStatus.UNKNOWN: ("Validation outcome unknown", "warning"),
    }
    return messages[status]


def _count_rows(report: ValidationReport) -> list[tuple[str, int]]:
    """Return only counts directly observed by the evidence normalizer."""
    counts = (
        ("Passed", report.passed),
        ("Failed", report.failed),
        ("Skipped", report.skipped),
        ("Expected failures", report.xfailed),
        ("Unexpected passes", report.xpassed),
        ("Errors", report.errors),
    )
    return [(label, value) for label, value in counts if value is not None]


def _display_report(st: Any, report: ValidationReport) -> None:
    title, level = _status_message(report.status)
    getattr(st, level)(title)
    st.write(f"Report status: `{report.status.value}`")
    st.write(
        "Integration status: "
        f"`{report.integration_status.value if report.integration_status else 'unknown'}`"
    )

    with st.expander("Execution details", expanded=True):
        details = {
            "Inspection status": (
                report.inspection_status.value
                if report.inspection_status is not None
                else "unknown"
            ),
            "Runner status": (
                report.runner_status.value
                if report.runner_status is not None
                else "unknown"
            ),
            "Evidence status": (
                report.evidence_status.value
                if report.evidence_status is not None
                else "unknown"
            ),
            "Exit code": report.exit_code if report.exit_code is not None else "not available",
        }
        st.table([{"Field": key, "Observed value": value} for key, value in details.items()])

    counts = _count_rows(report)
    if counts:
        st.subheader("Observed test counts")
        st.table([{"Outcome": label, "Count": value} for label, value in counts])
    else:
        st.info("No test counts were established by the controlled evidence parser.")

    if report.classification is not None:
        st.subheader("Deterministic classification")
        st.write(f"Classification: `{report.classification.status.value}`")
        st.write(report.classification.evidence_summary)
        if not report.classification.root_cause_supported:
            st.caption("No root cause was established from the observed evidence.")

    advisory_guidance = present_advisory_guidance(report)
    if advisory_guidance:
        st.subheader("Advisory next steps")
        st.caption("Advisory guidance only; not a confirmed root cause.")
        for guidance in advisory_guidance:
            st.text(guidance)

    if report.warnings:
        st.subheader("Parser warnings")
        for warning in report.warnings:
            st.warning(warning)

    if report.error_message is not None:
        st.subheader("Error information")
        st.error(report.error_message)

    if report.stdout or report.stderr:
        st.subheader("Bounded test output")
        if report.stdout:
            st.caption("Standard output")
            st.code(report.stdout)
        if report.stderr:
            st.caption("Standard error")
            st.code(report.stderr)
        if report.output_truncated:
            st.caption("Output was truncated by the controlled execution limits.")


def main() -> None:
    """Render the controlled validation workflow."""
    import streamlit as st

    st.set_page_config(page_title="TestFlow AI", page_icon="✅", layout="centered")
    st.title("TestFlow AI")
    st.write(
        "Run the approved synthetic calculator project's pytest suite and inspect "
        "bounded, evidence-first validation results."
    )

    st.subheader("Approved project")
    project_label = st.selectbox("Project", (_PROJECT_LABEL,))
    st.caption(
        f"{project_label} is the only execution target in this MVP. "
        "Uploaded or arbitrary projects are not supported."
    )
    st.text_input("Allowed root", value="Project workspace", disabled=True)

    run_requested = st.button("Run controlled validation", type="primary")
    if st.button("Clear previous report"):
        st.session_state.pop("validation_report", None)
        st.rerun()

    if run_requested:
        integration_result = run_controlled_validation(
            _CALCULATOR_PROJECT,
            _DEMO_PROJECTS_ROOT,
        )
        st.session_state["validation_report"] = present_validation_report(
            integration_result
        )

    report = st.session_state.get("validation_report")
    if report is None:
        st.info("No validation has been run yet.")
        return

    st.divider()
    st.header("Validation report")
    _display_report(st, report)


if __name__ == "__main__":
    main()
