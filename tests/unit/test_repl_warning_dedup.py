from io import StringIO
from unittest.mock import patch

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.cli.execution_pipeline import prevalidar_y_parsear_codigo


class _NodoDummy:
    def aceptar(self, validador):
        validador.calls.append((validador.verbose, validador.emitir_side_effects))


class _ValidadorDummy:
    def __init__(self) -> None:
        self.verbose = True
        self.emitir_side_effects = True
        self.calls = []


def test_analisis_silencioso_fuerza_emitir_side_effects_false_y_restauracion() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    validador = _ValidadorDummy()

    cmd._fijar_modo_repl("analysis")
    cmd._validar_ast_para_analisis([_NodoDummy()], validador)

    assert validador.calls == [(False, False)]
    assert validador.verbose is True
    assert validador.emitir_side_effects is True


def test_parsear_y_ejecutar_restaura_modo_y_sincroniza_interpretador() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    cmd._fijar_modo_repl("execution")
    modo_anterior_interpretador = cmd.interpretador.mode

    ast = prevalidar_y_parsear_codigo("1")
    with patch.object(cmd, "ejecutar_codigo") as mock_ejecutar:
        cmd.parsear_y_ejecutar_codigo_repl("1", prevalidar_fn=lambda _codigo: ast)

    mock_ejecutar.assert_called_once_with("1", None, ast_preparseado=ast)
    assert cmd.mode == "execution"
    assert cmd.interpretador.mode == modo_anterior_interpretador


def test_regresion_warning_test_1_se_emite_una_sola_vez() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    with patch("sys.stdout", new_callable=StringIO):
        cmd.ejecutar_codigo(
            """
func test(x):
    retorno x
fin
"""
        )

    with patch("sys.stdout", new_callable=StringIO), patch("logging.warning") as warning_mock:
        cmd.ejecutar_codigo("test(1)")

    assert warning_mock.call_count == 1
    assert warning_mock.call_args_list[0].args == ("Llamada a funcion: test",)
