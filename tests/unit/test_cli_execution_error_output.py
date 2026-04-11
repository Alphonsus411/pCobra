import argparse
import logging
from unittest.mock import patch

from cobra.cli.cli import CliApplication


def test_handle_execution_error_normal_hides_traceback_and_keeps_logging_exception():
    app = CliApplication()
    exc = RuntimeError("boom")

    with patch("cobra.cli.cli.messages.mostrar_error") as mock_error, patch(
        "cobra.cli.cli.logging.error"
    ) as mock_logging_error, patch("cobra.cli.cli.print") as mock_print, patch(
        "cobra.cli.cli.format_traceback", return_value="TRACEBACK"
    ) as mock_format_traceback:
        result = app._handle_execution_error(exc, "es", debug_activo=False)

    assert result == 1
    assert mock_error.call_count == 1
    assert mock_error.call_args[0][0] == "boom"
    mock_logging_error.assert_called_once_with("Error in execution: %s", "boom")
    mock_print.assert_not_called()
    mock_format_traceback.assert_not_called()


def test_handle_execution_error_no_duplica_salida_si_ya_fue_mostrada():
    app = CliApplication()
    exc = RuntimeError("boom")
    setattr(exc, "error_ya_mostrado", True)

    with patch("cobra.cli.cli.messages.mostrar_error") as mock_error, patch(
        "cobra.cli.cli.logging.error"
    ) as mock_logging_error, patch("cobra.cli.cli.print") as mock_print:
        result = app._handle_execution_error(exc, "es", debug_activo=False)

    assert result == 1
    mock_error.assert_not_called()
    mock_logging_error.assert_called_once_with("Error in execution: %s", "boom")
    mock_print.assert_not_called()


def test_handle_execution_error_debug_envia_traceback_a_logger_debug():
    app = CliApplication()
    exc = RuntimeError("boom")

    with patch("cobra.cli.cli.messages.mostrar_error") as mock_error, patch(
        "cobra.cli.cli.logging.exception"
    ) as mock_logging_exception, patch(
        "cobra.cli.cli.logging.getLogger"
    ) as mock_get_logger, patch(
        "cobra.cli.cli.format_traceback", return_value="TRACEBACK") as mock_format_traceback:
        result = app._handle_execution_error(exc, "es", debug_activo=True)

    assert result == 1
    assert mock_error.call_count == 1
    mock_logging_exception.assert_called_once_with("Error in execution")
    mock_format_traceback.assert_called_once_with(exc, "es")
    mock_get_logger.return_value.debug.assert_called_once_with("TRACEBACK")


def test_handle_execution_error_con_root_logger_configurado_no_duplica_salida():
    app = CliApplication()
    exc = RuntimeError("boom")

    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    root_logger.handlers = []
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(logging.StreamHandler())

    try:
        with patch("cobra.cli.cli.messages.mostrar_error") as mock_error, patch(
            "cobra.cli.cli.logging.error"
        ) as mock_logging_error, patch("cobra.cli.cli.print") as mock_print:
            result = app._handle_execution_error(exc, "es", debug_activo=False)
    finally:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)

    assert result == 1
    mock_error.assert_called_once_with("boom", registrar_log=False)
    mock_logging_error.assert_called_once_with("Error in execution: %s", "boom")
    mock_print.assert_not_called()


def test_run_propaga_debug_activo_hacia_execute_command():
    app = CliApplication()
    args = argparse.Namespace(
        verbose=1,
        debug=False,
        lang="es",
        no_color=False,
        legacy_imports=False,
        cmd=None,
    )

    with patch.object(app, "initialize"), patch.object(app, "_parse_arguments", return_value=args), patch.object(
        app, "execute_command", return_value=0
    ) as mock_execute_command, patch("cobra.cli.cli.messages.mostrar_logo"), patch(
        "cobra.cli.cli.messages.disable_colors"
    ), patch("cobra.cli.cli.setup_gettext"):
        result = app.run([])

    assert result == 0
    mock_execute_command.assert_called_once_with(args, debug_activo=True)


