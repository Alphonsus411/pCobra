from argparse import ArgumentParser
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
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


def test_set_oficial_documentado_en_tests():
    assert OFFICIAL_TARGETS == (
        "python",
        "rust",
        "javascript",
        "wasm",
        "go",
        "cpp",
        "java",
        "asm",
    )
