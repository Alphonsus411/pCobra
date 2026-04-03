from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from cobra.cli.commands.execute_cmd import ExecuteCommand
from cobra.cli.commands.interactive_cmd import InteractiveCommand
from core.interpreter import InterpretadorCobra



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



def test_repl_ejecuta_bloque_completo_sin_parseo_parcial_por_linea():
    inputs = ["si verdadero:", "imprimir(1)", "fin", "salir"]
    cmd = InteractiveCommand(MagicMock())

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), patch(
        "prompt_toolkit.PromptSession.prompt", side_effect=inputs
    ), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar_codigo:
        ret = cmd.run(_args_interactive())

    assert ret == 0
    mock_ejecutar_codigo.assert_called_once_with("si verdadero:\nimprimir(1)\nfin", None)
