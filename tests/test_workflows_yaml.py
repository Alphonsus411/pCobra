"""Pruebas para validar los archivos de workflows de GitHub."""

from pathlib import Path

import pytest
import yaml


WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"
WORKFLOW_FILES = tuple(
    sorted(
        workflow
        for pattern in ("*.yml", "*.yaml")
        for workflow in WORKFLOWS_DIR.glob(pattern)
        if workflow.is_file()
    )
)


@pytest.mark.parametrize("workflow_path", WORKFLOW_FILES, ids=lambda path: path.name)
def test_workflow_file_contains_valid_yaml(workflow_path: Path) -> None:
    """Comprueba que cada workflow sea YAML válido."""
    try:
        content = workflow_path.read_text(encoding="utf-8")
        yaml.safe_load(content)
    except yaml.YAMLError as exc:  # pragma: no cover - caso de fallo explícito
        pytest.fail(f"El workflow {workflow_path} no es un YAML válido: {exc}")


@pytest.mark.parametrize(
    ("workflow_filename", "job_name"),
    (
        ("ci.yml", "tier1-required"),
        ("test.yml", "tier1-required"),
    ),
)
def test_workflow_has_smoke_syntax_gate(workflow_filename: str, job_name: str) -> None:
    """Garantiza que el gate temprano de sintaxis siga presente en workflows críticos."""
    workflow_path = WORKFLOWS_DIR / workflow_filename
    content = workflow_path.read_text(encoding="utf-8")

    assert f"{job_name}:" in content
    assert "name: Run smoke syntax gates" in content
    assert "if: runner.os != 'Windows'" in content
    assert "shell: bash" in content
    assert "name: Run smoke syntax gates (Windows)" in content
    assert "if: runner.os == 'Windows'" in content
    assert "shell: pwsh" in content
    assert "python scripts/smoke_syntax.py" in content
    assert "python scripts/smoke_transpilers_syntax.py" in content


@pytest.mark.parametrize(
    "workflow_filename",
    (
        "build-binaries.yml",
        "ci.yml",
        "docker.yml",
        "pages.yml",
        "runtime-stabilization-contract.yml",
    ),
)
def test_workflow_branch_triggers_target_default_branch(workflow_filename: str) -> None:
    """Garantiza que los workflows críticos cubran las ramas existentes."""
    workflow_path = WORKFLOWS_DIR / workflow_filename
    content = workflow_path.read_text(encoding="utf-8")

    assert "master" not in content
    assert "branches: [ main, work ]" in content or (
        "      - main" in content and "      - work" in content
    )


def test_ci_protected_file_guard_uses_event_appropriate_comparison() -> None:
    """Evita construir una referencia vacía con ``base_ref`` en eventos push."""
    content = (WORKFLOWS_DIR / "ci.yml").read_text(encoding="utf-8")

    assert 'EVENT_NAME: ${{ github.event_name }}' in content
    assert 'BEFORE_SHA: ${{ github.event.before }}' in content
    assert '[[ "$EVENT_NAME" == "pull_request" ]]' in content
    assert '[[ "$EVENT_NAME" == "push" ]]' in content
    assert 'comparison_args=("${BEFORE_SHA}...HEAD")' in content
    assert 'comparison_args=("HEAD^...HEAD")' in content
