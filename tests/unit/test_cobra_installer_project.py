from __future__ import annotations

from pathlib import Path

from pcobra.cobra_installer import discover_project, validate_project


def _create_minimal_cobra_project(root: Path) -> tuple[Path, Path]:
    """Crea un proyecto Cobra mínimo para pruebas del instalador."""

    entrypoint = root / "main.cobra"
    manifest = root / "cobra.toml"
    entrypoint.write_text("imprimir('hola desde installer')\n", encoding="utf-8")
    manifest.write_text(
        '[project]\nname = "demo-installer"\nversion = "0.1.0"\n'
        '[build]\nentrypoint = "main.cobra"\n',
        encoding="utf-8",
    )
    return entrypoint, manifest


def test_installer_detecta_y_valida_proyecto_cobra_minimo(tmp_path: Path) -> None:
    entrypoint, manifest = _create_minimal_cobra_project(tmp_path)

    project = discover_project(tmp_path)
    validation = validate_project(project)

    assert project.project_root == tmp_path.resolve()
    assert project.entrypoint == entrypoint
    assert project.cobra_toml == manifest
    assert project.config["project"]["name"] == "demo-installer"
    assert project.config["build"]["entrypoint"] == "main.cobra"
    assert validation.is_valid
    assert validation.errors == ()
