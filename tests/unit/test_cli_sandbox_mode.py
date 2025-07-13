import io
from unittest.mock import patch
import pytest

from cli.cli import main


@pytest.mark.timeout(5)
def test_cli_sandbox_operacion_prohibida(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("open('f.txt', 'w')")
    salida = io.StringIO()
    with patch('cobra.transpilers.module_map.get_toml_map', return_value={}), \
         patch('sys.stdout', salida):
        codigo = main(["ejecutar", str(archivo), "--sandbox"])
    out = salida.getvalue()
    assert codigo != 0
    assert "Error ejecutando en sandbox" in out


@pytest.mark.timeout(5)
def test_cli_sandbox_operacion_valida(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("print(2+2)")
    with patch('cobra.transpilers.module_map.get_toml_map', return_value={}), \
         patch('sys.stdout', new_callable=io.StringIO):
        codigo = main(["ejecutar", str(archivo), "--sandbox"])
    assert codigo == 0
