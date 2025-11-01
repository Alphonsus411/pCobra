import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from pcobra.cobra.cli.commands.interactive_cmd import (
    InteractiveCommand,
    NoConsoleScreenBufferError,
    DummyOutput,
)


class _FakeInterpreter:
    def ejecutar_ast(self, ast):
        pass


def test_interactive_cmd_without_console(monkeypatch, capsys):
    cmd = InteractiveCommand(_FakeInterpreter())

    # Evitar efectos secundarios
    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.limitar_memoria_mb",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias",
        lambda *a, **k: None,
    )

    class DummyPrompt:
        calls = 0
        last_output = None

        def __init__(self, *args, **kwargs):
            DummyPrompt.calls += 1
            DummyPrompt.last_output = kwargs.get("output")
            if DummyPrompt.calls == 1:
                raise NoConsoleScreenBufferError()

        def prompt(self, *args, **kwargs):
            raise EOFError

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.PromptSession", DummyPrompt
    )

    args = argparse.Namespace(
        memory_limit=InteractiveCommand.MEMORY_LIMIT_MB,
        ignore_memory_limit=False,
        sandbox=False,
        sandbox_docker=None,
        seguro=False,
        extra_validators=None,
    )

    result = cmd.run(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "Entorno sin consola compatible" in captured.out
    assert DummyPrompt.calls == 2
    assert isinstance(DummyPrompt.last_output, DummyOutput)