def test_run_bloquea_fallback_inseguro_en_ci_sin_override(monkeypatch):
    app = CliApplication()
    args = argparse.Namespace(
        verbose=0,
        debug=False,
        lang="es",
        no_color=False,
        legacy_imports=False,
        cmd=argparse.Namespace(name="ejecutar"),
        seguro=True,
        allow_insecure_fallback=True,
        allow_insecure_non_interactive=False,
    )
    monkeypatch.setenv("CI", "1")

    with patch.object(app, "initialize"), patch.object(app, "_parse_arguments", return_value=args), patch.object(
        app, "execute_command", return_value=0
    ) as mock_execute_command, patch("cobra.cli.cli.messages.mostrar_logo"), patch(
        "cobra.cli.cli.messages.disable_colors"
    ), patch("cobra.cli.cli.setup_gettext"), patch("cobra.cli.cli.messages.mostrar_advertencia"), patch(
        "cobra.cli.cli.messages.mostrar_error"
    ) as mock_error:
        result = app.run([])

    assert result == 1
    mock_execute_command.assert_not_called()
    assert "CI/no interactivo" in mock_error.call_args[0][0]


def test_run_permite_override_explicito_en_ci_y_muestra_mensaje(monkeypatch):
    app = CliApplication()
    args = argparse.Namespace(
        verbose=0,
        debug=False,
        lang="es",
        no_color=False,
        legacy_imports=False,
        cmd=argparse.Namespace(name="ejecutar"),
        seguro=True,
        allow_insecure_fallback=True,
        allow_insecure_non_interactive=True,
    )
    monkeypatch.setenv("CI", "1")

    with patch.object(app, "initialize"), patch.object(app, "_parse_arguments", return_value=args), patch.object(
        app, "execute_command", return_value=0
    ) as mock_execute_command, patch("cobra.cli.cli.messages.mostrar_logo"), patch(
        "cobra.cli.cli.messages.disable_colors"
    ), patch("cobra.cli.cli.setup_gettext"), patch(
        "cobra.cli.cli.messages.mostrar_advertencia"
    ) as mock_warning:
        result = app.run([])

    assert result == 0
    mock_execute_command.assert_called_once_with(args, debug_activo=False)
    assert any(
        "Override explícito activo" in call.args[0]
        for call in mock_warning.call_args_list
    )


def test_registrar_advertencia_seguridad_emite_msg_estructurado():
    app = CliApplication()
    with patch("cobra.cli.cli.logging.getLogger") as mock_get_logger:
        logger = mock_get_logger.return_value
        app._registrar_advertencia_seguridad(
            event="unsafe_mode",
            command_name="ejecutar",
            reason="safe_mode_disabled",
            audit_id="SEC-RUNTIME-002",
        )

    warning_args = logger.warning.call_args.kwargs
    assert "event=unsafe_mode" in logger.warning.call_args.args[0]
    assert "command=ejecutar" in logger.warning.call_args.args[0]
    assert "reason=safe_mode_disabled" in logger.warning.call_args.args[0]
    assert "audit_id=SEC-RUNTIME-002" in logger.warning.call_args.args[0]
    assert warning_args["extra"]["audit_id"] == "SEC-RUNTIME-002"


def test_enforce_runtime_safety_policy_audita_rama_critica_sin_fallback():
    app = CliApplication()
    args = argparse.Namespace(
        cmd=argparse.Namespace(name="ejecutar"),
        seguro=True,
        allow_insecure_fallback=False,
        allow_insecure_non_interactive=True,
    )
    with patch.object(app, "_registrar_advertencia_seguridad") as mock_audit:
        try:
            app._enforce_runtime_safety_policy(args)
        except RuntimeError:
            pass

    mock_audit.assert_called_once_with(
        event="invalid_non_interactive_override",
        command_name="ejecutar",
        reason="non_interactive_override_without_fallback",
        audit_id="SEC-RUNTIME-001",
    )
