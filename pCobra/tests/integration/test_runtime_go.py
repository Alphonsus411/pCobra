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

from cobra.core import Lexer, Parser  # noqa: E402
from cobra.transpilers.transpiler.to_go import TranspiladorGo  # noqa: E402


@pytest.mark.skipif(shutil.which("go") is None, reason="requiere Go")
@pytest.mark.parametrize(
    "codigo_cobra_fixture", ["codigo_imprimir", "codigo_bucle_simple"]
)
def test_runtime_go_ejecucion(request, codigo_cobra_fixture):
    """Transpila y ejecuta snippets Cobra básicos en Go."""
    codigo_cobra = request.getfixturevalue(codigo_cobra_fixture)
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    snippet_go = TranspiladorGo().generate_code(ast)

    codigo_go = (
        "package main\n"
        "import \"fmt\"\n"
        "func main() {\n"
        f"{snippet_go}\n"
        "}\n"
    )

    salida = run_code("go", codigo_go)

    assert "1" in salida

