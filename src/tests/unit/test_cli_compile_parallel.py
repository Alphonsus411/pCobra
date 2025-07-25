import os
import pytest
from io import StringIO
from unittest.mock import patch

from cli.cli import main


def _fake_transpile(self, ast):
    import time
    time.sleep(0.1)
    return str(os.getpid())


@pytest.mark.timeout(5)
def test_cli_compilar_varios_tipos_en_paralelo(tmp_path):
    archivo = tmp_path / "c.co"
    archivo.write_text("var x = 5")
    with patch("cobra.transpilers.transpiler.to_python.TranspiladorPython.transpilar", _fake_transpile), \
         patch("cobra.transpilers.transpiler.to_js.TranspiladorJavaScript.transpilar", _fake_transpile), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo), "--tipos=python,js"])
    lineas = out.getvalue().strip().splitlines()
    assert lineas[0].startswith("Código generado (TranspiladorPython) para python:")
    assert lineas[2].startswith("Código generado (TranspiladorJavaScript) para js:")
    pid1 = lineas[1]
    pid2 = lineas[3]
    assert pid1 != pid2
