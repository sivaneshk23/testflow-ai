"""Normalize bounded pytest output without executing or interpreting project code."""

from __future__ import annotations

import re
from typing import Optional

from app.models.validation_models import (
    EvidenceStatus,
    NormalizedTestEvidence,
    RunnerStatus,
    TestRunResult,
)

_DEFAULT_MAX_OUTPUT_BYTES = 64 * 1024
_SUMMARY_RE = re.compile(
    r"^(?P<items>\d+\s+(?:passed|failed|skipped|xfailed|xpassed|errors?)"
    r"(?:,\s*\d+\s+(?:passed|failed|skipped|xfailed|xpassed|errors?))*"
    r")\s+in\s+\d+(?:\.\d+)?s$"
)
_ITEM_RE = re.compile(
    r"(?P<count>\d+)\s+"
    r"(?P<label>passed|failed|skipped|xfailed|xpassed|errors?)"
)
_COLLECTION_ERROR_RE = re.compile(r"^\s*ERROR collecting\b", re.MULTILINE)


def _bounded_text(value: str, max_output_bytes: int) -> tuple[str, bool]:
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= max_output_bytes:
        return value, False
    return encoded[:max_output_bytes].decode("utf-8", errors="ignore"), True


def _parse_summary(output: str) -> tuple[dict[str, int], bool, tuple[str, ...]]:
    recognized: list[tuple[int, str]] = []
    warnings: list[str] = []
    for line in output.splitlines():
        candidate = line.strip()
        match = _SUMMARY_RE.fullmatch(candidate)
        if match is None:
            continue
        items = [
            (int(item.group("count")), item.group("label"))
            for item in _ITEM_RE.finditer(match.group("items"))
        ]
        if len(items) < 1:
            continue
        recognized.append((len(recognized), candidate))

    if not recognized:
        return {}, False, ()
    if len(recognized) > 1:
        warnings.append("Multiple pytest summary lines were observed; the last was used.")

    summary = recognized[-1][1]
    counts: dict[str, int] = {}
    for item in _ITEM_RE.finditer(summary):
        label = item.group("label")
        key = "errors" if label.startswith("error") else label
        if key in counts:
            warnings.append(f"Duplicate count category ignored: {key}.")
            continue
        counts[key] = int(item.group("count"))
    return counts, True, tuple(warnings)


def _status_for_runner(
    runner_status: RunnerStatus,
    *,
    exit_code: Optional[int],
    output: str,
    summary_counts: dict[str, int],
    summary_recognized: bool,
) -> tuple[EvidenceStatus, tuple[str, ...]]:
    if runner_status is RunnerStatus.TIMEOUT:
        return EvidenceStatus.TIMEOUT, ()
    if runner_status is RunnerStatus.STARTUP_ERROR:
        return EvidenceStatus.STARTUP_ERROR, ()
    if runner_status is RunnerStatus.EXECUTION_ERROR:
        return EvidenceStatus.EXECUTION_ERROR, ()
    if runner_status is not RunnerStatus.COMPLETED:
        return EvidenceStatus.UNKNOWN, ()
    if _COLLECTION_ERROR_RE.search(output) or summary_counts.get("errors", 0) > 0:
        return EvidenceStatus.COLLECTION_ERROR, ()
    if not summary_recognized:
        return (
            EvidenceStatus.MALFORMED if exit_code is not None else EvidenceStatus.UNKNOWN,
            ("No supported pytest summary line was recognized.",),
        )
    if exit_code == 0:
        return EvidenceStatus.SUCCESSFUL, ()
    return EvidenceStatus.TEST_FAILURES, ()


def normalize_test_evidence(
    result: TestRunResult | object,
    *,
    max_output_bytes: int = _DEFAULT_MAX_OUTPUT_BYTES,
) -> NormalizedTestEvidence:
    """Convert one controlled runner result into bounded, conservative evidence.

    Supported summaries are pytest's comma-separated count format ending in
    ``in <duration>s``, for example ``1 passed, 1 skipped in 0.02s``.
    Other output remains raw evidence but does not produce inferred counts.
    """
    if (
        not isinstance(max_output_bytes, int)
        or isinstance(max_output_bytes, bool)
        or max_output_bytes <= 0
    ):
        return NormalizedTestEvidence(
            evidence_status=EvidenceStatus.MALFORMED,
            runner_status=None,
            project_path=None,
            parser_warnings=("The output limit must be a positive integer.",),
        )
    if not isinstance(result, TestRunResult):
        return NormalizedTestEvidence(
            evidence_status=EvidenceStatus.MALFORMED,
            runner_status=None,
            project_path=None,
            parser_warnings=("Runner evidence was missing or malformed.",),
        )

    stdout, stdout_truncated = _bounded_text(result.stdout, max_output_bytes)
    stderr, stderr_truncated = _bounded_text(result.stderr, max_output_bytes)
    combined = f"{stdout}\n{stderr}"
    counts, recognized, warnings = _parse_summary(combined)
    status, status_warnings = _status_for_runner(
        result.status,
        exit_code=result.exit_code,
        output=combined,
        summary_counts=counts,
        summary_recognized=recognized,
    )
    return NormalizedTestEvidence(
        evidence_status=status,
        runner_status=result.status,
        project_path=result.project_path,
        exit_code=result.exit_code,
        passed=counts.get("passed"),
        failed=counts.get("failed"),
        skipped=counts.get("skipped"),
        xfailed=counts.get("xfailed"),
        xpassed=counts.get("xpassed"),
        errors=counts.get("errors"),
        summary_recognized=recognized,
        stdout=stdout,
        stderr=stderr,
        output_truncated=result.output_truncated or stdout_truncated or stderr_truncated,
        parser_warnings=warnings + status_warnings,
    )
