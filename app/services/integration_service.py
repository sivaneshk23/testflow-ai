"""Coordinate the controlled inspection, pytest, evidence, and classification flow."""

from __future__ import annotations

from pathlib import Path

from app.models.validation_models import (
    ClassifiedFailureInfo,
    EvidenceStatus,
    IntegrationResult,
    IntegrationStatus,
    ObservedTestResult,
    ProjectInspectionResult,
    RunnerStatus,
    TestResultStatus,
    TestRunResult,
)
from app.services.evidence_normalizer import normalize_test_evidence
from app.services.project_inspector import inspect_project
from app.services.result_classifier import classify_test_result
from app.services.test_runner import run_pytest


def _unknown_classification(message: str) -> ClassifiedFailureInfo:
    return ClassifiedFailureInfo(
        status=TestResultStatus.UNKNOWN,
        observed_status=None,
        evidence_summary=message,
    )


def _classification_input(
    runner: TestRunResult,
    evidence_status: EvidenceStatus,
    stdout: str,
    stderr: str,
) -> ObservedTestResult:
    if evidence_status is EvidenceStatus.COLLECTION_ERROR:
        status = "collection_error"
    elif evidence_status is EvidenceStatus.SUCCESSFUL:
        status = "passed"
    elif evidence_status is EvidenceStatus.TEST_FAILURES:
        status = "failed"
    elif evidence_status is EvidenceStatus.TIMEOUT:
        status = "timeout"
    elif evidence_status is EvidenceStatus.STARTUP_ERROR:
        status = "startup_error"
    elif evidence_status is EvidenceStatus.EXECUTION_ERROR:
        status = "execution_error"
    else:
        status = "unknown"
    return ObservedTestResult(
        status=status,
        output=f"{stdout}\n{stderr}",
        exit_code=runner.exit_code,
        collection_error=evidence_status is EvidenceStatus.COLLECTION_ERROR,
    )


def run_controlled_validation(
    project_path: str | Path,
    allowed_root: str | Path,
    *,
    timeout_seconds: float = 30.0,
    max_output_bytes: int = 64 * 1024,
) -> IntegrationResult:
    """Run the complete controlled workflow for the trusted demo project.

    No caller-supplied pytest arguments or project code are accepted here. The
    runner remains responsible for its fixed command and startup-hook policy.
    """
    if not isinstance(project_path, (str, Path)) or not isinstance(
        allowed_root, (str, Path)
    ):
        return IntegrationResult(
            status=IntegrationStatus.INVALID_INPUT,
            error_message="Project path and allowed root must be path values.",
        )

    inspection = inspect_project(project_path, allowed_root)
    if inspection.status.value != "complete":
        return IntegrationResult(
            status=IntegrationStatus.BLOCKED,
            inspection=inspection,
            classification=_unknown_classification(
                "Validation was blocked before pytest execution."
            ),
            error_message="The project did not pass controlled inspection.",
        )

    runner = run_pytest(
        project_path,
        allowed_root,
        timeout_seconds=timeout_seconds,
        max_output_bytes=max_output_bytes,
    )
    evidence = normalize_test_evidence(
        runner,
        max_output_bytes=max_output_bytes,
    )
    classification = classify_test_result(
        _classification_input(
            runner,
            evidence.evidence_status,
            evidence.stdout,
            evidence.stderr,
        )
    )

    if runner.status is RunnerStatus.COMPLETED:
        status = IntegrationStatus.COMPLETED
    elif runner.status in {
        RunnerStatus.TIMEOUT,
        RunnerStatus.STARTUP_ERROR,
        RunnerStatus.EXECUTION_ERROR,
    }:
        status = IntegrationStatus.RUNNER_ERROR
    else:
        status = IntegrationStatus.BLOCKED
    return IntegrationResult(
        status=status,
        inspection=inspection,
        runner=runner,
        evidence=evidence,
        classification=classification,
        error_message=runner.error_message,
    )
