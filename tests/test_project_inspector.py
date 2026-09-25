from pathlib import Path

from app.models.validation_models import InspectionStatus
from app.services.project_inspector import inspect_project


def test_inspects_valid_python_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "calculator.py").write_text(
        "def add(left: int, right: int) -> int:\n    return left + right\n",
        encoding="utf-8",
    )

    result = inspect_project(project, tmp_path)

    assert result.status is InspectionStatus.COMPLETE
    assert [file.relative_path for file in result.python_files] == ["calculator.py"]
    assert result.python_files[0].functions == ("add",)
    assert result.findings == ()
    assert result.static_only is True


def test_missing_project_is_reported(tmp_path: Path) -> None:
    result = inspect_project(tmp_path / "missing", tmp_path)

    assert result.status is InspectionStatus.INVALID_PATH
    assert result.findings[0].code == "MISSING_PROJECT"


def test_file_path_is_rejected_as_project(tmp_path: Path) -> None:
    project_file = tmp_path / "project.py"
    project_file.write_text("value = 1\n", encoding="utf-8")

    result = inspect_project(project_file, tmp_path)

    assert result.status is InspectionStatus.NOT_A_DIRECTORY
    assert result.findings[0].code == "NOT_A_DIRECTORY"


def test_path_outside_allowed_root_is_rejected(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    outside_project = tmp_path / "outside"
    allowed_root.mkdir()
    outside_project.mkdir()

    result = inspect_project(outside_project, allowed_root)

    assert result.status is InspectionStatus.OUTSIDE_ALLOWED_ROOT
    assert result.findings[0].code == "OUTSIDE_ALLOWED_ROOT"


def test_syntax_error_is_a_structured_finding(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "broken.py").write_text("def broken(:\n", encoding="utf-8")

    result = inspect_project(project, tmp_path)

    assert result.status is InspectionStatus.COMPLETE
    assert result.python_files[0].syntax_error is not None
    assert result.findings[0].code == "SYNTAX_ERROR"


def test_empty_project_is_complete_with_no_files(tmp_path: Path) -> None:
    project = tmp_path / "empty"
    project.mkdir()

    result = inspect_project(project, tmp_path)

    assert result.status is InspectionStatus.COMPLETE
    assert result.python_files == ()
    assert result.findings == ()

