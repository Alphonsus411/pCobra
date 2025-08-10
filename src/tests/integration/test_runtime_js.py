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

try:
    from cobra.transpilers.transpiler.to_js import (
        TranspiladorJavaScript as TranspiladorJS,
    )
except Exception:  # pragma: no cover - si falla la importación se omite la prueba
    TranspiladorJS = None


@pytest.mark.skipif(
    TranspiladorJS is None or shutil.which("node") is None,
    reason="requiere Node.js",
)
@pytest.mark.parametrize(
    "codigo_cobra_fixture", ["codigo_imprimir", "codigo_bucle_simple"]
)
def test_runtime_js_ejecucion(request, codigo_cobra_fixture):
    """Transpila y ejecuta snippets Cobra básicos en Node.js."""
    codigo_cobra = request.getfixturevalue(codigo_cobra_fixture)
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    codigo_js = TranspiladorJS().generate_code(ast)

    # Elimina las importaciones estándar generadas por el transpiler
    lineas = codigo_js.splitlines()[12:]
    codigo_js = "\n".join(lineas)

    salida = run_code("js", codigo_js)

    assert "1" in salida
