from __future__ import annotations

from argparse import Namespace

from pcobra.cobra.cli.commands import validar_sintaxis_cmd as cmd_module
from pcobra.cobra.cli.commands.validar_sintaxis_cmd import (
    ValidationResult,
    ValidarSintaxisCommand,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _build_parser() -> CustomArgumentParser:
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    ValidarSintaxisCommand().register_subparser(subparsers)
    return parser


def test_parser_validar_sintaxis_acepta_perfiles_soportados():
    parser = _build_parser()
    for perfil in ("solo-cobra", "transpiladores", "completo"):
        args = parser.parse_args(["validar-sintaxis", "--perfil", perfil])
        assert args.perfil == perfil


def test_parser_validar_sintaxis_expone_alias_deprecado_solo_cobra():
    parser = _build_parser()
    args = parser.parse_args(["validar-sintaxis", "--solo-cobra"])

    assert args.solo_cobra is True
    assert args.perfil == "completo"


def test_run_prioriza_alias_deprecado_sobre_perfil(monkeypatch):
    command = ValidarSintaxisCommand()
    calls = {"python": 0, "cobra": 0, "transpilers": 0}
    monkeypatch.setattr(
        cmd_module,
        "_validate_python_syntax",
        lambda: calls.__setitem__("python", calls["python"] + 1) or ValidationResult("ok", "py"),
    )
    monkeypatch.setattr(
        cmd_module,
        "_validate_cobra_parse",
        lambda: calls.__setitem__("cobra", calls["cobra"] + 1) or ValidationResult("ok", "cobra"),
    )
    monkeypatch.setattr(
        command,
        "_run_transpilers_syntax",
        lambda *_: calls.__setitem__("transpilers", calls["transpilers"] + 1) or ({}, {}, False),
    )

    rc = command.run(Namespace(modo="mixto", strict=False, perfil="transpiladores", solo_cobra=True, targets="", report_json=None))

    assert rc == 0
    assert calls == {"python": 1, "cobra": 1, "transpilers": 0}
