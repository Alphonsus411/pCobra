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
