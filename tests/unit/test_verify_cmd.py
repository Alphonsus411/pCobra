import pytest

from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand, VALID_EXTENSIONS


def test_valid_extensions_include_co():
    """La extensión `.co` debe incluirse en el listado permitido."""
    assert ".co" in VALID_EXTENSIONS


def test_verify_command_accepts_co_file(tmp_path):
    """`VerifyCommand` debe aceptar archivos `.co`."""
    archivo = tmp_path / "script.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    comando = VerifyCommand()

    # No debe lanzar excepción.
    comando._validate_file(str(archivo))
