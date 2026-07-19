from io import StringIO
from unittest.mock import patch
import pytest

from cobra.cli.cli import main
from pcobra.cli import build_legacy_cli_shim_main


def _legacy_main():
    return build_legacy_cli_shim_main("cli.cli")


@pytest.mark.timeout(5)
def test_error_msg_compile_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        _legacy_main()(["compilar", str(archivo)])
    assert "archivo" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_error_msg_execute_missing(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["ejecutar", str(archivo)])
    assert "archivo" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_cli_legacy_imports_flag_muestra_ruta_migracion(tmp_path, monkeypatch):
    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        _legacy_main()(["--legacy-imports", "compilar", str(archivo)])
    salida = out.getvalue()
    assert "Compatibilidad legacy habilitada" in salida
    assert "pcobra.*" in salida
