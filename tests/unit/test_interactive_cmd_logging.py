import logging
import types
from unittest.mock import Mock, patch

from cobra.cli.commands.interactive_cmd import InteractiveCommand, format_user_error
from cobra.cli.i18n import _
from pcobra.core.errors import CondicionNoBooleanaError


def test_context_logging(caplog):
    dummy = types.SimpleNamespace()
    cmd = InteractiveCommand(dummy)
    with caplog.at_level(logging.DEBUG):
        with cmd:
            pass
    messages = [r.message for r in caplog.records]
    assert _("Iniciando REPL de Cobra") in messages
    assert _("Finalizando REPL de Cobra") in messages


def test_log_error_emits_debug_once(caplog):
    dummy = types.SimpleNamespace()
    cmd = InteractiveCommand(dummy)
    with caplog.at_level(logging.DEBUG):
        cmd._log_error(_("Error de prueba"), RuntimeError("fallo"))

    record = caplog.records[-1]
    assert "Error en REPL" in record.message
    assert _("Error de prueba") in record.message
    assert record.levelno == logging.DEBUG


def test_run_repl_loop_runtime_error_no_debug_no_imprime_traceback():
    dummy = types.SimpleNamespace()
    cmd = InteractiveCommand(dummy)
    cmd._debug_mode = False

    entradas = iter(["imprimir(1)", "salir"])

    def _leer_linea(_prompt):
        return next(entradas)

    with patch.object(
        cmd,
        "ejecutar_codigo",
        side_effect=CondicionNoBooleanaError(),
    ), patch.object(cmd, "_log_error") as mock_log_error:
        cmd._run_repl_loop(
            args=types.SimpleNamespace(),
            validador=None,
            leer_linea=_leer_linea,
            sandbox=False,
            sandbox_docker=None,
        )

    mock_log_error.assert_called_once()


def test_run_repl_loop_runtime_error_debug_si_imprime_traceback():
    dummy = types.SimpleNamespace()
    cmd = InteractiveCommand(dummy)
    cmd._debug_mode = True

    entradas = iter(["imprimir(1)", "salir"])

    def _leer_linea(_prompt):
        return next(entradas)

    with patch.object(
        cmd,
        "ejecutar_codigo",
        side_effect=CondicionNoBooleanaError(),
    ), patch.object(cmd, "_log_error") as mock_log_error:
        cmd._run_repl_loop(
            args=types.SimpleNamespace(),
            validador=None,
            leer_linea=_leer_linea,
            sandbox=False,
            sandbox_docker=None,
        )

    mock_log_error.assert_called_once()


def test_format_user_error_elimina_prefijos_duplicados():
    assert format_user_error(Exception("Error general: Error: fallo")) == "fallo"


def test_log_error_no_debug_solo_imprime_error_limpio():
    cmd = InteractiveCommand(types.SimpleNamespace())
    cmd._debug_mode = False
    mock_mostrar_error = Mock()
    globals_log_error = InteractiveCommand._log_error.__globals__

    with patch.dict(
        globals_log_error,
        {"mostrar_error": mock_mostrar_error},
    ):
        cmd._log_error(_("Error general"), Exception("Error general: Error: fallo"))

    mock_mostrar_error.assert_called_once_with("fallo", registrar_log=False)


def test_log_error_debug_muestra_traceback_en_logger():
    cmd = InteractiveCommand(types.SimpleNamespace())
    cmd._debug_mode = True
    cmd._estado_repl["debug_enabled"] = True
    mock_mostrar_error = Mock()
    mock_logger = Mock()
    globals_log_error = InteractiveCommand._log_error.__globals__
    mock_traceback = Mock(return_value="TRACEBACK")

    with patch.dict(
        globals_log_error,
        {
            "mostrar_error": mock_mostrar_error,
            "format_traceback": mock_traceback,
        },
    ):
        cmd.logger = mock_logger
        cmd._log_error(_("Error general"), CondicionNoBooleanaError())

    mock_traceback.assert_called_once()
    mock_mostrar_error.assert_called_once()
    assert mock_mostrar_error.call_args.kwargs == {"registrar_log": False}
    assert isinstance(mock_mostrar_error.call_args.args[0], str)
    mock_logger.debug.assert_any_call("TRACEBACK")
