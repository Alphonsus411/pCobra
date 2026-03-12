from argparse import _StoreAction

from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES, CompileCommand
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _build_parser():
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    cmd = CompileCommand()
    compile_parser = cmd.register_subparser(subparsers)
    return parser, compile_parser


def test_compile_tipo_choices_usa_lang_choices_centrales():
    _, compile_parser = _build_parser()
    action = next(
        a for a in compile_parser._actions if isinstance(a, _StoreAction) and a.dest == "tipo"
    )

    assert tuple(action.choices) == tuple(LANG_CHOICES)


def test_compile_parser_normaliza_alias_js_en_tipo_y_tipos():
    parser, _ = _build_parser()

    args = parser.parse_args(["compilar", "input.co", "--tipo", "js", "--tipos", "python,js"])

    assert args.tipo == "javascript"
    assert args.tipos == ["python", "javascript"]
