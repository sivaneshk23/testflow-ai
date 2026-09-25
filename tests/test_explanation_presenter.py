import inspect
from copy import deepcopy

from app.models.validation_models import (
    EvidenceStatus,
    IntegrationStatus,
    InspectionStatus,
    ReportStatus,
    RunnerStatus,
    TestResultStatus,
    ValidationReport,
    ClassifiedFailureInfo,
)
from app.services import explanation_presenter
from app.services.explanation_presenter import present_advisory_guidance


def _report(status: ReportStatus) -> ValidationReport:
    integration_status = IntegrationStatus.COMPLETED
    inspection_status = InspectionStatus.COMPLETE
    evidence_status = EvidenceStatus.TEST_FAILURES
    runner_status = RunnerStatus.COMPLETED
    if status is ReportStatus.BLOCKED:
        integration_status = IntegrationStatus.BLOCKED
        evidence_status = None
        runner_status = None
    elif status is ReportStatus.INSPECTION_ERROR:
        integration_status = IntegrationStatus.INSPECTION_ERROR
        inspection_status = InspectionStatus.INSPECTION_ERROR
        evidence_status = None
        runner_status = None
    elif status is ReportStatus.COLLECTION_ERROR:
        evidence_status = EvidenceStatus.COLLECTION_ERROR
    elif status is ReportStatus.RUNNER_ERROR:
        integration_status = IntegrationStatus.RUNNER_ERROR
        evidence_status = EvidenceStatus.EXECUTION_ERROR
        runner_status = RunnerStatus.EXECUTION_ERROR
    elif status is ReportStatus.TIMEOUT:
        integration_status = IntegrationStatus.RUNNER_ERROR
        evidence_status = EvidenceStatus.TIMEOUT
        runner_status = RunnerStatus.TIMEOUT

    return ValidationReport(
        status=status,
        integration_status=integration_status,
        project_path="calculator_project",
        inspection_status=inspection_status,
        runner_status=runner_status,
        evidence_status=evidence_status,
        exit_code=1,
        passed=8,
        failed=1,
        skipped=1,
        xfailed=1,
        xpassed=0,
        errors=2,
        error_message="Observed error message.",
        warnings=("Observed parser warning.",),
        stdout="command-like text: && echo should remain evidence",
        stderr="<not executable>",
        output_truncated=True,
        classification=ClassifiedFailureInfo(
            status=TestResultStatus.ASSERTION_FAILURE,
            observed_status="failed",
            evidence_summary="Observed assertion evidence.",
        ),
    )


def test_guidance_is_deterministic_for_the_same_report() -> None:
    report = _report(ReportStatus.TEST_FAILURES)

    assert present_advisory_guidance(report) == present_advisory_guidance(report)


def test_each_actionable_status_has_conservative_advisory_guidance() -> None:
    actionable = (
        ReportStatus.TEST_FAILURES,
        ReportStatus.COLLECTION_ERROR,
        ReportStatus.BLOCKED,
        ReportStatus.INSPECTION_ERROR,
        ReportStatus.RUNNER_ERROR,
        ReportStatus.TIMEOUT,
    )

    for status in actionable:
        guidance = present_advisory_guidance(_report(status))
        assert len(guidance) == 1
        assert guidance[0].startswith("Advisory:")
        assert "root cause" not in guidance[0].lower()
        assert "definitely" not in guidance[0].lower()
        assert "this will fix" not in guidance[0].lower()


def test_successful_malformed_and_unknown_reports_have_no_guidance() -> None:
    for status in (
        ReportStatus.SUCCESSFUL,
        ReportStatus.MALFORMED,
        ReportStatus.UNKNOWN,
    ):
        assert present_advisory_guidance(_report(status)) == ()


def test_insufficient_or_malformed_inputs_have_no_guidance() -> None:
    assert present_advisory_guidance(object()) == ()
    for status in (
        ReportStatus.TEST_FAILURES,
        ReportStatus.COLLECTION_ERROR,
        ReportStatus.BLOCKED,
        ReportStatus.INSPECTION_ERROR,
        ReportStatus.RUNNER_ERROR,
        ReportStatus.TIMEOUT,
    ):
        assert present_advisory_guidance(ValidationReport(status=status)) == ()


def test_guidance_does_not_modify_the_immutable_report() -> None:
    report = _report(ReportStatus.TEST_FAILURES)
    before = deepcopy(report)

    present_advisory_guidance(report)

    assert report == before
    assert report.status is ReportStatus.TEST_FAILURES
    assert report.project_path == "calculator_project"
    assert report.integration_status is IntegrationStatus.COMPLETED
    assert report.inspection_status is InspectionStatus.COMPLETE
    assert report.runner_status is RunnerStatus.COMPLETED
    assert report.evidence_status is EvidenceStatus.TEST_FAILURES
    assert report.exit_code == 1
    assert report.passed == 8
    assert report.failed == 1
    assert report.skipped == 1
    assert report.xfailed == 1
    assert report.xpassed == 0
    assert report.errors == 2
    assert report.warnings == ("Observed parser warning.",)
    assert report.stdout == "command-like text: && echo should remain evidence"
    assert report.stderr == "<not executable>"
    assert report.output_truncated is True
    assert report.summary_recognized is False
    assert report.classification is not None
    assert report.error_message == "Observed error message."


def test_guidance_does_not_reparse_or_echo_command_like_evidence() -> None:
    guidance = present_advisory_guidance(_report(ReportStatus.TEST_FAILURES))

    assert "echo should remain evidence" not in " ".join(guidance)
    assert "<not executable>" not in " ".join(guidance)


def test_presenter_has_no_execution_or_network_dependencies() -> None:
    source = inspect.getsource(explanation_presenter)

    for forbidden in (
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "importlib",
        "eval(",
        "exec(",
        "os.system",
        "shell=True",
    ):
        assert forbidden not in source
