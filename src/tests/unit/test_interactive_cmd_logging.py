import logging
import types

from cobra.cli.commands.interactive_cmd import InteractiveCommand
from cobra.cli.i18n import _


def test_context_logging(caplog):
    dummy = types.SimpleNamespace()
    cmd = InteractiveCommand(dummy)
    with caplog.at_level(logging.INFO):
        with cmd:
            pass
    messages = [r.message for r in caplog.records]
    assert _("Iniciando REPL de Cobra") in messages
    assert _("Finalizando REPL de Cobra") in messages


def test_log_error_emits_error(caplog):
    dummy = types.SimpleNamespace()
    cmd = InteractiveCommand(dummy)
    with caplog.at_level(logging.ERROR):
        cmd._log_error(_("Error de prueba"), RuntimeError("fallo"))
    record = caplog.records[-1]
    assert _("Error de prueba") in record.message
    assert record.levelno == logging.ERROR

