from __future__ import annotations

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
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
    assert interp.obtener_variable("xs") == [1, 2, 3]


def test_repl_interpreter_evalua_lista_con_expresiones_internas():
    interp = _estado(
        lambda: InteractiveCommand(InterpretadorCobra()),
        lambda cmd, code: cmd.ejecutar_codigo(code),
        lambda cmd: cmd.interpretador,
        "var a = 10\nvar xs = [a, a + 1]",
    )
    assert interp.obtener_variable("xs") == [10, 11]


def test_repl_v2_delega_mismo_tratamiento_de_lista_literal():
    interp = _estado(
        ReplCommandV2,
        lambda cmd, code: cmd._ejecutar_en_modo_normal(code),
        lambda cmd: cmd._delegate.interpretador,
        "var a = 5\nvar xs = [a, a + 1]",
    )
    assert interp.obtener_variable("xs") == [5, 6]
