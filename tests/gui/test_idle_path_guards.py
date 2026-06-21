from pathlib import Path

import pytest

from pcobra.gui import idle


def test_resolver_ruta_en_project_root_acepta_ruta_relativa_normal(tmp_path: Path):
    project_root = tmp_path / "workspace" / "proyecto"
    project_root.mkdir(parents=True)

    assert idle.resolver_ruta_en_project_root("src/programa.co", project_root) == (
        project_root / "src" / "programa.co"
    ).resolve()


def test_resolver_ruta_en_project_root_bloquea_parent_directory(tmp_path: Path):
    project_root = tmp_path / "workspace" / "proyecto"
    project_root.mkdir(parents=True)

    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        idle.resolver_ruta_en_project_root("../escape.co", project_root)


def test_resolver_ruta_en_project_root_bloquea_absoluta_fuera_de_project_root(
    tmp_path: Path,
):
    project_root = tmp_path / "workspace" / "proyecto"
    externo = tmp_path / "externo.co"
    project_root.mkdir(parents=True)

    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        idle.resolver_ruta_en_project_root(externo, project_root)


def test_validar_ruta_carpeta_eliminable_idle_bloquea_punto_como_carpeta_normal(
    tmp_path: Path,
):
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "proyecto"
    project_root.mkdir(parents=True)

    with pytest.raises(ValueError, match="proyecto activo como carpeta normal"):
        idle.validar_ruta_carpeta_eliminable_idle(".", project_root, workspace_root)


def test_validar_ruta_carpeta_eliminable_idle_bloquea_workspace_root(tmp_path: Path):
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "proyecto"
    project_root.mkdir(parents=True)

    with pytest.raises(ValueError):
        idle.validar_ruta_carpeta_eliminable_idle(
            workspace_root, project_root, workspace_root
        )
