from argparse import _StoreAction

from pcobra.cobra.cli.commands.transpilar_inverso_cmd import (
    DESTINO_CHOICES,
    TranspilarInversoCommand,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def _build_parser():
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    cmd = TranspilarInversoCommand()
    reverse_parser = cmd.register_subparser(subparsers)
    return parser, reverse_parser


def test_transpilar_inverso_destino_choices_usa_targets_oficiales():
    assert tuple(DESTINO_CHOICES) == OFFICIAL_TARGETS

    _, reverse_parser = _build_parser()
    action = next(
        a for a in reverse_parser._actions if isinstance(a, _StoreAction) and a.dest == "destino"
    )
    assert tuple(action.choices) == OFFICIAL_TARGETS


def test_transpilar_inverso_help_refleja_solo_nombres_canonicos():
    _, reverse_parser = _build_parser()
    help_text = reverse_parser.format_help()

    assert "Tier 1: python, javascript, rust." in help_text
    assert "Tier 2:" not in help_text
    assert "JavaScript (javascript)" not in help_text
    assert "Ensamblador (asm)" not in help_text
