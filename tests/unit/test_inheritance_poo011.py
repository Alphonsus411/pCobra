"""Contrato focal de herencia simple y override de POO-011 desde fuente Cobra."""

from contextlib import redirect_stdout
from io import StringIO

import pytest

from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.core.parsing import parsear_codigo_resuelto
from pcobra.core.interpreter import InterpretadorCobra

FUENTE_HERENCIA_SIMPLE = """clase Base:
    metodo valor(este):
        retorno "base"
fin
clase Hija(Base):
fin
var hija = Hija()
imprimir hija.valor()
"""


FUENTE_OVERRIDE = """clase Base:
    metodo valor(este):
        retorno "base"
fin
clase Hija(Base):
    metodo valor(este):
        retorno "hija"
fin
var hija = Hija()
imprimir hija.valor()
"""


def _ast(fuente):
    return parsear_codigo_resuelto(fuente, usar_cache=False)


@pytest.mark.parametrize(
    ("fuente", "esperado"),
    [(FUENTE_HERENCIA_SIMPLE, "base"), (FUENTE_OVERRIDE, "hija")],
)
def test_runtime_ejecuta_herencia_simple_y_override_desde_fuente(
    fuente, esperado, capsys
):
    InterpretadorCobra().ejecutar_ast(_ast(fuente))

    assert capsys.readouterr().out.strip() == esperado


@pytest.mark.parametrize(
    ("fuente", "esperado"),
    [(FUENTE_HERENCIA_SIMPLE, "base"), (FUENTE_OVERRIDE, "hija")],
)
def test_backend_python_ejecuta_herencia_simple_y_override_desde_fuente(
    fuente, esperado
):
    salida = PythonAdapter().compile(_ast(fuente))
    consola = StringIO()

    with redirect_stdout(consola):
        exec(salida, {})

    assert consola.getvalue().strip() == esperado


@pytest.mark.parametrize(
    ("fuente", "esperado"),
    [(FUENTE_HERENCIA_SIMPLE, "base"), (FUENTE_OVERRIDE, "hija")],
)
def test_backend_javascript_emite_herencia_simple_y_override_desde_fuente(
    fuente, esperado
):
    salida = JavaScriptAdapter().compile(_ast(fuente))

    assert "class Hija extends Base {" in salida
    assert "hija.valor()" in salida
    assert f"console.log(hija.valor());" in salida
    assert esperado in salida


FUENTE_HERENCIA_MULTIPLE = """clase BaseA:
fin
clase BaseB:
fin
clase Hija(BaseA, BaseB):
fin
"""


@pytest.mark.parametrize(
    "compilador",
    [
        lambda ast: InterpretadorCobra().ejecutar_ast(ast),
        lambda ast: PythonAdapter().compile(ast),
        lambda ast: JavaScriptAdapter().compile(ast),
    ],
)
def test_herencia_multiple_se_rechaza_expresamente(compilador):
    with pytest.raises(NotImplementedError, match="herencia múltiple"):
        compilador(_ast(FUENTE_HERENCIA_MULTIPLE))
