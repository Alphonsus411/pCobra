import pytest

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _build_parser_with_command(command):
    parser = CustomArgumentParser(prog="cobra")
    parser.add_argument("--allow-legacy-target-aliases", action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


def test_execute_parser_rechaza_alias_js_en_contenedor_por_defecto():
    parser = _build_parser_with_command(ExecuteCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["ejecutar", "script.co", "--contenedor", "js"])


def test_verify_parser_rechaza_alias_js_en_lista_de_lenguajes_por_defecto():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,js"])


def test_verify_parser_rechaza_alias_ensamblador_en_lista_de_lenguajes_por_defecto():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,ensamblador"])
