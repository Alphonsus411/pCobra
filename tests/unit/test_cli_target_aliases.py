import argparse

import pytest

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import parse_target, parse_target_list
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.registry import official_transpiler_targets

LEGACY_ALIASES = ("js", "ensamblador", "assembly", "c++")


def _build_parser_with_command(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


@pytest.mark.parametrize("alias", LEGACY_ALIASES)
def test_regresion_parse_target_rechaza_aliases_legacy(alias):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target(alias)


@pytest.mark.parametrize("alias", LEGACY_ALIASES)
def test_regresion_parse_target_list_rechaza_aliases_legacy(alias):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target_list(f"python,{alias}")


def test_regresion_execute_parser_rechaza_alias_js_en_contenedor():
    parser = _build_parser_with_command(ExecuteCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["ejecutar", "script.co", "--contenedor", "js"])


def test_regresion_verify_parser_rechaza_alias_js_en_lista_de_lenguajes():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,js"])


def test_regresion_verify_parser_rechaza_alias_ensamblador_en_lista_de_lenguajes():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,ensamblador"])


def test_la_whitelist_publica_sigue_si_aceptar_aliases():
    targets = official_transpiler_targets()
    assert "javascript" in targets
    for alias in LEGACY_ALIASES:
        assert alias not in targets
