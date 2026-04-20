from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.execution_pipeline import PipelineInput, ejecutar_pipeline_explicito
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.core.runtime import InterpretadorCobra


def _args_interactive():
    return SimpleNamespace(
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=None,
        memory_limit=1024,
        ignore_memory_limit=True,
        allow_insecure_fallback=False,
    )


def test_contrato_resultado_igual_entre_modo_archivo_y_interactivo():
    codigo = "x = 5\nimprimir(x)"

    cmd_execute = ExecuteCommand()
    with patch("sys.stdout", new_callable=StringIO) as out_file:
        result_file = cmd_execute._ejecutar_normal(codigo, seguro=False, extra_validators=None)

    cmd_interactive = InteractiveCommand(InterpretadorCobra())
    with patch("sys.stdout", new_callable=StringIO) as out_repl:
        cmd_interactive.ejecutar_codigo(codigo)

    assert result_file == 0
    assert out_file.getvalue() == out_repl.getvalue()


@pytest.mark.parametrize(
    ("caso", "codigo"),
    [
        (
            "mientras multilinea",
            "x = 0\nmientras falso:\n    imprimir(99)\nfin\nimprimir(x)",
        ),
        (
            "si_sino multilinea",
            "x = 2\nsi x < 1:\n    imprimir('menor')\nsino:\n    imprimir('mayor')\nfin",
        ),
        (
            "funcion con mutacion",
            "func incrementar(v):\n    retorno v + 1\nfin\nx = 1\nx = incrementar(x)\nimprimir(x)",
        ),
    ],
)
def test_contrato_salida_y_error_iguales_entre_execute_e_interactive(caso, codigo):
    cmd_execute = ExecuteCommand()
    out_execute, err_execute = StringIO(), StringIO()
    with redirect_stdout(out_execute), redirect_stderr(err_execute):
        rc_execute = cmd_execute._ejecutar_normal(codigo, seguro=False, extra_validators=None)

    cmd_interactive = InteractiveCommand(InterpretadorCobra())
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        cmd_interactive.ejecutar_codigo(codigo)

    assert rc_execute == 0, f"{caso}: execute devolvió código distinto de 0"
    assert out_execute.getvalue() == out_repl.getvalue(), f"{caso}: salida divergente"
    assert err_execute.getvalue() == err_repl.getvalue(), f"{caso}: error divergente"


def test_contrato_error_igual_entre_modo_archivo_y_interactivo():
    codigo_invalido = "si verdadero:\nimprimir(1)"

    cmd_execute = ExecuteCommand()
    cmd_interactive = InteractiveCommand(InterpretadorCobra())

    with pytest.raises(Exception) as err_execute:
        cmd_execute._analizar_codigo(codigo_invalido)

    with pytest.raises(Exception) as err_interactive:
        cmd_interactive.procesar_ast(codigo_invalido)

    assert type(err_execute.value) is type(err_interactive.value)
    assert str(err_execute.value) == str(err_interactive.value)


@pytest.mark.parametrize(
    ("codigo_invalido", "caso"),
    [
        ("si verdadero:\nimprimir(1)\nfin", "condicional válido con ':'"),
        ("si verdadero\nimprimir(1)\nfin", "condicional sin ':'"),
        ("si verdadero:\nimprimir(1)", "condicional sin 'fin'"),
    ],
)
def test_contrato_pipeline_error_y_mensaje_entre_no_interactivo_y_repl(
    codigo_invalido, caso
):
    cmd_execute = ExecuteCommand()
    cmd_interactive = InteractiveCommand(InterpretadorCobra())

    def _capturar_error_no_interactivo():
        try:
            cmd_execute._analizar_codigo(codigo_invalido)
            return None
        except Exception as exc:  # noqa: BLE001 - contrato explícito del test
            return exc

    def _capturar_error_repl():
        try:
            cmd_interactive.ejecutar_codigo(codigo_invalido)
            return None
        except Exception as exc:  # noqa: BLE001 - contrato explícito del test
            return exc

    err_execute = _capturar_error_no_interactivo()
    err_repl = _capturar_error_repl()

    assert type(err_execute) is type(err_repl), f"{caso}: tipo de error divergente"
    assert str(err_execute) == str(err_repl), f"{caso}: mensaje de error divergente"


def test_repl_ejecuta_bloque_completo_sin_parseo_parcial_por_linea():
    inputs = ["si verdadero:", "imprimir(1)", "fin", "salir"]
    cmd = InteractiveCommand(MagicMock())

    with patch("pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias"), patch(
        "prompt_toolkit.PromptSession.prompt", side_effect=inputs
    ), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar_codigo:
        ret = cmd.run(_args_interactive())

    assert ret == 0
    mock_ejecutar_codigo.assert_called_once_with("si verdadero:\nimprimir(1)\nfin", None)


def test_paridad_repl_script_mientras_con_mutacion_persistente_mismo_entorno():
    cmd_execute = ExecuteCommand()
    out_script, err_script = StringIO(), StringIO()
    codigo_script = (
        "var base = 0\n"
        "mientras falso:\n"
        "    pasar\n"
        "fin\n"
        "var acumulado = 42"
    )
    with redirect_stdout(out_script), redirect_stderr(err_script):
        rc_script = cmd_execute._ejecutar_normal(codigo_script, seguro=False, extra_validators=None)

    cmd_interactive = InteractiveCommand(InterpretadorCobra())
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        cmd_interactive.ejecutar_codigo(
            "var base = 0\nmientras falso:\n    pasar\nfin"
        )
        cmd_interactive.ejecutar_codigo("var acumulado = 42")

    assert rc_script == 0
    assert out_script.getvalue() == ""
    assert err_script.getvalue() == err_repl.getvalue() == ""
    assert cmd_interactive.interpretador.contextos[-1].get("base") == 0
    assert cmd_interactive.interpretador.contextos[-1].get("acumulado") == 42


def test_contrato_repl_igual_script_estado_final_con_bucles_y_asignaciones():
    codigo = (
        "var base = 0\n"
        "mientras falso:\n"
        "    pasar\n"
        "fin\n"
        "var acumulado = 42\n"
        "var ultimo = 42"
    )
    setup_script, _ = ejecutar_pipeline_explicito(
        PipelineInput(
            codigo=codigo,
            interpretador_cls=InterpretadorCobra,
            safe_mode=False,
            extra_validators=None,
        )
    )
    contexto_script = setup_script.interpretador.contextos[-1]

    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    repl.ejecutar_codigo(codigo)
    estado_repl = repl.interpretador.contextos[-1]

    assert estado_repl.values == contexto_script.values
    assert estado_repl.get("base") == 0
