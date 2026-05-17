from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.cobra.core.parser import ParserError
from pcobra.cobra.core.runtime import InterpretadorCobra


def _estado(factory, executor, getter, codigo: str):
    cmd = factory()
    executor(cmd, codigo)
    return getter(cmd)


def test_repl_interpreter_evalua_lista_literal_en_asignacion_var():
    interp = _estado(
        lambda: InteractiveCommand(InterpretadorCobra()),
        lambda cmd, code: cmd.ejecutar_codigo(code),
        lambda cmd: cmd.interpretador,
        "var xs = [1, 2, 3]",
    )
    xs = interp.obtener_variable("xs")
    assert isinstance(xs, list)
    assert xs == [1, 2, 3]


def test_repl_interpreter_lista_literal_repr_y_uso_posterior():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo("var xs = [1, 2, 3]")
        repl.ejecutar_codigo("imprimir(xs)")
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo("imprimir(longitud(xs))")

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    assert "[1, 2, 3]" in lineas
    valores = [linea for linea in lineas if linea.isdigit()]
    assert valores[-1] == "3"


def test_repl_interpreter_evalua_lista_con_expresiones_internas():
    interp = _estado(
        lambda: InteractiveCommand(InterpretadorCobra()),
        lambda cmd, code: cmd.ejecutar_codigo(code),
        lambda cmd: cmd.interpretador,
        "var a = 10\nvar xs = [a, a + 1, 3]",
    )
    xs = interp.obtener_variable("xs")
    assert isinstance(xs, list)
    assert xs == [10, 11, 3]


def test_repl_v2_delega_mismo_tratamiento_de_lista_literal():
    interp = _estado(
        ReplCommandV2,
        lambda cmd, code: cmd._ejecutar_en_modo_normal(code),
        lambda cmd: cmd._delegate.interpretador,
        "var a = 5\nvar xs = [a, a + 1]",
    )
    assert interp.obtener_variable("xs") == [5, 6]


def test_repl_interpreter_longitud_lista_literal_y_variable_desde_datos():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo('var xs = [1, 2, 3]')
        repl.ejecutar_codigo('imprimir(longitud(xs))')
        repl.ejecutar_codigo('imprimir(longitud([1, 2, 3]))')

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    valores = [linea for linea in lineas if linea.isdigit()]
    assert valores[-2:] == ["3", "3"]


def test_repl_interpreter_datos_longitud_lista_literal_directa():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo('imprimir(longitud([1, 2, 3]))')

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    valores = [linea for linea in lineas if linea.isdigit()]
    assert valores[-1] == "3"


def test_repl_interpreter_lista_literal_con_variables_longitud_dos():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo('var a = 10')
        repl.ejecutar_codigo('var xs = [a, a + 1]')
        repl.ejecutar_codigo('imprimir(longitud(xs))')

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    valores = [linea for linea in lineas if linea.isdigit()]
    assert valores[-1] == "2"


def test_repl_interpreter_longitud_lista_con_expresiones_y_repr_razonable():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo('var a = 10')
        repl.ejecutar_codigo('var xs = [a, a + 1, 3]')
        repl.ejecutar_codigo('imprimir(longitud(xs))')
        repl.ejecutar_codigo('imprimir(xs)')

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    assert lineas[-2] == "3"
    repr_lista = lineas[-1]
    assert "10" in repr_lista and "11" in repr_lista and "3" in repr_lista
    assert repr_lista.startswith("[") and repr_lista.endswith("]")


def test_repl_interpreter_datos_elemento_variable_y_literal():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo('var ys = [10, 20, 30]')
        repl.ejecutar_codigo('imprimir(elemento(ys, 0))')
        repl.ejecutar_codigo('imprimir(elemento(ys, 1))')
        repl.ejecutar_codigo('imprimir(elemento(ys, 2))')
        repl.ejecutar_codigo('imprimir(elemento([1, 2, 3], 2))')

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    valores = [linea for linea in lineas if linea.isdigit()]
    assert valores[-4:] == ["10", "20", "30", "3"]


def test_repl_interpreter_usar_datos_expone_elemento():
    repl = InteractiveCommand(InterpretadorCobra())
    repl.ejecutar_codigo('usar "datos"')

    simbolos = repl.interpretador.contextos[-1].values
    assert "elemento" in simbolos


def test_repl_interpreter_datos_elemento_regresion_variante_solicitada():
    repl = InteractiveCommand(InterpretadorCobra())
    out = StringIO()

    with redirect_stdout(out):
        repl.ejecutar_codigo('usar "datos"')
        repl.ejecutar_codigo('imprimir(elemento([10, 20, 30], 0))')
        repl.ejecutar_codigo('var ys = [10, 20, 30]')
        repl.ejecutar_codigo('imprimir(elemento(ys, 1))')
        repl.ejecutar_codigo('imprimir(elemento([1, 2, 3], 2))')
        repl.ejecutar_codigo('imprimir(longitud([1, 2, 3]))')

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    valores = [linea for linea in lineas if linea.isdigit()]
    assert valores[-4:] == ["10", "20", "3", "3"]


def test_repl_interpreter_datos_elemento_errores_limpios():
    repl = InteractiveCommand(InterpretadorCobra())
    repl.ejecutar_codigo('usar "datos"')
    repl.ejecutar_codigo('var ys = [10, 20, 30]')

    with pytest.raises(IndexError, match="índice fuera de rango"):
        repl.ejecutar_codigo('imprimir(elemento(ys, 99))')
    with pytest.raises(TypeError, match="índice debe ser entero"):
        repl.ejecutar_codigo('imprimir(elemento(ys, "0"))')
    with pytest.raises(TypeError, match="objeto no indexable"):
        repl.ejecutar_codigo('imprimir(elemento(10, 0))')


def test_repl_v2_datos_elemento_errores_cortos_sin_traceback(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal('var ys = [10, 20, 30]')

    with pytest.raises(IndexError, match="índice fuera de rango") as excinfo:
        cmd._ejecutar_en_modo_normal('imprimir(elemento(ys, 99))')
    salida = capsys.readouterr().out
    assert "índice fuera de rango" in str(excinfo.value)
    assert "Traceback" not in salida

    with pytest.raises(TypeError, match="índice debe ser entero") as excinfo:
        cmd._ejecutar_en_modo_normal('imprimir(elemento(ys, "0"))')
    salida = capsys.readouterr().out
    assert "índice debe ser entero" in str(excinfo.value)
    assert "Traceback" not in salida

    with pytest.raises(TypeError, match="objeto no indexable") as excinfo:
        cmd._ejecutar_en_modo_normal('imprimir(elemento(10, 0))')
    salida = capsys.readouterr().out
    assert "objeto no indexable" in str(excinfo.value)
    assert "Traceback" not in salida


def test_repl_v2_usar_fronteras_rechaza_numpy_y_sintaxis_invalida(capsys):
    cmd = ReplCommandV2()

    with pytest.raises(PermissionError):
        cmd._ejecutar_en_modo_normal('usar "numpy"')
    salida_numpy = capsys.readouterr().out
    assert "Traceback" not in salida_numpy

    with pytest.raises(ParserError):
        cmd._ejecutar_en_modo_normal("usar archivo")
    salida_archivo = capsys.readouterr().out
    assert "Traceback" not in salida_archivo
