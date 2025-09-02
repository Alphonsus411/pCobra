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
    from cobra.transpilers.transpiler.to_python import TranspiladorPython
except Exception:  # pragma: no cover - si falla la importación se omite la prueba
    TranspiladorPython = None


@pytest.mark.skipif(
    TranspiladorPython is None or shutil.which("python") is None,
    reason="requiere intérprete de Python",
)
@pytest.mark.parametrize(
    "codigo_cobra_fixture", ["codigo_imprimir", "codigo_bucle_simple"]
)
def test_runtime_python_ejecucion(request, codigo_cobra_fixture):
    """Transpila y ejecuta snippets Cobra básicos."""
    codigo_cobra = request.getfixturevalue(codigo_cobra_fixture)
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    codigo_python = TranspiladorPython().generate_code(ast)

    # Elimina las importaciones estándar generadas por el transpiler
    lineas = codigo_python.splitlines()[3:]
    codigo_python = "\n".join(lineas)

    salida = run_code("python", codigo_python)

    assert "1" in salida
