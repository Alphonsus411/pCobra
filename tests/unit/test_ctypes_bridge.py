import subprocess
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoValor,
    NodoLlamadaFuncion,
    NodoImprimir,
)


def _compilar_lib(dir_: Path) -> Path:
    src = dir_ / "lib.c"
    src.write_text("int triple(int x){return x*3;}")
    lib = dir_ / "libtriple.so"
    subprocess.run([
        "gcc",
        "-shared",
        "-fPIC",
        str(src),
        "-o",
        str(lib),
    ], check=True)
    return lib


@pytest.mark.timeout(5)
def test_ctypes_bridge_executes_function(tmp_path):
    lib = _compilar_lib(tmp_path)
    ast = [
        NodoAsignacion(
            "triple",
            NodoLlamadaFuncion(
                "cargar_funcion",
                [NodoValor(f"'{lib}'"), NodoValor("'triple'")],
            ),
        ),
        NodoImprimir(NodoLlamadaFuncion("triple", [NodoValor(4)])),
    ]
    code = TranspiladorPython().generate_code(ast)
    with patch("sys.stdout", new_callable=StringIO) as out:
        exec(code, {})
    assert out.getvalue().strip() == "12"
