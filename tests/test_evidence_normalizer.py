from app.models.validation_models import (
    EvidenceStatus,
    NormalizedTestEvidence,
    RunnerStatus,
    TestRunResult,
)
from app.services.evidence_normalizer import normalize_test_evidence


def _result(stdout: str, *, exit_code: int = 0, status: RunnerStatus = RunnerStatus.COMPLETED) -> TestRunResult:
    return TestRunResult(status=status, project_path="calculator_project", exit_code=exit_code, stdout=stdout)


def test_normalizes_passing_summary() -> None:
    evidence = normalize_test_evidence(_result("9 passed in 0.18s\n"))

    assert evidence.evidence_status is EvidenceStatus.SUCCESSFUL
    assert evidence.passed == 9
    assert evidence.failed is None
    assert evidence.summary_recognized is True


def test_normalizes_failed_summary() -> None:
    evidence = normalize_test_evidence(_result("1 failed, 8 passed in 0.20s\n", exit_code=1))

    assert evidence.evidence_status is EvidenceStatus.TEST_FAILURES
    assert evidence.failed == 1
    assert evidence.passed == 8


def test_normalizes_skipped_expected_and_unexpected_results() -> None:
    evidence = normalize_test_evidence(
        _result("2 skipped, 1 xfailed, 1 xpassed in 0.04s\n")
    )

    assert evidence.skipped == 2
    assert evidence.xfailed == 1
    assert evidence.xpassed == 1
    assert evidence.evidence_status is EvidenceStatus.SUCCESSFUL


def test_normalizes_collection_error() -> None:
    evidence = normalize_test_evidence(
        _result("ERROR collecting test_demo.py\n1 error in 0.03s\n", exit_code=2)
    )

    assert evidence.evidence_status is EvidenceStatus.COLLECTION_ERROR
    assert evidence.errors == 1


def test_preserves_runner_failure_statuses() -> None:
    for runner_status, expected in (
        (RunnerStatus.TIMEOUT, EvidenceStatus.TIMEOUT),
        (RunnerStatus.STARTUP_ERROR, EvidenceStatus.STARTUP_ERROR),
        (RunnerStatus.EXECUTION_ERROR, EvidenceStatus.EXECUTION_ERROR),
    ):
        evidence = normalize_test_evidence(_result("", status=runner_status, exit_code=None))
        assert evidence.evidence_status is expected


def test_empty_and_malformed_output_do_not_invent_counts() -> None:
    for output in ("", "warning: 99 passed is mentioned here", "unexpected pytest text"):
        evidence = normalize_test_evidence(_result(output, exit_code=1))
        assert evidence.passed is None
        assert evidence.failed is None
        assert evidence.summary_recognized is False
        assert evidence.evidence_status is EvidenceStatus.MALFORMED


def test_multiple_summaries_use_last_supported_summary() -> None:
    evidence = normalize_test_evidence(
        _result("1 passed in 0.01s\n2 failed, 3 passed in 0.02s\n", exit_code=1)
    )

    assert evidence.failed == 2
    assert evidence.passed == 3
    assert evidence.parser_warnings


def test_truncated_output_is_bounded_and_reported() -> None:
    evidence = normalize_test_evidence(_result("x" * 1000), max_output_bytes=32)

    assert len(evidence.stdout.encode("utf-8")) <= 32
    assert evidence.output_truncated is True


def test_preserves_raw_streams_and_runner_facts() -> None:
    result = TestRunResult(
        status=RunnerStatus.COMPLETED,
        project_path="calculator_project",
        exit_code=0,
        stdout="9 passed in 0.18s\n",
        stderr="warning text\n",
        output_truncated=True,
    )

    evidence = normalize_test_evidence(result)

    assert evidence.runner_status is RunnerStatus.COMPLETED
    assert evidence.exit_code == 0
    assert evidence.stdout == result.stdout
    assert evidence.stderr == result.stderr
    assert evidence.output_truncated is True


def test_malformed_input_returns_typed_malformed_evidence() -> None:
    evidence = normalize_test_evidence({"status": "completed"})

    assert isinstance(evidence, NormalizedTestEvidence)
    assert evidence.evidence_status is EvidenceStatus.MALFORMED
    assert evidence.runner_status is None
