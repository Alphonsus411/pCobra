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
    BEST_EFFORT_RUNTIME_TARGETS,
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser

FIRST_TRANSPILATION_ONLY = TRANSPILATION_ONLY_TARGETS[0] if TRANSPILATION_ONLY_TARGETS else None
FIRST_BEST_EFFORT = BEST_EFFORT_RUNTIME_TARGETS[0] if BEST_EFFORT_RUNTIME_TARGETS else None


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


runtime_error_cases = []
if FIRST_TRANSPILATION_ONLY:
    runtime_error_cases.extend(
        [
            (ExecuteCommand(), ["ejecutar", "archivo.co", "--contenedor", FIRST_TRANSPILATION_ONLY], DOCKER_EXECUTABLE_TARGETS, FIRST_TRANSPILATION_ONLY),
            (InteractiveCommand(MagicMock()), ["interactive", "--sandbox-docker", FIRST_TRANSPILATION_ONLY], DOCKER_EXECUTABLE_TARGETS, FIRST_TRANSPILATION_ONLY),
            (VerifyCommand(), ["verificar", "archivo.co", "--lenguajes", FIRST_TRANSPILATION_ONLY], VERIFICATION_EXECUTABLE_TARGETS, FIRST_TRANSPILATION_ONLY),
        ]
    )
if FIRST_BEST_EFFORT:
    runtime_error_cases.extend(
        [
            (ExecuteCommand(), ["ejecutar", "archivo.co", "--contenedor", FIRST_BEST_EFFORT], DOCKER_EXECUTABLE_TARGETS, FIRST_BEST_EFFORT),
            (InteractiveCommand(MagicMock()), ["interactive", "--sandbox-docker", FIRST_BEST_EFFORT], DOCKER_EXECUTABLE_TARGETS, FIRST_BEST_EFFORT),
            (VerifyCommand(), ["verificar", "archivo.co", "--lenguajes", FIRST_BEST_EFFORT], VERIFICATION_EXECUTABLE_TARGETS, FIRST_BEST_EFFORT),
        ]
    )


@pytest.mark.parametrize(("command", "argv", "supported_targets", "unsupported_target"), runtime_error_cases)
def test_errores_cli_aclran_cuando_un_target_no_tiene_runtime_oficial(command, argv, supported_targets, unsupported_target, caplog):
    parser, _ = _build_parser_for(command)

    with pytest.raises(SystemExit):
        parser.parse_args(argv)

    err = caplog.text
    assert unsupported_target in err
    assert "targets oficiales de salida" in err
    assert "Targets best-effort" in err
    assert "Targets solo de transpilación" in err
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

    help_text = " ".join(subparser.format_help().split())

    assert "runtime oficial" in help_text
    assert "best-effort" in help_text
    assert "solo de transpilación" in help_text
    for target in runtime_targets:
        assert target in help_text
    for target in BEST_EFFORT_RUNTIME_TARGETS:
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
    if not FIRST_TRANSPILATION_ONLY:
        pytest.skip("No hay targets oficiales solo de transpilación en la política pública actual")

    cmd = InteractiveCommand(MagicMock())
    args = SimpleNamespace(
        memory_limit=cmd.MEMORY_LIMIT_MB,
        ignore_memory_limit=False,
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=FIRST_TRANSPILATION_ONLY,
    )

    with pytest.MonkeyPatch.context() as mp:
        mensajes: list[str] = []
        mp.setattr("pcobra.cobra.cli.commands.interactive_cmd.limitar_memoria_mb", lambda *_: None)
        mp.setattr("pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias", lambda *_: None)
        mp.setattr("pcobra.cobra.cli.commands.interactive_cmd.mostrar_error", mensajes.append)
        ret = cmd.run(args)

    assert ret == 1
    assert mensajes
    assert "Targets best-effort" in mensajes[0]
    assert "Targets solo de transpilación" in mensajes[0]
    for target in DOCKER_EXECUTABLE_TARGETS:
        assert target in mensajes[0]
