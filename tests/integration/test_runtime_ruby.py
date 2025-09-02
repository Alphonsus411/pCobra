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
from cobra.transpilers.transpiler.to_ruby import TranspiladorRuby  # noqa: E402


@pytest.mark.skipif(shutil.which("ruby") is None, reason="requiere Ruby")
@pytest.mark.parametrize("codigo_cobra_fixture", ["codigo_imprimir"])
def test_runtime_ruby_ejecucion(request, codigo_cobra_fixture):
    """Transpila y ejecuta snippets Cobra básicos en Ruby."""
    codigo_cobra = request.getfixturevalue(codigo_cobra_fixture)
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    codigo_ruby = TranspiladorRuby().generate_code(ast)

    salida = run_code("ruby", codigo_ruby)

    assert "1" in salida

