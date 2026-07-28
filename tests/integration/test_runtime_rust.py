import shutil

import pytest

from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust

from tests.utils.runtime import run_code


@pytest.mark.skipif(
    shutil.which("rustc") is None,
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



def test_runtime_rust_holobit_public_ops_contract():
    from pcobra.cobra.transpilers.common.utils import get_runtime_hooks
    hooks = "\n".join(get_runtime_hooks("rust"))
    assert "cobra_holobit" in hooks
    assert "cobra_proyectar" in hooks
    assert "cobra_transformar" in hooks
    assert "cobra_graficar" in hooks
    assert "partial" in hooks.lower() or "holobit_sdk" in hooks
