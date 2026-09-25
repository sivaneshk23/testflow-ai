"""Build a deterministic user-facing report from one integration result."""

from __future__ import annotations

from app.models.validation_models import (
    EvidenceStatus,
    IntegrationResult,
    IntegrationStatus,
    ReportStatus,
    ValidationReport,
)


def _malformed_report(message: str) -> ValidationReport:
    return ValidationReport(
        status=ReportStatus.MALFORMED,
        warnings=(message,),
    )


def _report_status(result: IntegrationResult) -> ReportStatus:
    if result.status is IntegrationStatus.INVALID_INPUT:
        return ReportStatus.MALFORMED
    if result.status is IntegrationStatus.INSPECTION_ERROR:
        return ReportStatus.INSPECTION_ERROR
    if result.status is IntegrationStatus.BLOCKED:
        return ReportStatus.BLOCKED

    evidence = result.evidence
    if evidence is None:
        return ReportStatus.MALFORMED
    if evidence.evidence_status is EvidenceStatus.TIMEOUT:
        return ReportStatus.TIMEOUT
    if evidence.evidence_status in {
        EvidenceStatus.STARTUP_ERROR,
        EvidenceStatus.EXECUTION_ERROR,
    }:
        return ReportStatus.RUNNER_ERROR
    if evidence.evidence_status is EvidenceStatus.SUCCESSFUL:
        return ReportStatus.SUCCESSFUL
    if evidence.evidence_status is EvidenceStatus.TEST_FAILURES:
        return ReportStatus.TEST_FAILURES
    if evidence.evidence_status is EvidenceStatus.COLLECTION_ERROR:
        return ReportStatus.COLLECTION_ERROR
    if evidence.evidence_status is EvidenceStatus.MALFORMED:
        return ReportStatus.MALFORMED
    return ReportStatus.UNKNOWN


def present_validation_report(result: IntegrationResult | object) -> ValidationReport:
    """Project one integration result into a bounded, observed report model.

    The function performs no execution, parsing, classification, or network
    access. It preserves counts only when the normalizer already observed them.
    """
    if not isinstance(result, IntegrationResult):
        return _malformed_report("Integration evidence was missing or malformed.")

    evidence = result.evidence
    inspection = result.inspection
    runner = result.runner
    if result.status is IntegrationStatus.INVALID_INPUT:
        return ValidationReport(
            status=ReportStatus.MALFORMED,
            integration_status=result.status,
            error_message=result.error_message,
            warnings=("The validation request was malformed.",),
        )

    if evidence is None and result.status is IntegrationStatus.COMPLETED:
        return _malformed_report("Completed validation did not include evidence.")

    warnings = evidence.parser_warnings if evidence is not None else ()
    return ValidationReport(
        status=_report_status(result),
        integration_status=result.status,
        project_path=(
            evidence.project_path
            if evidence is not None
            else runner.project_path
            if runner is not None
            else inspection.project_path
            if inspection is not None
            else None
        ),
        inspection_status=inspection.status if inspection is not None else None,
        runner_status=runner.status if runner is not None else None,
        evidence_status=evidence.evidence_status if evidence is not None else None,
        exit_code=evidence.exit_code if evidence is not None else runner.exit_code if runner is not None else None,
        passed=evidence.passed if evidence is not None else None,
        failed=evidence.failed if evidence is not None else None,
        skipped=evidence.skipped if evidence is not None else None,
        xfailed=evidence.xfailed if evidence is not None else None,
        xpassed=evidence.xpassed if evidence is not None else None,
        errors=evidence.errors if evidence is not None else None,
        summary_recognized=evidence.summary_recognized if evidence is not None else False,
        stdout=evidence.stdout if evidence is not None else runner.stdout if runner is not None else "",
        stderr=evidence.stderr if evidence is not None else runner.stderr if runner is not None else "",
        output_truncated=(
            evidence.output_truncated
            if evidence is not None
            else runner.output_truncated
            if runner is not None
            else False
        ),
        warnings=warnings,
        classification=result.classification,
        error_message=result.error_message
        or (runner.error_message if runner is not None else None),
    )
