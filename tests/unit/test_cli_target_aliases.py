import argparse

import pytest

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import parse_target, parse_target_list
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _build_parser_with_command(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


def test_execute_parser_rechaza_alias_js_en_contenedor():
    parser = _build_parser_with_command(ExecuteCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["ejecutar", "script.co", "--contenedor", "js"])


def test_verify_parser_rechaza_alias_js_en_lista_de_lenguajes():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,js"])


def test_parse_target_rechaza_alias_js_como_nombre_simple():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target("js")


def test_parse_target_list_rechaza_alias_js_dentro_de_lista():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target_list("python,js")


def test_verify_parser_rechaza_alias_ensamblador_en_lista_de_lenguajes():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,ensamblador"])
