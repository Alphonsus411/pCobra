from __future__ import annotations

from argparse import _StoreAction
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _build_parser_for(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    subparser = command.register_subparser(subparsers)
    return parser, subparser


@pytest.mark.parametrize("target", OFFICIAL_TRANSPILATION_TARGETS)
def test_compilar_acepta_los_8_targets_oficiales_en_tipo(target):
    parser, _ = _build_parser_for(CompileCommand())

    args = parser.parse_args(["compilar", "archivo.co", "--tipo", target])

    assert args.tipo == target


def test_compilar_acepta_los_8_targets_oficiales_en_tipos():
    parser, _ = _build_parser_for(CompileCommand())

    args = parser.parse_args(
        ["compilar", "archivo.co", "--tipos", ",".join(OFFICIAL_TRANSPILATION_TARGETS)]
    )

    assert args.tipos == list(OFFICIAL_TRANSPILATION_TARGETS)


@pytest.mark.parametrize(
    ("command", "flag", "supported_targets"),
    [
        (ExecuteCommand(), "--contenedor", DOCKER_EXECUTABLE_TARGETS),
        (InteractiveCommand(MagicMock()), "--sandbox-docker", DOCKER_EXECUTABLE_TARGETS),
    ],
)
def test_execute_e_interactive_aceptan_solo_targets_runtime(command, flag, supported_targets):
    parser, _ = _build_parser_for(command)

    for target in supported_targets:
        args = parser.parse_args([command.name, flag, target, *(["archivo.co"] if command.name == "ejecutar" else [])])
        attr = "contenedor" if flag == "--contenedor" else "sandbox_docker"
        assert getattr(args, attr) == target


@pytest.mark.parametrize(
    ("command", "argv", "supported_targets", "unsupported_target"),
    [
        (ExecuteCommand(), ["ejecutar", "archivo.co", "--contenedor", TRANSPILATION_ONLY_TARGETS[0]], DOCKER_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS[0]),
        (InteractiveCommand(MagicMock()), ["interactive", "--sandbox-docker", TRANSPILATION_ONLY_TARGETS[0]], DOCKER_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS[0]),
        (VerifyCommand(), ["verificar", "archivo.co", "--lenguajes", TRANSPILATION_ONLY_TARGETS[0]], VERIFICATION_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS[0]),
    ],
)
def test_errores_cli_aclran_cuando_un_target_es_solo_transpilacion(command, argv, supported_targets, unsupported_target, caplog):
    parser, _ = _build_parser_for(command)

    with pytest.raises(SystemExit):
        parser.parse_args(argv)

    err = caplog.text
    assert unsupported_target in err
    assert "solo transpilación" in err
    assert "oficiales para transpilación" in err
    for target in supported_targets:
        assert target in err


@pytest.mark.parametrize(
    ("command", "runtime_targets", "transpilation_only_targets"),
    [
        (ExecuteCommand(), DOCKER_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS),
        (InteractiveCommand(MagicMock()), DOCKER_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS),
        (VerifyCommand(), VERIFICATION_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS),
    ],
)
def test_ayuda_cli_distingue_runtime_oficial_de_targets_solo_transpilacion(
    command,
    runtime_targets,
    transpilation_only_targets,
):
    _, subparser = _build_parser_for(command)

    help_text = subparser.format_help()

    assert "runtime oficial" in help_text
    assert "solo transpilación" in help_text
    for target in runtime_targets:
        assert target in help_text
    for target in transpilation_only_targets:
        assert target in help_text


def test_verify_parser_documenta_solo_runtimes_ejecutables_en_la_opcion_lenguajes():
    _, verify_parser = _build_parser_for(VerifyCommand())

    action = next(
        action
        for action in verify_parser._actions
        if isinstance(action, _StoreAction) and action.dest == "lenguajes"
    )

    assert action.required is True
    parsed = action.type("python,javascript")
    assert parsed == ["python", "javascript"]


def test_interactive_run_mantiene_error_centralizado_para_target_invalido_runtime():
    cmd = InteractiveCommand(MagicMock())
    args = SimpleNamespace(
        memory_limit=cmd.MEMORY_LIMIT_MB,
        ignore_memory_limit=False,
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=TRANSPILATION_ONLY_TARGETS[0],
    )

    with pytest.MonkeyPatch.context() as mp:
        mensajes: list[str] = []
        mp.setattr("pcobra.cobra.cli.commands.interactive_cmd.limitar_memoria_mb", lambda *_: None)
        mp.setattr("pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias", lambda *_: None)
        mp.setattr("pcobra.cobra.cli.commands.interactive_cmd.mostrar_error", mensajes.append)
        ret = cmd.run(args)

    assert ret == 1
    assert mensajes
    assert "solo transpilación" in mensajes[0]
    for target in DOCKER_EXECUTABLE_TARGETS:
        assert target in mensajes[0]
