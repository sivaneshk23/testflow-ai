"""Controlled pytest execution for approved local projects."""

from __future__ import annotations

import math
import os
import site
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from app.models.validation_models import RunnerStatus, TestRunResult

_COMMAND_METADATA = ("python", "-m", "pytest", "-q", "-s")
_DEFAULT_TIMEOUT_SECONDS = 30.0
_DEFAULT_MAX_OUTPUT_BYTES = 64 * 1024
_CHUNK_SIZE = 4096


def _result(
    status: RunnerStatus,
    project_path: Optional[str],
    *,
    allowed_root: Optional[str] = None,
    error_message: Optional[str] = None,
    **kwargs: object,
) -> TestRunResult:
    del allowed_root
    return TestRunResult(
        status=status,
        project_path=project_path,
        error_message=error_message,
        **kwargs,
    )


def _resolve(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_paths(
    project_path: str | Path,
    allowed_root: str | Path,
) -> tuple[Optional[Path], Optional[Path], Optional[TestRunResult]]:
    try:
        root = _resolve(allowed_root)
        project = _resolve(project_path)
    except (TypeError, ValueError, OSError, RuntimeError) as error:
        return None, None, _result(
            RunnerStatus.INVALID_INPUT,
            None,
            error_message=f"Paths could not be resolved safely: {error}",
        )

    project_text = str(project)
    if not root.is_dir():
        return None, None, _result(
            RunnerStatus.INVALID_ALLOWED_ROOT,
            project_text,
            error_message="The allowed root does not exist or is not a directory.",
        )
    if not _within(project, root):
        return None, None, _result(
            RunnerStatus.OUTSIDE_ALLOWED_ROOT,
            project_text,
            error_message="The project path is outside the allowed root.",
        )
    if not project.exists():
        return None, None, _result(
            RunnerStatus.MISSING_PROJECT,
            project_text,
            error_message="The project path does not exist.",
        )
    if not project.is_dir():
        return None, None, _result(
            RunnerStatus.NOT_A_DIRECTORY,
            project_text,
            error_message="The project path is not a directory.",
        )
    if project.is_symlink():
        return None, None, _result(
            RunnerStatus.OUTSIDE_ALLOWED_ROOT,
            project_text,
            error_message="Symlinked project directories are not permitted.",
        )
    return root, project, None


def _safe_environment() -> dict[str, str]:
    environment: dict[str, str] = {}
    for name in ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP"):
        value = os.environ.get(name)
        if value:
            environment[name] = value
    # The configured interpreter's user-site packages contain pytest here.
    # Only this package location is passed; unrelated environment variables
    # are intentionally excluded from the child process.
    environment["PYTHONPATH"] = site.getusersitepackages()
    return environment


def _read_stream(
    stream: object,
    limit: int,
    output: list[bytes],
    truncated: list[bool],
) -> None:
    remaining = limit
    while True:
        chunk = stream.read(_CHUNK_SIZE)  # type: ignore[attr-defined]
        if not chunk:
            return
        if remaining:
            output.append(chunk[:remaining])
            remaining -= len(chunk)
        if len(chunk) > max(remaining, 0):
            truncated[0] = True


def _capture_process(
    process: subprocess.Popen[bytes],
    max_output_bytes: int,
    timeout_seconds: float,
) -> tuple[bytes, bytes, bool, bool]:
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    stdout_truncated = [False]
    stderr_truncated = [False]
    stdout_thread = threading.Thread(
        target=_read_stream,
        args=(process.stdout, max_output_bytes, stdout_chunks, stdout_truncated),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_read_stream,
        args=(process.stderr, max_output_bytes, stderr_chunks, stderr_truncated),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()
    timed_out = False
    deadline = time.monotonic() + timeout_seconds
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.01)
    if process.poll() is None:
        timed_out = True
        process.kill()
    process.wait()
    stdout_thread.join()
    stderr_thread.join()
    return (
        b"".join(stdout_chunks),
        b"".join(stderr_chunks),
        timed_out,
        stdout_truncated[0] or stderr_truncated[0],
    )


def run_pytest(
    project_path: str | Path,
    allowed_root: str | Path,
    *,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    max_output_bytes: int = _DEFAULT_MAX_OUTPUT_BYTES,
) -> TestRunResult:
    """Run only ``python -m pytest -q`` in a validated project directory."""
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
        or not isinstance(max_output_bytes, int)
        or isinstance(max_output_bytes, bool)
        or max_output_bytes <= 0
    ):
        return _result(
            RunnerStatus.INVALID_INPUT,
            None,
            error_message="Timeout and output limits must be positive finite values.",
        )

    _, project, validation_error = _validate_paths(project_path, allowed_root)
    if validation_error is not None:
        return validation_error
    assert project is not None

    start = time.monotonic()
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "pytest", "-q", "-s"],
            cwd=str(project),
            env=_safe_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
        stdout, stderr, timed_out, output_truncated = _capture_process(
            process,
            max_output_bytes,
            float(timeout_seconds),
        )
    except OSError:
        return _result(
            RunnerStatus.STARTUP_ERROR,
            str(project),
            error_message="The controlled pytest process could not be started.",
            duration_seconds=time.monotonic() - start,
        )
    except Exception:
        return _result(
            RunnerStatus.EXECUTION_ERROR,
            str(project),
            error_message="The controlled pytest process failed unexpectedly.",
            duration_seconds=time.monotonic() - start,
        )

    duration = time.monotonic() - start
    decoded_stdout = stdout.decode("utf-8", errors="replace")
    decoded_stderr = stderr.decode("utf-8", errors="replace")
    if timed_out:
        status = RunnerStatus.TIMEOUT
    else:
        status = RunnerStatus.COMPLETED
    return TestRunResult(
        status=status,
        project_path=str(project),
        exit_code=process.returncode,
        stdout=decoded_stdout,
        stderr=decoded_stderr,
        timed_out=timed_out,
        duration_seconds=duration,
        output_truncated=output_truncated,
    )
