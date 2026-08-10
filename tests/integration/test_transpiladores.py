import os
import subprocess
import sys
from pathlib import Path

import pcobra
from pcobra.core.ast_nodes import NodoImprimir, NodoValor
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython


ROOT = Path(__file__).resolve().parents[2]


def test_transpilador_python_generacion(tmp_path):
    ast = [NodoImprimir(NodoValor("'hola'"))]
    codigo = TranspiladorPython().generate_code(ast)
    assert "from pcobra.cobra.core.nativos import *" in codigo
    assert "import pcobra.corelibs as _pcobra_corelibs" in codigo
    assert "import pcobra.standard_library as _pcobra_standard_library" in codigo
    assert "print(" in codigo
    assert "hola" in codigo
    compile(codigo, "<cobra-transpilado>", "exec")

    artefacto = tmp_path / "programa.py"
    artefacto.write_bytes(codigo.encode("utf-8"))
    assert artefacto.read_bytes() == codigo.encode("utf-8")
    assert str(ROOT) not in codigo

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    resultado = subprocess.run(
        [sys.executable, str(artefacto)],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    assert resultado.stdout == "'hola'\n"
