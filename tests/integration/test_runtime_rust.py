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

try:
    from cobra.transpilers.transpiler.to_rust import TranspiladorRust  # noqa: E402
except Exception:  # pragma: no cover - si la importación falla se omite la prueba
    TranspiladorRust = None


@pytest.mark.skipif(
    TranspiladorRust is None or shutil.which("rustc") is None,
    reason="requiere rustc",
)
@pytest.mark.parametrize(
    "codigo_cobra_fixture", ["codigo_imprimir", "codigo_bucle_simple"]
)
def test_runtime_rust_ejecucion(request, codigo_cobra_fixture):
    """Transpila y ejecuta snippets Cobra básicos en Rust."""
    codigo_cobra = request.getfixturevalue(codigo_cobra_fixture)
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    snippet_rust = TranspiladorRust().generate_code(ast)

    codigo_rust = (
        "fn main() {\n"
        f"{snippet_rust}\n"
        "}\n"
    )

    salida = run_code("rust", codigo_rust)

    assert "1" in salida

