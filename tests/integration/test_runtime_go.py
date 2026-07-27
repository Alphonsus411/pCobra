import shutil

import pytest

from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser
from tests.utils.runtime import run_code

try:
    from pcobra.cobra.transpilers.transpiler.to_go import TranspiladorGo
except ImportError:
    TranspiladorGo = None


@pytest.mark.experimental
@pytest.mark.skipif(TranspiladorGo is None, reason="TranspiladorGo module not found")
@pytest.mark.skipif(shutil.which("go") is None, reason="requiere Go")
@pytest.mark.parametrize(
    "codigo_cobra_fixture", ["codigo_imprimir", "codigo_bucle_simple"]
)
def test_runtime_go_ejecucion_experimental(request, codigo_cobra_fixture):
    """Cobertura manual/best-effort para Go; no es runtime oficial contractual."""
    codigo_cobra = request.getfixturevalue(codigo_cobra_fixture)
    lexer = Lexer(codigo_cobra)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    codigo_go = TranspiladorGo().generate_code(ast)
    salida = run_code("go", codigo_go)

    assert "1" in salida
