from app.models.validation_models import ReportStatus, ValidationReport
from app.streamlit_app import (
    _CALCULATOR_PROJECT,
    _DEMO_PROJECTS_ROOT,
    _REPOSITORY_ROOT,
    _count_rows,
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
