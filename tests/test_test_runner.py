from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.validation_models import RunnerStatus
from app.services.test_runner import run_pytest


def _project(tmp_path: Path, source: str) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "test_demo.py").write_text(source, encoding="utf-8")
    return project


def test_runs_valid_approved_project(tmp_path: Path) -> None:
    project = _project(tmp_path, "def test_passes():\n    assert 2 + 2 == 4\n")

    result = run_pytest(project, tmp_path)

    assert result.status is RunnerStatus.COMPLETED
    assert result.success is True
    assert result.exit_code == 0
    assert result.timed_out is False


def test_rejects_missing_project(tmp_path: Path) -> None:
    result = run_pytest(tmp_path / "missing", tmp_path)

    assert result.status is RunnerStatus.MISSING_PROJECT


def test_rejects_file_project(tmp_path: Path) -> None:
    file_path = tmp_path / "project.py"
    file_path.write_text("value = 1\n", encoding="utf-8")

    result = run_pytest(file_path, tmp_path)

    assert result.status is RunnerStatus.NOT_A_DIRECTORY


def test_rejects_project_outside_allowed_root(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed_root.mkdir()
    outside.mkdir()

    result = run_pytest(outside, allowed_root)

    assert result.status is RunnerStatus.OUTSIDE_ALLOWED_ROOT


def test_rejects_symlink_project_escape(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed_root.mkdir()
    outside.mkdir()
    (outside / "test_escape.py").write_text(
        "def test_should_not_run():\n    assert False\n",
        encoding="utf-8",
    )
    link = allowed_root / "linked-project"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are unavailable in this environment")

    result = run_pytest(link, allowed_root)

    assert result.status is RunnerStatus.OUTSIDE_ALLOWED_ROOT


def test_rejects_invalid_allowed_root(tmp_path: Path) -> None:
    project = _project(tmp_path, "def test_passes():\n    assert True\n")

    result = run_pytest(project, tmp_path / "missing-root")

    assert result.status is RunnerStatus.INVALID_ALLOWED_ROOT


def test_handles_timeout(tmp_path: Path) -> None:
    project = _project(
        tmp_path,
        "import time\n\ndef test_slow():\n    time.sleep(1)\n",
    )

    result = run_pytest(project, tmp_path, timeout_seconds=0.05)

    assert result.status is RunnerStatus.TIMEOUT
    assert result.timed_out is True
    assert result.success is False


def test_reports_non_zero_pytest_exit_code(tmp_path: Path) -> None:
    project = _project(tmp_path, "def test_fails():\n    assert False\n")

    result = run_pytest(project, tmp_path)

    assert result.status is RunnerStatus.COMPLETED
    assert result.success is False
    assert result.exit_code != 0


def test_captures_stdout_and_stderr(tmp_path: Path) -> None:
    project = _project(
        tmp_path,
        "import sys\n\n"
        "def test_output():\n"
        "    print('stdout marker')\n"
        "    print('stderr marker', file=sys.stderr)\n",
    )

    result = run_pytest(project, tmp_path)

    assert "stdout marker" in result.stdout
    assert "stderr marker" in result.stderr


def test_reports_process_startup_failure(tmp_path: Path) -> None:
    project = _project(tmp_path, "def test_passes():\n    assert True\n")

    with patch(
        "app.services.test_runner.subprocess.Popen",
        side_effect=OSError("simulated startup failure"),
    ):
        result = run_pytest(project, tmp_path)

    assert result.status is RunnerStatus.STARTUP_ERROR
    assert result.exit_code is None
    assert result.error_message == "The controlled pytest process could not be started."


def test_limits_captured_output(tmp_path: Path) -> None:
    project = _project(
        tmp_path,
        "def test_large_output():\n"
        "    print('x' * 5000)\n",
    )

    result = run_pytest(project, tmp_path, max_output_bytes=100)

    assert len(result.stdout.encode("utf-8")) <= 100
    assert result.output_truncated is True


def test_rejects_invalid_limits_without_starting_process(tmp_path: Path) -> None:
    project = _project(tmp_path, "def test_passes():\n    assert True\n")

    with patch("app.services.test_runner.subprocess.Popen") as popen:
        result = run_pytest(project, tmp_path, timeout_seconds=0)

    assert result.status is RunnerStatus.INVALID_INPUT
    popen.assert_not_called()


def test_rejects_malformed_path_input() -> None:
    result = run_pytest(None, None)  # type: ignore[arg-type]

    assert result.status is RunnerStatus.INVALID_INPUT
    assert result.exit_code is None


def test_does_not_accept_a_user_command_argument() -> None:
    import inspect

    parameters = inspect.signature(run_pytest).parameters

    assert "command" not in parameters
