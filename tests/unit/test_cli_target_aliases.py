from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _build_parser_with_command(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


def test_execute_parser_normaliza_alias_js_a_javascript_en_contenedor():
    parser = _build_parser_with_command(ExecuteCommand())

    args = parser.parse_args(["ejecutar", "script.co", "--contenedor", "js"])

    assert args.contenedor == "javascript"


def test_verify_parser_normaliza_alias_js_en_lista_de_lenguajes():
    parser = _build_parser_with_command(VerifyCommand())

    args = parser.parse_args(["verificar", "script.co", "--lenguajes", "python,js"])

    assert args.lenguajes == ["python", "javascript"]
