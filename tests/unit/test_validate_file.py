import os

import pytest

from pcobra.cobra.cli.commands.compile_cmd import MAX_FILE_SIZE, validate_file


def test_validate_file_nonexistent(tmp_path):
    """Debe fallar si el archivo no existe."""
    ruta_invalida = tmp_path / "inexistente.cobra"
    with pytest.raises(ValueError):
        validate_file(str(ruta_invalida))


def test_validate_file_no_read_permission(tmp_path, monkeypatch):
    """Debe fallar si no hay permisos de lectura."""
    archivo = tmp_path / "sin_permiso.cobra"
    archivo.write_text("contenido")
    os.chmod(archivo, 0)

    monkeypatch.setattr(os, "access", lambda *_: False)

    with pytest.raises(ValueError):
        validate_file(str(archivo))


def test_validate_file_too_large(tmp_path):
    """Debe fallar si el archivo excede el tamaño permitido."""
    archivo = tmp_path / "grande.cobra"
    with open(archivo, "wb") as f:
        f.seek(MAX_FILE_SIZE)
        f.write(b"0")

    with pytest.raises(ValueError):
        validate_file(str(archivo))


def test_validate_file_ok(tmp_path):
    """Devuelve ``True`` para un archivo válido."""
    archivo = tmp_path / "valido.cobra"
    archivo.write_text("imprimir('hola')\n")
    assert validate_file(str(archivo)) is True


@pytest.mark.parametrize("extension", [".co", ".txt", ".py"])
def test_validate_file_rechaza_archivos_que_no_son_fuente_cobra(
    tmp_path, extension
):
    archivo = tmp_path / f"programa{extension}"
    archivo.write_text("imprimir('no ejecutar')\n", encoding="utf-8")

    with pytest.raises(ValueError, match="paquete Cobra|extensión \\.cobra"):
        validate_file(str(archivo))
