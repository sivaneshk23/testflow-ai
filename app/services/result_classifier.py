"""Deterministic, conservative classification of observed test evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

from app.models.validation_models import (
    ClassifiedFailureInfo,
    ObservedTestResult,
    TestResultStatus,
)


def _unknown(observed_status: Optional[str], summary: str) -> ClassifiedFailureInfo:
    return ClassifiedFailureInfo(
        status=TestResultStatus.UNKNOWN,
        observed_status=observed_status,
        evidence_summary=summary,
    )


def _as_observed_result(
    result: ObservedTestResult | Mapping[str, Any],
) -> Optional[ObservedTestResult]:
    if isinstance(result, ObservedTestResult):
        return result
    if not isinstance(result, Mapping):
        return None
    status = result.get("status")
    if not isinstance(status, str) or not status.strip():
        return None
    output = result.get("output")
    error_type = result.get("error_type")
    exit_code = result.get("exit_code")
    collection_error = result.get("collection_error", False)
    if output is not None and not isinstance(output, str):
        return None
    if error_type is not None and not isinstance(error_type, str):
        return None
    if exit_code is not None and not isinstance(exit_code, int):
        return None
    if not isinstance(collection_error, bool):
        return None
    return ObservedTestResult(
        status=status,
        output=output,
        error_type=error_type,
        exit_code=exit_code,
        collection_error=collection_error,
    )


def classify_test_result(
    result: ObservedTestResult | Mapping[str, Any] | None,
) -> ClassifiedFailureInfo:
    """Classify evidence without inferring an unsupported root cause."""
    if result is None:
        return _unknown(None, "No test-result evidence was supplied.")
    observed = _as_observed_result(result)
    if observed is None:
        return _unknown(None, "Test-result evidence was missing or malformed.")

    normalized_status = observed.status.strip().lower()
    error_type = (observed.error_type or "").strip().lower()
    output = (observed.output or "").lower()

    if observed.collection_error or normalized_status == "collection_error":
        return ClassifiedFailureInfo(
            status=TestResultStatus.COLLECTION_ERROR,
            observed_status=observed.status,
            evidence_summary="The observed result reports a test collection error.",
        )
    if normalized_status in {"passed", "pass", "success"}:
        return ClassifiedFailureInfo(
            status=TestResultStatus.PASSED,
            observed_status=observed.status,
            evidence_summary="The observed result reports a passing test run.",
        )
    if normalized_status in {"failed", "failure", "assertion_failure"}:
        if error_type in {"assertionerror", "assertion_failure"} or "assertionerror" in output:
            return ClassifiedFailureInfo(
                status=TestResultStatus.ASSERTION_FAILURE,
                observed_status=observed.status,
                evidence_summary="Observed evidence identifies an assertion failure.",
            )
        if error_type and error_type not in {"failed", "failure"}:
            return ClassifiedFailureInfo(
                status=TestResultStatus.EXCEPTION,
                observed_status=observed.status,
                evidence_summary=f"Observed evidence identifies an exception type: {observed.error_type}.",
            )
        return _unknown(
            observed.status,
            "The result reports failure but does not identify its failure evidence.",
        )
    if normalized_status in {"exception", "error"}:
        return ClassifiedFailureInfo(
            status=TestResultStatus.EXCEPTION,
            observed_status=observed.status,
            evidence_summary="The observed result reports an exception or error.",
        )
    return _unknown(
        observed.status,
        "The observed status is not recognized by the conservative classifier.",
    )

