from pathlib import Path

import pytest

from pcobra.gui import runtime


def test_eliminar_archivo_validado_borra_archivo_existente(tmp_path: Path):
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('hola')", encoding="utf-8")

    assert runtime.eliminar_archivo_validado(archivo) is None

    assert not archivo.exists()


def test_eliminar_archivo_validado_rechaza_directorio(tmp_path: Path):
    directorio = tmp_path / "carpeta"
    directorio.mkdir()

    with pytest.raises(ValueError, match="no es un archivo"):
        runtime.eliminar_archivo_validado(directorio)

    assert directorio.is_dir()


def test_eliminar_archivo_validado_rechaza_archivo_inexistente(tmp_path: Path):
    archivo = tmp_path / "no_existe.cobra"

    with pytest.raises(FileNotFoundError, match="No existe el archivo"):
        runtime.eliminar_archivo_validado(archivo)


def test_eliminar_directorio_validado_borra_carpeta_existente(tmp_path: Path):
    directorio = tmp_path / "proyecto"
    directorio.mkdir()
    (directorio / "programa.co").write_text("imprimir('hola')", encoding="utf-8")

    assert runtime.eliminar_directorio_validado(directorio) is None

    assert not directorio.exists()

def test_eliminar_directorio_validado_rechaza_archivo(tmp_path: Path):
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('hola')", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="no es un directorio"):
        runtime.eliminar_directorio_validado(archivo)

    assert archivo.is_file()

def test_eliminar_directorio_validado_rechaza_carpeta_inexistente(tmp_path: Path):
    directorio = tmp_path / "no_existe"

    with pytest.raises(FileNotFoundError, match="No existe el directorio"):
        runtime.eliminar_directorio_validado(directorio)


def test_eliminar_proyecto_validado_borra_proyecto_hijo_directo_de_workspace(
    tmp_path: Path,
):
    workspace = tmp_path / "workspace"
    proyecto = workspace / "mi_proyecto"
    proyecto.mkdir(parents=True)
    (proyecto / "main.cobra").write_text("imprimir('hola')", encoding="utf-8")

    assert runtime.eliminar_proyecto_validado(proyecto, workspace) is None

    assert workspace.is_dir()
    assert not proyecto.exists()

def test_eliminar_proyecto_validado_rechaza_project_root_igual_a_workspace_root(
    tmp_path: Path,
):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with pytest.raises(ValueError, match="raíz completa del workspace"):
        runtime.eliminar_proyecto_validado(workspace, workspace)

    assert workspace.is_dir()

def test_eliminar_proyecto_validado_rechaza_proyecto_cuyo_parent_no_es_workspace_root(
    tmp_path: Path,
):
    workspace = tmp_path / "workspace"
    proyecto = workspace / "grupo" / "mi_proyecto"
    proyecto.mkdir(parents=True)

    with pytest.raises(ValueError, match="hija directa"):
        runtime.eliminar_proyecto_validado(proyecto, workspace)

    assert proyecto.is_dir()

def test_eliminar_proyecto_validado_rechaza_ruta_inexistente(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    proyecto = workspace / "no_existe"

    with pytest.raises(FileNotFoundError, match="No existe el proyecto"):
        runtime.eliminar_proyecto_validado(proyecto, workspace)

def test_eliminar_proyecto_validado_rechaza_archivo(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    proyecto = workspace / "archivo.cobra"
    proyecto.write_text("imprimir('hola')", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="no es un directorio"):
        runtime.eliminar_proyecto_validado(proyecto, workspace)

    assert proyecto.is_file()
