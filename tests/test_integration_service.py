from pathlib import Path
from unittest.mock import patch

from app.models.validation_models import (
    EvidenceStatus,
    IntegrationStatus,
    InspectionStatus,
    RunnerStatus,
    TestResultStatus,
    TestRunResult,
)
from app.services.integration_service import run_controlled_validation


def _project(tmp_path: Path, source: str = "def test_passes():\n    assert True\n") -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "test_demo.py").write_text(source, encoding="utf-8")
    return project


def test_runs_complete_controlled_workflow(tmp_path: Path) -> None:
    project = _project(tmp_path)

    result = run_controlled_validation(project, tmp_path)

    assert result.status is IntegrationStatus.COMPLETED
    assert result.inspection is not None
    assert result.inspection.status is InspectionStatus.COMPLETE
    assert result.runner is not None
    assert result.evidence is not None
    assert result.evidence.evidence_status is EvidenceStatus.SUCCESSFUL
    assert result.classification is not None
    assert result.classification.status is TestResultStatus.PASSED


def test_blocks_invalid_project_before_runner(tmp_path: Path) -> None:
    with patch("app.services.integration_service.run_pytest") as run:
        result = run_controlled_validation(tmp_path / "missing", tmp_path)

    assert result.status is IntegrationStatus.BLOCKED
    assert result.runner is None
    run.assert_not_called()


def test_blocks_prohibited_startup_hook(tmp_path: Path) -> None:
    project = _project(tmp_path)
    (project / "conftest.py").write_text("", encoding="utf-8")

    result = run_controlled_validation(project, tmp_path)

    assert result.status is IntegrationStatus.BLOCKED
    assert result.runner is not None
    assert result.runner.status is RunnerStatus.PROJECT_POLICY_REJECTED
    assert result.evidence is not None
    assert result.evidence.evidence_status is EvidenceStatus.UNKNOWN


def test_preserves_runner_failure_and_classifies_test_failure(tmp_path: Path) -> None:
    project = _project(tmp_path, "def test_fails():\n    assert False\n")

    result = run_controlled_validation(project, tmp_path)

    assert result.status is IntegrationStatus.COMPLETED
    assert result.runner is not None
    assert result.runner.status is RunnerStatus.COMPLETED
    assert result.runner.exit_code != 0
    assert result.evidence is not None
    assert result.evidence.evidence_status is EvidenceStatus.TEST_FAILURES
    assert result.classification is not None
    assert result.classification.status is TestResultStatus.ASSERTION_FAILURE


def test_runner_failure_is_structured_and_not_presented_as_pass(tmp_path: Path) -> None:
    project = _project(tmp_path)
    runner_result = TestRunResult(
        status=RunnerStatus.STARTUP_ERROR,
        project_path=str(project),
        error_message="The controlled pytest process could not be started.",
    )
    with patch(
        "app.services.integration_service.run_pytest",
        return_value=runner_result,
    ):
        result = run_controlled_validation(project, tmp_path)

    assert result.status is IntegrationStatus.RUNNER_ERROR
    assert result.evidence is not None
    assert result.evidence.evidence_status is EvidenceStatus.STARTUP_ERROR
    assert result.classification is not None
    assert result.classification.status is TestResultStatus.UNKNOWN


def test_normalization_and_classification_receive_runner_output(tmp_path: Path) -> None:
    project = _project(tmp_path)
    runner_result = TestRunResult(
        status=RunnerStatus.COMPLETED,
        project_path=str(project),
        exit_code=0,
        stdout="1 passed in 0.01s\n",
    )
    with patch(
        "app.services.integration_service.run_pytest",
        return_value=runner_result,
    ):
        result = run_controlled_validation(project, tmp_path)

    assert result.evidence is not None
    assert result.evidence.passed == 1
    assert result.classification is not None
    assert result.classification.observed_status == "passed"


def test_malformed_service_inputs_are_blocked() -> None:
    result = run_controlled_validation(None, None)  # type: ignore[arg-type]

    assert result.status is IntegrationStatus.INVALID_INPUT
    assert result.inspection is None
    assert result.runner is None
