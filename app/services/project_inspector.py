"""Safe, read-only inspection of a configured Python project."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Optional

from app.models.validation_models import (
    InspectionFinding,
    InspectionStatus,
    ProjectInspectionResult,
    PythonFileInfo,
)


def _invalid_result(
    status: InspectionStatus,
    message: str,
    project_path: Optional[str] = None,
    allowed_root: Optional[str] = None,
    code: str = "INVALID_PATH",
) -> ProjectInspectionResult:
    return ProjectInspectionResult(
        status=status,
        project_path=project_path,
        allowed_root=allowed_root,
        findings=(InspectionFinding(code=code, message=message),),
    )


def _resolve_path(value: str | Path) -> Path:
    """Resolve a path without requiring it to exist."""
    return Path(value).expanduser().resolve(strict=False)


def _has_symlink_component(value: str | Path) -> bool:
    raw = Path(value).expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    current = Path(raw.anchor)
    for part in raw.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _parse_python_file(
    file_path: Path,
    project_root: Path,
) -> tuple[PythonFileInfo, Optional[InspectionFinding]]:
    relative_path = file_path.relative_to(project_root).as_posix()
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        finding = InspectionFinding(
            code="FILE_READ_ERROR",
            message=f"Could not read permitted Python file: {error}",
            relative_path=relative_path,
        )
        return (
            PythonFileInfo(
                path=str(file_path),
                relative_path=relative_path,
            ),
            finding,
        )

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as error:
        message = f"Python syntax error at line {error.lineno}: {error.msg}"
        finding = InspectionFinding(
            code="SYNTAX_ERROR",
            message=message,
            relative_path=relative_path,
        )
        return (
            PythonFileInfo(
                path=str(file_path),
                relative_path=relative_path,
                syntax_error=message,
            ),
            finding,
        )

    functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    test_functions = tuple(name for name in functions if name.startswith("test_"))
    return (
        PythonFileInfo(
            path=str(file_path),
            relative_path=relative_path,
            functions=functions,
            test_functions=test_functions,
        ),
        None,
    )


def inspect_project(
    project_path: str | Path,
    allowed_root: str | Path,
) -> ProjectInspectionResult:
    """Inspect permitted Python files without importing or executing project code."""
    try:
        if _has_symlink_component(allowed_root) or _has_symlink_component(
            project_path
        ):
            return _invalid_result(
                InspectionStatus.INVALID_PATH,
                "Symlinked allowed roots and project paths are not permitted.",
                code="SYMLINK_NOT_ALLOWED",
            )
        root = _resolve_path(allowed_root)
        project = _resolve_path(project_path)
    except (TypeError, ValueError, OSError, RuntimeError) as error:
        return _invalid_result(
            InspectionStatus.INVALID_PATH,
            f"Path could not be resolved safely: {error}",
            code="INVALID_PATH",
        )

    root_text = str(root)
    project_text = str(project)
    if not root.is_dir():
        return _invalid_result(
            InspectionStatus.INVALID_PATH,
            "The allowed project root does not exist or is not a directory.",
            project_path=project_text,
            allowed_root=root_text,
            code="INVALID_ALLOWED_ROOT",
        )
    if not _is_within(project, root):
        return _invalid_result(
            InspectionStatus.OUTSIDE_ALLOWED_ROOT,
            "The project path is outside the configured allowed root.",
            project_path=project_text,
            allowed_root=root_text,
            code="OUTSIDE_ALLOWED_ROOT",
        )
    if not project.exists():
        return _invalid_result(
            InspectionStatus.INVALID_PATH,
            "The configured project path does not exist.",
            project_path=project_text,
            allowed_root=root_text,
            code="MISSING_PROJECT",
        )
    if not project.is_dir():
        return _invalid_result(
            InspectionStatus.NOT_A_DIRECTORY,
            "The configured project path is not a directory.",
            project_path=project_text,
            allowed_root=root_text,
            code="NOT_A_DIRECTORY",
        )

    files: list[PythonFileInfo] = []
    findings: list[InspectionFinding] = []
    try:
        candidates = sorted(project.rglob("*.py"), key=lambda path: path.as_posix())
    except OSError as error:
        return _invalid_result(
            InspectionStatus.INSPECTION_ERROR,
            f"Could not enumerate permitted Python files: {error}",
            project_path=project_text,
            allowed_root=root_text,
            code="ENUMERATION_ERROR",
        )

    for candidate in candidates:
        relative_path = candidate.relative_to(project).as_posix()
        if candidate.is_symlink():
            findings.append(
                InspectionFinding(
                    code="SYMLINK_SKIPPED",
                    message="Symlinked Python files are not inspected.",
                    relative_path=relative_path,
                )
            )
            continue
        try:
            resolved_candidate = candidate.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            findings.append(
                InspectionFinding(
                    code="FILE_RESOLUTION_ERROR",
                    message=f"Could not safely resolve Python file: {error}",
                    relative_path=relative_path,
                )
            )
            continue
        if not _is_within(resolved_candidate, project):
            findings.append(
                InspectionFinding(
                    code="FILE_OUTSIDE_PROJECT",
                    message="A discovered Python file resolved outside the project.",
                    relative_path=relative_path,
                )
            )
            continue
        file_info, finding = _parse_python_file(resolved_candidate, project)
        files.append(file_info)
        if finding is not None:
            findings.append(finding)

    return ProjectInspectionResult(
        status=InspectionStatus.COMPLETE,
        project_path=project_text,
        allowed_root=root_text,
        python_files=tuple(files),
        findings=tuple(findings),
    )
