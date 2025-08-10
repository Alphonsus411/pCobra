import os
import shutil
import subprocess
from pathlib import Path

import pytest
import cobra.core as cobra_core
import core.ast_nodes as core_ast_nodes

# Expone todos los nodos al paquete "cobra.core" y ajusta __all__
node_names = [name for name in dir(core_ast_nodes) if name.startswith("Nodo")]
core_ast_nodes.__all__ = node_names
for name in node_names:
    setattr(cobra_core, name, getattr(core_ast_nodes, name))

from cobra.core import Lexer, Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython


@pytest.mark.skipif(shutil.which("python") is None, reason="requiere intérprete de Python")
def test_runtime_python_imprimir():
    """Transpila y ejecuta un snippet Cobra sencillo."""
    codigo_cobra = 'imprimir("hola")'
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    codigo_python = TranspiladorPython().generate_code(ast)

    # Elimina las importaciones estándar y define la variable requerida
    lineas = codigo_python.splitlines()[3:]
    codigo_python = "hola = 'hola'\n" + "\n".join(lineas)

    env = os.environ.copy()
    root = Path(__file__).resolve().parents[3]
    src = root / "src"
    env["PYTHONPATH"] = os.pathsep.join(
        [str(root), str(src), env.get("PYTHONPATH", "")]
    )

    resultado = subprocess.run(
        ["python", "-"],
        input=codigo_python,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )

    assert "hola" in resultado.stdout
