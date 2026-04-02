from __future__ import annotations

from argparse import Namespace

from pcobra.cobra.cli.commands import validar_sintaxis_cmd as cmd_module
from pcobra.cobra.cli.commands.validar_sintaxis_cmd import ValidarSintaxisCommand
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.qa.syntax_validation import SyntaxReport, SyntaxValidationExecution, ValidationResult


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
    captured: dict[str, str] = {}

    def _fake_execute(**kwargs):
        captured["profile"] = kwargs["profile"]
        return SyntaxValidationExecution(
            report=SyntaxReport(
                python=ValidationResult("ok", "py"),
                cobra=ValidationResult("ok", "cobra"),
                targets={},
                strict=False,
                errors_by_target={},
            ),
            profile="solo-cobra",
            targets_requested=[],
            has_failures=False,
        )

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", _fake_execute)

    rc = command.run(Namespace(modo="mixto", strict=False, perfil="transpiladores", solo_cobra=True, targets="", report_json=None))

    assert rc == 0
    assert captured["profile"] == "solo-cobra"
