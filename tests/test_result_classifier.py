from app.models.validation_models import TestResultStatus
from app.services.result_classifier import classify_test_result


def test_classifies_passing_result() -> None:
    result = classify_test_result({"status": "passed", "exit_code": 0})

    assert result.status is TestResultStatus.PASSED
    assert result.root_cause_supported is False


def test_classifies_assertion_failure_from_error_type() -> None:
    result = classify_test_result(
        {"status": "failed", "error_type": "AssertionError"}
    )

    assert result.status is TestResultStatus.ASSERTION_FAILURE


def test_classifies_exception_from_observed_error_type() -> None:
    result = classify_test_result(
        {"status": "failed", "error_type": "ZeroDivisionError"}
    )

    assert result.status is TestResultStatus.EXCEPTION


def test_classifies_collection_error() -> None:
    result = classify_test_result(
        {"status": "failed", "collection_error": True}
    )

    assert result.status is TestResultStatus.COLLECTION_ERROR


def test_unknown_for_incomplete_failure() -> None:
    result = classify_test_result({"status": "failed"})

    assert result.status is TestResultStatus.UNKNOWN
    assert result.observed_status == "failed"


def test_unknown_for_malformed_input() -> None:
    result = classify_test_result({"status": 1})

    assert result.status is TestResultStatus.UNKNOWN
    assert result.observed_status is None


def test_unknown_for_none_input() -> None:
    result = classify_test_result(None)

    assert result.status is TestResultStatus.UNKNOWN
    assert result.evidence_summary == "No test-result evidence was supplied."


def test_assertion_text_in_output_is_direct_evidence() -> None:
    result = classify_test_result(
        {"status": "failed", "output": "AssertionError: expected 2, got 1"}
    )

    assert result.status is TestResultStatus.ASSERTION_FAILURE
