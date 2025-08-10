import shutil

import pytest
import cobra.core as cobra_core
import core.ast_nodes as core_ast_nodes

from tests.utils.runtime import run_code

# Expone todos los nodos al paquete "cobra.core" y ajusta __all__
node_names = [name for name in dir(core_ast_nodes) if name.startswith("Nodo")]
core_ast_nodes.__all__ = node_names
for name in node_names:
    setattr(cobra_core, name, getattr(core_ast_nodes, name))

from cobra.core import Lexer, Parser
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript as TranspiladorJS


@pytest.mark.skipif(shutil.which("node") is None, reason="requiere Node.js")
def test_runtime_js_imprimir():
    """Transpila y ejecuta un snippet Cobra sencillo en Node.js."""
    codigo_cobra = "imprimir('hola')"
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    codigo_js = TranspiladorJS().generate_code(ast)

    # Elimina las importaciones estándar y define la variable requerida
    lineas = codigo_js.splitlines()[12:]
    codigo_js = "const hola = 'hola';\n" + "\n".join(lineas)

    salida = run_code("js", codigo_js)

    assert "hola" in salida
