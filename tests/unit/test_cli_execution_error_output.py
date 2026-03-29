import argparse
from unittest.mock import patch

from cobra.cli.cli import CliApplication


def test_handle_execution_error_normal_hides_traceback_and_keeps_logging_exception():
    app = CliApplication()
    exc = RuntimeError("boom")

    with patch("cobra.cli.cli.messages.mostrar_error") as mock_error, patch(
        "cobra.cli.cli.logging.exception"
    ) as mock_logging_exception, patch("cobra.cli.cli.print") as mock_print, patch(
        "cobra.cli.cli.format_traceback", return_value="TRACEBACK"
    ) as mock_format_traceback:
        result = app._handle_execution_error(exc, "es", debug_activo=False)

    assert result == 1
    assert mock_error.call_count == 1
    assert "--debug" in mock_error.call_args[0][0]
    mock_logging_exception.assert_called_once_with("Error in execution")
    mock_print.assert_not_called()
    mock_format_traceback.assert_not_called()


def test_handle_execution_error_debug_shows_traceback_and_keeps_logging_exception():
    app = CliApplication()
    exc = RuntimeError("boom")

    with patch("cobra.cli.cli.messages.mostrar_error") as mock_error, patch(
        "cobra.cli.cli.logging.exception"
    ) as mock_logging_exception, patch("cobra.cli.cli.print") as mock_print, patch(
        "cobra.cli.cli.format_traceback", return_value="TRACEBACK") as mock_format_traceback:
        result = app._handle_execution_error(exc, "es", debug_activo=True)

    assert result == 1
    assert mock_error.call_count == 1
    mock_logging_exception.assert_called_once_with("Error in execution")
    mock_format_traceback.assert_called_once_with(exc, "es")
    mock_print.assert_called_once_with("TRACEBACK")


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
