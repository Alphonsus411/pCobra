import re
from io import StringIO
from unittest.mock import patch

import pytest

from cobra.cli.cli import main


def _fake_transpile(self, ast):
    return self.__class__.__name__


@pytest.mark.timeout(5)
def test_cli_compilar_varios_tipos_en_paralelo(tmp_path):
    archivo = tmp_path / "c.co"
    archivo.write_text("var x = 5")

    class DummyPool:
        def __init__(self, processes=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def map_async(self, func, iterable, chunksize=None):
            class Result:
                def __init__(self, data):
                    self._data = data

                def get(self, timeout=None):
                    return self._data

            return Result([func(item) for item in iterable])

    with patch("cobra.cli.commands.compile_cmd.multiprocessing.Pool", DummyPool), \
         patch("cobra.transpilers.transpiler.to_python.TranspiladorPython.transpilar", _fake_transpile), \
         patch("cobra.transpilers.transpiler.to_js.TranspiladorJavaScript.transpilar", _fake_transpile), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo), "--tipos=python,javascript"])

    lineas = [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in out.getvalue().strip().splitlines()]
    texto = "\n".join(lineas)
    assert "Código generado (TranspiladorPython) para Python (python):" in texto
    assert "Código generado (TranspiladorJavaScript) para JavaScript (javascript):" in texto
