from app.models.validation_models import (
    ClassifiedFailureInfo,
    EvidenceStatus,
    IntegrationResult,
    IntegrationStatus,
    InspectionStatus,
    ProjectInspectionResult,
    ReportStatus,
    RunnerStatus,
    TestResultStatus,
    TestRunResult,
    NormalizedTestEvidence,
    ValidationReport,
)
from app.services.report_presenter import present_validation_report


def _evidence(status: EvidenceStatus, **kwargs: object) -> NormalizedTestEvidence:
    return NormalizedTestEvidence(
        evidence_status=status,
        runner_status=RunnerStatus.COMPLETED,
        project_path="calculator_project",
        **kwargs,
    )


def test_presents_success_and_observed_counts() -> None:
    result = IntegrationResult(
        status=IntegrationStatus.COMPLETED,
        evidence=_evidence(
            EvidenceStatus.SUCCESSFUL,
            exit_code=0,
            passed=9,
            skipped=1,
            xfailed=1,
            parser_warnings=("A parser note.",),
        ),
    )

    report = present_validation_report(result)

    assert report.status is ReportStatus.SUCCESSFUL
    assert report.passed == 9
    assert report.skipped == 1
    assert report.xfailed == 1
    assert report.warnings == ("A parser note.",)


def test_presents_test_failure_without_inventing_root_cause() -> None:
    classification = ClassifiedFailureInfo(
        status=TestResultStatus.ASSERTION_FAILURE,
        observed_status="failed",
        evidence_summary="Observed assertion evidence.",
    )
    report = present_validation_report(
        IntegrationResult(
            status=IntegrationStatus.COMPLETED,
            evidence=_evidence(
                EvidenceStatus.TEST_FAILURES,
                exit_code=1,
                failed=1,
                stdout="1 failed in 0.01s\n",
            ),
            classification=classification,
        )
    )

    assert report.status is ReportStatus.TEST_FAILURES
    assert report.failed == 1
    assert report.classification is classification
    assert classification.root_cause_supported is False


def test_presents_blocked_and_inspection_error_separately() -> None:
    blocked = present_validation_report(
        IntegrationResult(status=IntegrationStatus.BLOCKED)
    )
    inspection_error = present_validation_report(
        IntegrationResult(
            status=IntegrationStatus.INSPECTION_ERROR,
            inspection=ProjectInspectionResult(
                status=InspectionStatus.INSPECTION_ERROR,
                project_path="project",
                allowed_root="workspace",
            ),
        )
    )

    assert blocked.status is ReportStatus.BLOCKED
    assert inspection_error.status is ReportStatus.INSPECTION_ERROR


def test_presents_timeout_and_runner_errors() -> None:
    timeout = present_validation_report(
        IntegrationResult(
            status=IntegrationStatus.RUNNER_ERROR,
            evidence=NormalizedTestEvidence(
                evidence_status=EvidenceStatus.TIMEOUT,
                runner_status=RunnerStatus.TIMEOUT,
                project_path="calculator_project",
            ),
        )
    )
    startup = present_validation_report(
        IntegrationResult(
            status=IntegrationStatus.RUNNER_ERROR,
            runner=TestRunResult(
                status=RunnerStatus.STARTUP_ERROR,
                project_path="calculator_project",
                error_message="startup failed",
            ),
            evidence=NormalizedTestEvidence(
                evidence_status=EvidenceStatus.STARTUP_ERROR,
                runner_status=RunnerStatus.STARTUP_ERROR,
                project_path="calculator_project",
            ),
        )
    )

    assert timeout.status is ReportStatus.TIMEOUT
    assert startup.status is ReportStatus.RUNNER_ERROR
    assert startup.error_message == "startup failed"


def test_presents_malformed_unknown_and_raw_bounded_evidence() -> None:
    malformed = present_validation_report(
        IntegrationResult(
            status=IntegrationStatus.COMPLETED,
            evidence=_evidence(
                EvidenceStatus.MALFORMED,
                stdout="unexpected",
                output_truncated=True,
            ),
        )
    )
    invalid = present_validation_report(None)

    assert malformed.status is ReportStatus.MALFORMED
    assert malformed.stdout == "unexpected"
    assert malformed.output_truncated is True
    assert invalid.status is ReportStatus.MALFORMED
    assert isinstance(invalid, ValidationReport)


def test_preserves_unknown_evidence_and_does_not_invent_counts() -> None:
    report = present_validation_report(
        IntegrationResult(
            status=IntegrationStatus.COMPLETED,
            evidence=_evidence(
                EvidenceStatus.UNKNOWN,
                stderr="plugin output",
                parser_warnings=("No supported summary.",),
            ),
        )
    )

    assert report.status is ReportStatus.UNKNOWN
    assert report.passed is None
    assert report.failed is None
    assert report.stderr == "plugin output"
