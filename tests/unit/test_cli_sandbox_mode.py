import io
from unittest.mock import patch
import pytest

from cobra.cli.cli import main


@pytest.mark.timeout(5)
def test_cli_sandbox_operacion_prohibida(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("open('f.txt', 'w')")
    salida = io.StringIO()
    with patch('cobra.cli.i18n.LOCALE_DIR', tmp_path), \
         patch('cobra.transpilers.module_map.get_toml_map', return_value={}), \
         patch('cobra.cli.commands.execute_cmd.ejecutar_en_sandbox', side_effect=RuntimeError('operación prohibida')), \
         patch('sys.stdout', salida):
        codigo = main(["ejecutar", str(archivo), "--sandbox"])
    out = salida.getvalue()
    assert codigo != 0
    assert "Error de ejecución en sandbox" in out


@pytest.mark.timeout(5)
def test_cli_sandbox_operacion_valida(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("print(2+2)")
    with patch('cobra.cli.i18n.LOCALE_DIR', tmp_path), \
         patch('cobra.transpilers.module_map.get_toml_map', return_value={}), \
         patch('cobra.cli.commands.execute_cmd.ejecutar_en_sandbox', return_value='Resultado de sandbox'), \
         patch('sys.stdout', new_callable=io.StringIO) as stdout:
        codigo = main(["ejecutar", str(archivo), "--sandbox"])
    assert codigo == 0
    assert "Resultado de sandbox" in stdout.getvalue()
