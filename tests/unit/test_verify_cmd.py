import pytest
from unittest.mock import patch

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


def test_verify_command_supported_languages_canonicos():
    comando = VerifyCommand()

    assert "python" in comando.SUPPORTED_LANGUAGES
    assert "javascript" in comando.SUPPORTED_LANGUAGES
    assert "rust" in comando.SUPPORTED_LANGUAGES
    assert "cpp" in comando.SUPPORTED_LANGUAGES
    assert "js" not in comando.SUPPORTED_LANGUAGES


@pytest.mark.parametrize("language", ["rust", "cpp"])
def test_verify_command_usa_contenedor_para_runtimes_compilados(language):
    comando = VerifyCommand()

    class DummyTranspiler:
        def generate_code(self, _ast):
            return "codigo"

    with patch(
        "pcobra.cobra.cli.commands.verify_cmd.ejecutar_en_contenedor",
        return_value="ok\n",
    ) as mock_runtime:
        salida, error = comando._compile_and_execute([], language, DummyTranspiler())

    assert error is None
    assert salida == "ok\n"
    mock_runtime.assert_called_once_with("codigo", language)
