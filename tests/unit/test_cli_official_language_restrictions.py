from argparse import ArgumentParser, ArgumentTypeError
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, get_lang_choices
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import (
    BEST_EFFORT_RUNTIME_TARGETS,
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    legacy_or_ambiguous_target_error,
    parse_target,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.registry import official_transpiler_targets
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

INVALID_LANGUAGES = ("backend_x", "backend_y", "backend_z")
EXPECTED_CANONICAL_TARGETS = ("python", "javascript", "rust")


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
            "fantasy",
            "--destino",
            "python",
        ])


@pytest.mark.parametrize("language", INVALID_LANGUAGES)
def test_verify_rechaza_lenguajes_fuera_del_runtime_soportado(language):
    parser = _build_parser_for(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "archivo.co", "--lenguajes", language])


def test_set_oficial_documentado_en_tests_deriva_del_registro_canonico():
    assert OFFICIAL_TARGETS == EXPECTED_CANONICAL_TARGETS
    assert OFFICIAL_TARGETS == official_transpiler_targets()
    assert tuple(get_lang_choices()) == official_transpiler_targets()


def test_no_hay_targets_solo_transpilacion_en_superficie_publica():
    assert TRANSPILATION_ONLY_TARGETS == ()


def test_set_runtime_docker_documentado_en_tests():
    assert DOCKER_EXECUTABLE_TARGETS == EXPECTED_CANONICAL_TARGETS


def test_verify_no_expone_targets_solo_transpilacion():
    assert TRANSPILATION_ONLY_TARGETS == ()


def test_compile_choices_siguen_alineados_con_targets_oficiales():
    parser = _build_parser_for(CompileCommand())
    compilar_parser = parser._subparsers._group_actions[0].choices["compilar"]

    backend_action = next(action for action in compilar_parser._actions if action.dest == "backend")
    tipo_action = next(action for action in compilar_parser._actions if action.dest == "tipo")

    assert tuple(get_lang_choices()) == EXPECTED_CANONICAL_TARGETS
    assert tuple(backend_action.choices) == EXPECTED_CANONICAL_TARGETS
    assert tuple(tipo_action.choices) == EXPECTED_CANONICAL_TARGETS


def test_tests_documentan_las_tres_categorias_publicas_de_targets():
    assert OFFICIAL_TARGETS == EXPECTED_CANONICAL_TARGETS
    assert OFFICIAL_TARGETS == official_transpiler_targets()
    assert OFFICIAL_RUNTIME_TARGETS == EXPECTED_CANONICAL_TARGETS
    assert BEST_EFFORT_RUNTIME_TARGETS == ()
    assert TRANSPILATION_ONLY_TARGETS == ()


def test_no_hay_best_effort_experimental_en_set_publico():
    assert BEST_EFFORT_RUNTIME_TARGETS == ()
    assert len(OFFICIAL_TARGETS) == 3


LEGACY_ALIASES_RECHAZADOS = (
    "assembly",
    "js",
    "c",
    "cxx",
    "cpp11",
    "cpp17",
    "asm64",
    "assembler",
    "node",
    "nodejs",
    "py",
    "python3",
    "golang",
    "jvm",
)


@pytest.mark.parametrize("legacy_alias", LEGACY_ALIASES_RECHAZADOS)
def test_compile_rechaza_cada_alias_legacy_con_mensaje_uniforme(legacy_alias):
    parser = _build_parser_for(CompileCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "archivo.co", "--tipo", legacy_alias])


@pytest.mark.parametrize("legacy_alias", LEGACY_ALIASES_RECHAZADOS)
def test_interactive_rechaza_cada_alias_legacy_con_mensaje_uniforme(legacy_alias):
    parser = _build_parser_for(InteractiveCommand(MagicMock()))

    with pytest.raises(SystemExit):
        parser.parse_args(["interactive", "--sandbox-docker", legacy_alias])


@pytest.mark.parametrize("legacy_alias", LEGACY_ALIASES_RECHAZADOS)
def test_transpilar_inverso_rechaza_cada_alias_legacy_con_mensaje_uniforme(legacy_alias):
    parser = _build_parser_for(TranspilarInversoCommand())

    with pytest.raises(SystemExit):
        parser.parse_args([
            "transpilar-inverso",
            "archivo.py",
            "--origen",
            "python",
            "--destino",
            legacy_alias,
        ])


@pytest.mark.parametrize("legacy_alias", LEGACY_ALIASES_RECHAZADOS)
def test_verify_rechaza_cada_alias_legacy_con_mensaje_uniforme(legacy_alias):
    parser = _build_parser_for(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "archivo.co", "--lenguajes", legacy_alias])


@pytest.mark.parametrize("legacy_alias", LEGACY_ALIASES_RECHAZADOS)
def test_parse_target_usa_mensaje_uniforme_para_alias_legacy(legacy_alias):
    with pytest.raises(ArgumentTypeError) as exc_info:
        parse_target(legacy_alias)

    message = str(exc_info.value)
    assert legacy_alias in message
    assert (
        "Target no permitido por nombre legacy/ambiguo" in message
        or "Target no soportado" in message
    )
    if "Target no permitido por nombre legacy/ambiguo" in message:
        assert message == legacy_or_ambiguous_target_error(legacy_alias)
