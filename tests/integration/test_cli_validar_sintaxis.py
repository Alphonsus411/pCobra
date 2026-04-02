from __future__ import annotations

from cobra.cli.cli import main
from cobra.cli.commands.validar_sintaxis_cmd import ValidationResult
from cobra.cli.commands import validar_sintaxis_cmd as cmd_module


def test_cli_validar_sintaxis_exit_code_ok(monkeypatch):
    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))

    def _fake_run_transpilers(self, targets, strict):
        assert "python" in targets
        assert strict is False
        return {}, False

    monkeypatch.setattr(cmd_module.ValidarSintaxisCommand, "_run_transpilers_syntax", _fake_run_transpilers)

    rc = main(["validar-sintaxis", "--targets", "python"])

    assert rc == 0


def test_cli_validar_sintaxis_exit_code_error(monkeypatch):
    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("fail", "py fail"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))

    rc = main(["validar-sintaxis", "--solo-cobra"])

    assert rc == 1


def test_cli_validar_sintaxis_strict_con_toolchain_ausente(monkeypatch):
    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(cmd_module.shutil, "which", lambda _: None)

    rc = main(["validar-sintaxis", "--targets", "javascript", "--strict"])

    assert rc == 1
