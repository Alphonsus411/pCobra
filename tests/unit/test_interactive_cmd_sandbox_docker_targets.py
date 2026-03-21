from argparse import _StoreAction
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import (
    DOCKER_EXECUTABLE_TARGETS,
    DOCKER_RUNTIME_TARGETS,
    InteractiveCommand,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.target_policies import TRANSPILATION_ONLY_TARGETS


def _build_parser_and_command():
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    cmd = InteractiveCommand(MagicMock())
    interactive_parser = cmd.register_subparser(subparsers)
    return parser, interactive_parser, cmd


def test_sandbox_docker_choices_usa_solo_targets_con_runtime_docker():
    _, interactive_parser, _ = _build_parser_and_command()

    action = next(
        a
        for a in interactive_parser._actions
        if isinstance(a, _StoreAction) and a.dest == "sandbox_docker"
    )

    assert tuple(action.choices) == DOCKER_EXECUTABLE_TARGETS


def test_sandbox_docker_help_deriva_de_targets_canonicos():
    _, interactive_parser, _ = _build_parser_and_command()

    help_text = interactive_parser.format_help()

    assert "Python (python)" in help_text
    assert "Rust (rust)" in help_text
    assert "C++ (cpp)" in help_text
    assert "Java (java)" not in help_text


@pytest.mark.parametrize("target", DOCKER_EXECUTABLE_TARGETS)
def test_parser_acepta_todos_los_targets_con_runtime_docker(target):
    parser, _, _ = _build_parser_and_command()

    args = parser.parse_args(["interactive", "--sandbox-docker", target])

    assert args.sandbox_docker == target


def test_runtime_docker_rechaza_target_oficial_no_ejecutable_en_contenedor():
    _, _, cmd = _build_parser_and_command()
    target_no_runtime = TRANSPILATION_ONLY_TARGETS[0]
    args = SimpleNamespace(
        memory_limit=cmd.MEMORY_LIMIT_MB,
        ignore_memory_limit=False,
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=target_no_runtime,
    )

    with patch("pcobra.cobra.cli.commands.interactive_cmd.limitar_memoria_mb"), patch(
        "pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias"
    ), patch("pcobra.cobra.cli.commands.interactive_cmd.mostrar_error") as mock_error:
        ret = cmd.run(args)

    assert ret == 1
    assert mock_error.call_count == 1
    msg = mock_error.call_args.args[0]
    assert target_no_runtime in msg
    for runtime_target in DOCKER_EXECUTABLE_TARGETS:
        assert runtime_target in msg
