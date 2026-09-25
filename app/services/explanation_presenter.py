"""Present deterministic advisory guidance without changing validation evidence."""

from __future__ import annotations

from app.models.validation_models import (
    EvidenceStatus,
    InspectionStatus,
    IntegrationStatus,
    ReportStatus,
    RunnerStatus,
    ValidationReport,
)


_ADVISORY_MESSAGES: dict[ReportStatus, str] = {
    ReportStatus.TEST_FAILURES: (
        "Advisory: review the bounded output for the observed test failures "
        "and compare it with the expected behavior."
    ),
    ReportStatus.COLLECTION_ERROR: (
        "Advisory: review the bounded collection-error output and the permitted "
        "project files involved in test discovery."
    ),
    ReportStatus.BLOCKED: (
        "Advisory: review the controlled inspection and policy result; pytest "
        "was not executed for this validation."
    ),
    ReportStatus.INSPECTION_ERROR: (
        "Advisory: review the inspection error and permitted-path findings; "
        "validation stopped before pytest execution."
    ),
    ReportStatus.RUNNER_ERROR: (
        "Advisory: review the controlled runner status, available exit code, "
        "and safe error information."
    ),
    ReportStatus.TIMEOUT: (
        "Advisory: review the timeout status and bounded output; the observed "
        "run exceeded its configured limit."
    ),
}


def _has_sufficient_evidence(report: ValidationReport) -> bool:
    """Require status-consistent typed evidence before presenting guidance."""
    if report.status is ReportStatus.TEST_FAILURES:
        return (
            report.integration_status is IntegrationStatus.COMPLETED
            and report.evidence_status is EvidenceStatus.TEST_FAILURES
        )
    if report.status is ReportStatus.COLLECTION_ERROR:
        return (
            report.integration_status is IntegrationStatus.COMPLETED
            and report.evidence_status is EvidenceStatus.COLLECTION_ERROR
        )
    if report.status is ReportStatus.BLOCKED:
        return report.integration_status is IntegrationStatus.BLOCKED
    if report.status is ReportStatus.INSPECTION_ERROR:
        return (
            report.integration_status is IntegrationStatus.INSPECTION_ERROR
            and report.inspection_status is InspectionStatus.INSPECTION_ERROR
        )
    if report.status is ReportStatus.RUNNER_ERROR:
        return (
            report.integration_status is IntegrationStatus.RUNNER_ERROR
            and (
                report.runner_status
                in {
                    RunnerStatus.STARTUP_ERROR,
                    RunnerStatus.EXECUTION_ERROR,
                }
                or report.evidence_status
                in {
                    EvidenceStatus.STARTUP_ERROR,
                    EvidenceStatus.EXECUTION_ERROR,
                }
            )
        )
    if report.status is ReportStatus.TIMEOUT:
        return (
            report.integration_status is IntegrationStatus.RUNNER_ERROR
            and report.evidence_status is EvidenceStatus.TIMEOUT
            and report.runner_status is RunnerStatus.TIMEOUT
        )
    return False


def present_advisory_guidance(report: ValidationReport) -> tuple[str, ...]:
    """Return fixed advisory guidance for actionable report statuses only."""
    if not isinstance(report, ValidationReport):
        return ()
    message = _ADVISORY_MESSAGES.get(report.status)
    if message is None or not _has_sufficient_evidence(report):
        return ()
    return (message,)
