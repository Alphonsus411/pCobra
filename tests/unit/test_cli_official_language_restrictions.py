from argparse import ArgumentParser
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.registry import official_transpiler_targets
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

INVALID_LANGUAGES = ("backend_x", "backend_y", "backend_z")


def _build_parser_for(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


@pytest.mark.parametrize("language", INVALID_LANGUAGES)
def test_compile_falla_con_tipo_fuera_de_targets_oficiales(language):
    parser = _build_parser_for(CompileCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "archivo.co", "--tipo", language])


@pytest.mark.parametrize("language", INVALID_LANGUAGES)
def test_compile_falla_con_tipos_fuera_de_targets_oficiales(language):
    parser = _build_parser_for(CompileCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "archivo.co", "--tipos", f"python,{language}"])


@pytest.mark.parametrize("language", INVALID_LANGUAGES)
def test_interactive_falla_con_sandbox_docker_fuera_de_targets_oficiales(language):
    parser = _build_parser_for(InteractiveCommand(MagicMock()))

    with pytest.raises(SystemExit):
        parser.parse_args(["interactive", "--sandbox-docker", language])


@pytest.mark.parametrize("language", INVALID_LANGUAGES)
def test_transpilar_inverso_falla_con_destino_fuera_de_targets_oficiales(language):
    parser = _build_parser_for(TranspilarInversoCommand())

    with pytest.raises(SystemExit):
        parser.parse_args([
            "transpilar-inverso",
            "archivo.py",
            "--origen",
            "python",
            "--destino",
            language,
        ])


def test_transpilar_inverso_falla_con_origen_fuera_del_scope_reverse():
    parser = _build_parser_for(TranspilarInversoCommand())

    with pytest.raises(SystemExit):
        parser.parse_args([
            "transpilar-inverso",
            "archivo.py",
            "--origen",
            "js",
            "--destino",
            "python",
        ])


@pytest.mark.parametrize("language", INVALID_LANGUAGES)
def test_verify_rechaza_lenguajes_fuera_del_runtime_soportado(language):
    verify = VerifyCommand()

    with pytest.raises(ValueError) as exc_info:
        verify._validate_languages([language])

    assert language in str(exc_info.value)
    for runtime in verify.SUPPORTED_LANGUAGES:
        assert runtime in str(exc_info.value)


def test_set_oficial_documentado_en_tests_deriva_del_registro_canonico():
    assert OFFICIAL_TARGETS == official_transpiler_targets()
    assert tuple(LANG_CHOICES) == official_transpiler_targets()


def test_interactive_rechaza_targets_solo_transpilacion_en_parseo():
    parser = _build_parser_for(InteractiveCommand(MagicMock()))

    with pytest.raises(SystemExit):
        parser.parse_args(["interactive", "--sandbox-docker", TRANSPILATION_ONLY_TARGETS[0]])


def test_set_runtime_docker_documentado_en_tests():
    assert DOCKER_EXECUTABLE_TARGETS == ("python", "rust", "javascript", "cpp")


def test_verify_parseo_rechaza_targets_solo_transpilacion():
    parser = _build_parser_for(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "archivo.co", "--lenguajes", TRANSPILATION_ONLY_TARGETS[0]])


def test_compile_choices_siguen_alineados_con_targets_oficiales():
    parser = _build_parser_for(CompileCommand())
    compilar_parser = parser._subparsers._group_actions[0].choices["compilar"]

    backend_action = next(action for action in compilar_parser._actions if action.dest == "backend")
    tipo_action = next(action for action in compilar_parser._actions if action.dest == "tipo")

    assert tuple(LANG_CHOICES) == OFFICIAL_TARGETS
    assert tuple(backend_action.choices) == OFFICIAL_TARGETS
    assert tuple(tipo_action.choices) == OFFICIAL_TARGETS


def test_tests_documentan_las_tres_categorias_publicas_de_targets():
    assert OFFICIAL_TARGETS == official_transpiler_targets()
    assert OFFICIAL_RUNTIME_TARGETS == ("python", "rust", "javascript", "cpp")
    assert TRANSPILATION_ONLY_TARGETS == ("wasm", "go", "java", "asm")


def test_tests_documentan_best_effort_experimental_sin_aliases_publicos():
    runtime_experimental = tuple(
        target for target in TRANSPILATION_ONLY_TARGETS if target in {"go", "java"}
    )
    assert runtime_experimental == ("go", "java")
    assert "js" not in OFFICIAL_TARGETS
    assert "ensamblador" not in OFFICIAL_TARGETS
