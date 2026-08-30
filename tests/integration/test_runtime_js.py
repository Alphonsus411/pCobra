import shutil

import pytest
from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser

from tests.utils.runtime import run_code

try:
    from pcobra.cobra.transpilers.transpiler.to_js import (
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

    try:
        salida = run_code("javascript", codigo_js)
    except RuntimeError as exc:
        if "vm2 no disponible" in str(exc):
            pytest.skip("vm2 no disponible")
        raise

    assert "1" in salida


def test_runtime_javascript_holobit_public_ops_contract():
    from pcobra.cobra.transpilers.common.utils import get_runtime_hooks

    hooks = "\n".join(get_runtime_hooks("javascript"))
    assert "cobra_holobit" in hooks
    assert "cobra_proyectar" in hooks
    assert "cobra_transformar" in hooks
    assert "cobra_graficar" in hooks
    assert "partial" in hooks.lower() or "holobit_sdk" in hooks
