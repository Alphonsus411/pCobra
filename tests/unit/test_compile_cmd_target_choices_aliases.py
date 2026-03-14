from argparse import _StoreAction

from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES, CompileCommand
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


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


def test_compile_parser_normaliza_aliases_js_y_ensamblador_en_tipo_y_tipos():
    parser, _ = _build_parser()

    args = parser.parse_args(["compilar", "input.co", "--tipo", "ensamblador", "--tipos", "python,js,ensamblador"])

    assert args.tipo == "asm"
    assert args.tipos == ["python", "javascript", "asm"]


def test_compile_help_refleja_labels_amigables_y_nombres_canonicos():
    _, compile_parser = _build_parser()
    help_text = compile_parser.format_help()

    assert "JavaScript (javascript; alias: js)" in help_text
    assert "Ensamblador (asm; alias: ensamblador)" in help_text
    for target in OFFICIAL_TARGETS:
        assert target in help_text
