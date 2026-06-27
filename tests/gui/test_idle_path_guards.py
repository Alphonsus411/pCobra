from pathlib import Path

import pytest

from pcobra.gui import idle


@pytest.fixture
def idle_roots(tmp_path: Path) -> tuple[Path, Path]:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "proyecto"
    project_root.mkdir(parents=True)
    return workspace_root, project_root


def test_resolver_ruta_en_project_root_acepta_ruta_relativa_normal(
    idle_roots: tuple[Path, Path],
):
    _workspace_root, project_root = idle_roots

    assert idle.resolver_ruta_en_project_root("src/programa.co", project_root) == (
        project_root / "src" / "programa.co"
    ).resolve()


def test_resolver_ruta_en_project_root_bloquea_parent_directory(
    idle_roots: tuple[Path, Path],
):
    _workspace_root, project_root = idle_roots

    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        idle.resolver_ruta_en_project_root("../escape.co", project_root)


def test_resolver_ruta_en_project_root_bloquea_absoluta_fuera_de_project_root(
    tmp_path: Path, idle_roots: tuple[Path, Path]
):
    _workspace_root, project_root = idle_roots
    externo = tmp_path / "externo.co"

    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        idle.resolver_ruta_en_project_root(externo, project_root)


def test_validar_ruta_carpeta_eliminable_idle_bloquea_punto_como_carpeta_normal(
    idle_roots: tuple[Path, Path],
):
    workspace_root, project_root = idle_roots

    with pytest.raises(ValueError, match="proyecto activo como carpeta normal"):
        idle.validar_ruta_carpeta_eliminable_idle(".", project_root, workspace_root)


def test_validar_ruta_carpeta_eliminable_idle_bloquea_workspace_root(
    idle_roots: tuple[Path, Path],
):
    workspace_root, project_root = idle_roots

    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        idle.validar_ruta_carpeta_eliminable_idle(
            workspace_root, project_root, workspace_root
        )


def test_validar_project_root_eliminable_idle_exige_proyecto_activo_existente(
    idle_roots: tuple[Path, Path],
):
    workspace_root, project_root = idle_roots
    project_root.rmdir()

    with pytest.raises(FileNotFoundError, match="No existe el proyecto"):
        idle.validar_project_root_eliminable_idle(project_root, workspace_root)
