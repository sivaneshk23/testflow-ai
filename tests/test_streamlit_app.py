from unittest.mock import MagicMock, patch

from app.models.validation_models import (
    EvidenceStatus,
    IntegrationStatus,
    ReportStatus,
    ValidationReport,
)
from app.streamlit_app import (
    _CALCULATOR_PROJECT,
    _DEMO_PROJECTS_ROOT,
    _REPOSITORY_ROOT,
    _count_rows,
    _display_report,
    _status_message,
)


def test_ui_execution_scope_uses_the_demo_projects_root() -> None:
    assert _CALCULATOR_PROJECT.is_relative_to(_DEMO_PROJECTS_ROOT)
    assert _DEMO_PROJECTS_ROOT == _REPOSITORY_ROOT / "demo_projects"


def test_status_message_is_explicit_for_each_report_status() -> None:
    for status in ReportStatus:
        title, level = _status_message(status)
        assert title
        assert level in {"success", "error", "warning"}


def test_count_rows_preserves_observed_counts_and_omits_unknowns() -> None:
    report = ValidationReport(
        status=ReportStatus.SUCCESSFUL,
        passed=9,
        xpassed=1,
        failed=None,
    )

    assert _count_rows(report) == [
        ("Passed", 9),
        ("Unexpected passes", 1),
    ]


def test_successful_report_does_not_render_empty_advisory_section() -> None:
    st = MagicMock()
    st.expander.return_value.__enter__.return_value = st
    report = ValidationReport(
        status=ReportStatus.SUCCESSFUL,
        integration_status=IntegrationStatus.COMPLETED,
        evidence_status=EvidenceStatus.SUCCESSFUL,
    )

    with patch("app.streamlit_app.present_advisory_guidance", return_value=()):
        _display_report(st, report)

    subheaders = [call.args[0] for call in st.subheader.call_args_list]
    assert "Advisory next steps" not in subheaders
    st.write.assert_any_call("Report status: `successful`")


def test_actionable_advisory_is_rendered_separately_from_evidence() -> None:
    st = MagicMock()
    st.expander.return_value.__enter__.return_value = st
    report = ValidationReport(
        status=ReportStatus.TEST_FAILURES,
        integration_status=IntegrationStatus.COMPLETED,
        evidence_status=EvidenceStatus.TEST_FAILURES,
        stdout="observed test output",
    )
    guidance = ("Advisory: review the observed failure.",)

    with patch("app.streamlit_app.present_advisory_guidance", return_value=guidance):
        _display_report(st, report)

    subheaders = [call.args[0] for call in st.subheader.call_args_list]
    assert "Advisory next steps" in subheaders
    st.caption.assert_any_call("Advisory guidance only; not a confirmed root cause.")
    st.text.assert_any_call(guidance[0])
    st.code.assert_any_call("observed test output")
