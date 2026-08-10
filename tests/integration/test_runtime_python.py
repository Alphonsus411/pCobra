import shutil

import pytest
from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser

from tests.utils.runtime import run_code

try:
    from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
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

    salida = run_code("python", codigo_python)

    assert "1" in salida


def test_holobit_operaciones_publicas_semantica_documentada():
    from pcobra.standard_library import holobit

    hb = holobit.crear_holobit([3, 4, 0])
    assert hb == {"tipo": "holobit", "valores": [3.0, 4.0, 0.0]}
    assert holobit.validar_holobit(hb) is True
    assert holobit.proyectar(hb, "2d")["valores"] == [3.0, 4.0]
    assert holobit.transformar(hb, "rotar", "z", 90)["tipo"] == "holobit"
    try:
        vista = holobit.graficar(hb)
        assert isinstance(vista, str)
    except TypeError:
        # Runtime parcial/fallback: la API puede rechazar graficado sin backend disponible.
        pass
    assert holobit.combinar(hb, {"tipo": "holobit", "valores": [1, 2]})["valores"][
        -2:
    ] == [1.0, 2.0]
    assert holobit.medir(hb)["dimension"] == 3
