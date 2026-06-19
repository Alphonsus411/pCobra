from argparse import _StoreAction
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import (
    DOCKER_EXECUTABLE_TARGETS,
    DOCKER_RUNTIME_TARGETS,
    InteractiveCommand,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


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


def test_sandbox_docker_help_deriva_de_targets_publicos_activos():
    _, interactive_parser, _ = _build_parser_and_command()

    help_text = interactive_parser.format_help()

    assert "{python,javascript,rust}" in help_text
    choices_fragment = help_text[help_text.index("{python,javascript,rust}"):]
    choices_fragment = choices_fragment.split("]", 1)[0]
    assert "python" in choices_fragment
    assert "javascript" in choices_fragment
    assert "rust" in choices_fragment
    for legacy_target in ("cpp", "go", "wasm", "asm"):
        assert legacy_target not in choices_fragment


@pytest.mark.parametrize("target", DOCKER_EXECUTABLE_TARGETS)
def test_parser_acepta_todos_los_targets_con_runtime_docker(target):
    parser, _, _ = _build_parser_and_command()

    args = parser.parse_args(["interactive", "--sandbox-docker", target])

    assert args.sandbox_docker == target


def test_runtime_docker_no_expone_targets_legacy_retirados():
    assert set(DOCKER_EXECUTABLE_TARGETS) == {"python", "javascript", "rust"}
    assert set(DOCKER_RUNTIME_TARGETS) == {"python", "javascript", "rust"}
    assert not set(DOCKER_EXECUTABLE_TARGETS) & {"cpp", "java", "go", "wasm", "asm"}
