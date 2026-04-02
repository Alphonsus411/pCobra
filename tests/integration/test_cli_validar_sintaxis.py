from __future__ import annotations

from cobra.cli.cli import main
from cobra.cli.commands import validar_sintaxis_cmd as cmd_module
from pcobra.cobra.cli.commands import validar_sintaxis_cmd as pcobra_cmd_module
from pcobra.cobra.qa.syntax_validation import SyntaxReport, SyntaxValidationExecution, ValidationResult


def _execution(*, has_failures: bool = False, profile: str = "completo") -> SyntaxValidationExecution:
    return SyntaxValidationExecution(
        report=SyntaxReport(
            python=ValidationResult("ok", "py"),
            cobra=ValidationResult("ok", "cobra"),
            targets={},
            strict=False,
            errors_by_target={},
        ),
        profile=profile,
        targets_requested=[] if profile == "solo-cobra" else ["python"],
        has_failures=has_failures,
    )


def test_cli_validar_sintaxis_exit_code_ok_y_propagacion_argumentos(monkeypatch):
    captured: dict[str, object] = {}

    def _fake_execute(**kwargs):
        captured.update(kwargs)
        return _execution(has_failures=False)

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", _fake_execute)
    monkeypatch.setattr(pcobra_cmd_module, "execute_syntax_validation", _fake_execute)

    rc = main(["--modo", "mixto", "validar-sintaxis", "--targets", "python", "--strict", "--perfil", "completo"])

    assert rc == 0
    assert captured["strict"] is True
    assert captured["targets_raw"] == "python"
    assert captured["profile"] == "completo"


def test_cli_validar_sintaxis_exit_code_error_cuando_hay_fallos(monkeypatch):
    monkeypatch.setattr(
        cmd_module,
        "execute_syntax_validation",
        lambda **_: _execution(has_failures=True, profile="completo"),
    )
    monkeypatch.setattr(
        pcobra_cmd_module,
        "execute_syntax_validation",
        lambda **_: _execution(has_failures=True, profile="completo"),
    )

    rc = main(["--modo", "mixto", "validar-sintaxis", "--targets", "python"])

    assert rc == 1


def test_cli_validar_sintaxis_solo_cobra_por_flag(monkeypatch):
    captured: dict[str, object] = {}

    def _fake_execute(**kwargs):
        captured.update(kwargs)
        return _execution(has_failures=False, profile="solo-cobra")

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", _fake_execute)
    monkeypatch.setattr(pcobra_cmd_module, "execute_syntax_validation", _fake_execute)
    monkeypatch.setattr(cmd_module, "validar_politica_modo", lambda *_, **__: None)
    monkeypatch.setattr(pcobra_cmd_module, "validar_politica_modo", lambda *_, **__: None)

    rc = main(["validar-sintaxis", "--solo-cobra", "--perfil", "transpiladores"])

    assert rc == 0
    assert captured["profile"] == "solo-cobra"
