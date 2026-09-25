"""Small, immutable models for static inspection and result classification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class InspectionStatus(str, Enum):
    """Overall status of a static project inspection."""

    COMPLETE = "complete"
    INVALID_PATH = "invalid_path"
    NOT_A_DIRECTORY = "not_a_directory"
    OUTSIDE_ALLOWED_ROOT = "outside_allowed_root"
    INSPECTION_ERROR = "inspection_error"


class RunnerStatus(str, Enum):
    """Status of a controlled pytest process."""

    COMPLETED = "completed"
    INVALID_INPUT = "invalid_input"
    INVALID_ALLOWED_ROOT = "invalid_allowed_root"
    MISSING_PROJECT = "missing_project"
    NOT_A_DIRECTORY = "not_a_directory"
    OUTSIDE_ALLOWED_ROOT = "outside_allowed_root"
    SYMLINK_NOT_ALLOWED = "symlink_not_allowed"
    PROJECT_POLICY_REJECTED = "project_policy_rejected"
    TIMEOUT = "timeout"
    STARTUP_ERROR = "startup_error"
    EXECUTION_ERROR = "execution_error"


class TestResultStatus(str, Enum):
    """Conservative categories for observed test evidence."""

    PASSED = "passed"
    ASSERTION_FAILURE = "assertion_failure"
    EXCEPTION = "exception"
    COLLECTION_ERROR = "collection_error"
    UNKNOWN = "unknown"


TestResultStatus.__test__ = False


class EvidenceStatus(str, Enum):
    """High-level status of normalized runner evidence."""

    SUCCESSFUL = "successful"
    TEST_FAILURES = "test_failures"
    COLLECTION_ERROR = "collection_error"
    TIMEOUT = "timeout"
    STARTUP_ERROR = "startup_error"
    EXECUTION_ERROR = "execution_error"
    MALFORMED = "malformed"
    UNKNOWN = "unknown"


EvidenceStatus.__test__ = False


class IntegrationStatus(str, Enum):
    """Overall status of one coordinated validation workflow."""

    COMPLETED = "completed"
    BLOCKED = "blocked"
    INVALID_INPUT = "invalid_input"
    INSPECTION_ERROR = "inspection_error"
    RUNNER_ERROR = "runner_error"


IntegrationStatus.__test__ = False


class ReportStatus(str, Enum):
    """User-facing status categories for one validation report."""

    SUCCESSFUL = "successful"
    TEST_FAILURES = "test_failures"
    COLLECTION_ERROR = "collection_error"
    BLOCKED = "blocked"
    INSPECTION_ERROR = "inspection_error"
    RUNNER_ERROR = "runner_error"
    TIMEOUT = "timeout"
    MALFORMED = "malformed"
    UNKNOWN = "unknown"


ReportStatus.__test__ = False


@dataclass(frozen=True)
class InspectionFinding:
    """A structured issue found while inspecting a project."""

    code: str
    message: str
    relative_path: Optional[str] = None


@dataclass(frozen=True)
class PythonFileInfo:
    """Static metadata collected from one permitted Python source file."""

    path: str
    relative_path: str
    functions: tuple[str, ...] = ()
    test_functions: tuple[str, ...] = ()
    syntax_error: Optional[str] = None


@dataclass(frozen=True)
class ProjectInspectionResult:
    """Result of inspecting a project without importing or executing it."""

    status: InspectionStatus
    project_path: Optional[str]
    allowed_root: Optional[str]
    python_files: tuple[PythonFileInfo, ...] = ()
    findings: tuple[InspectionFinding, ...] = ()
    static_only: bool = True


@dataclass(frozen=True)
class ObservedTestResult:
    """Minimal structured evidence accepted by the classifier."""

    status: str
    output: Optional[str] = None
    error_type: Optional[str] = None
    exit_code: Optional[int] = None
    collection_error: bool = False


@dataclass(frozen=True)
class ClassifiedFailureInfo:
    """Classification kept separate from the observed test evidence."""

    status: TestResultStatus
    observed_status: Optional[str]
    evidence_summary: str
    root_cause_supported: bool = False


@dataclass(frozen=True)
class TestRunResult:
    """Bounded evidence from one controlled pytest invocation."""

    status: RunnerStatus
    project_path: Optional[str]
    command_metadata: tuple[str, ...] = ("-m", "pytest", "-q", "-s")
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    output_truncated: bool = False

    @property
    def success(self) -> bool:
        """Return true only when pytest completed with exit code zero."""
        return (
            self.status is RunnerStatus.COMPLETED
            and self.exit_code == 0
            and not self.timed_out
        )


TestRunResult.__test__ = False


@dataclass(frozen=True)
class NormalizedTestEvidence:
    """Bounded, parser-derived evidence from one controlled pytest run."""

    evidence_status: EvidenceStatus
    runner_status: Optional[RunnerStatus]
    project_path: Optional[str]
    exit_code: Optional[int] = None
    passed: Optional[int] = None
    failed: Optional[int] = None
    skipped: Optional[int] = None
    xfailed: Optional[int] = None
    xpassed: Optional[int] = None
    errors: Optional[int] = None
    summary_recognized: bool = False
    stdout: str = ""
    stderr: str = ""
    output_truncated: bool = False
    parser_warnings: tuple[str, ...] = ()


NormalizedTestEvidence.__test__ = False


@dataclass(frozen=True)
class IntegrationResult:
    """Immutable result spanning inspection, execution, evidence, and classification."""

    status: IntegrationStatus
    inspection: Optional[ProjectInspectionResult] = None
    runner: Optional[TestRunResult] = None
    evidence: Optional[NormalizedTestEvidence] = None
    classification: Optional[ClassifiedFailureInfo] = None
    error_message: Optional[str] = None


IntegrationResult.__test__ = False


@dataclass(frozen=True)
class ValidationReport:
    """Immutable user-facing projection of observed validation evidence.

    This model intentionally contains no AI-generated explanation and does not
    serialize itself. JSON schema construction belongs to a later presentation
    or report-export layer.
    """

    status: ReportStatus
    integration_status: Optional[IntegrationStatus] = None
    project_path: Optional[str] = None
    inspection_status: Optional[InspectionStatus] = None
    runner_status: Optional[RunnerStatus] = None
    evidence_status: Optional[EvidenceStatus] = None
    exit_code: Optional[int] = None
    passed: Optional[int] = None
    failed: Optional[int] = None
    skipped: Optional[int] = None
    xfailed: Optional[int] = None
    xpassed: Optional[int] = None
    errors: Optional[int] = None
    summary_recognized: bool = False
    stdout: str = ""
    stderr: str = ""
    output_truncated: bool = False
    warnings: tuple[str, ...] = ()
    classification: Optional[ClassifiedFailureInfo] = None
    error_message: Optional[str] = None


ValidationReport.__test__ = False
