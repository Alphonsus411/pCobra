from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from cobra.cli.commands import validar_sintaxis_cmd as cmd_module
from cobra.cli.commands.validar_sintaxis_cmd import (
    TargetSummary,
    ValidationResult,
    ValidarSintaxisCommand,
)


def _args(**kwargs) -> Namespace:
    base = {
        "modo": "mixto",
        "strict": False,
        "solo_cobra": False,
        "targets": "",
        "report_json": None,
    }
    base.update(kwargs)
    return Namespace(**base)


def test_validar_sintaxis_solo_cobra_ok(monkeypatch):
    command = ValidarSintaxisCommand()

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(
        command,
        "_run_transpilers_syntax",
        lambda *_: (_ for _ in ()).throw(AssertionError("No debe ejecutar transpiladores")),
    )

    rc = command.run(_args(solo_cobra=True))
    assert rc == 0


def test_validar_sintaxis_respeta_validar_politica_modo(monkeypatch):
    command = ValidarSintaxisCommand()
    mensajes: list[str] = []

    monkeypatch.setattr(cmd_module, "mostrar_error", lambda msg: mensajes.append(msg))
    monkeypatch.setattr(cmd_module, "validar_politica_modo", lambda *_: (_ for _ in ()).throw(ValueError("modo bloqueado")))

    rc = command.run(_args())

    assert rc == 1
    assert any("modo bloqueado" in msg for msg in mensajes)


def test_validar_sintaxis_strict_convierte_skipped_en_error(monkeypatch):
    command = ValidarSintaxisCommand()

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(
        command,
        "_run_transpilers_syntax",
        lambda *_: ({"javascript": TargetSummary(ok=0, fail=0, skipped=1)}, True),
    )

    rc = command.run(_args(strict=True, targets="javascript"))
    assert rc == 1


def test_validar_sintaxis_report_json_en_archivo(monkeypatch, tmp_path: Path):
    command = ValidarSintaxisCommand()
    output = tmp_path / "reporte.json"

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(command, "_run_transpilers_syntax", lambda *_: ({}, False))

    rc = command.run(_args(report_json=str(output)))

    assert rc == 0
    assert output.exists()
    contenido = output.read_text(encoding="utf-8")
    assert '"python"' in contenido
    assert '"cobra"' in contenido


def test_validator_javascript_skipped_sin_node(monkeypatch):
    monkeypatch.setattr(cmd_module.shutil, "which", lambda _: None)

    result = cmd_module._validate_javascript("let x = 1;")

    assert result.status == "skipped"
    assert "node" in result.message


def test_validator_rust_skipped_sin_rustc(monkeypatch):
    monkeypatch.setattr(cmd_module.shutil, "which", lambda _: None)

    result = cmd_module._validate_rust("fn main() {}")

    assert result.status == "skipped"
    assert "rustc" in result.message


@pytest.mark.parametrize("targets", ["javascript,go", "python"])
def test_parse_targets_validos(targets: str):
    command = ValidarSintaxisCommand()
    parsed = command._parse_targets(targets)
    assert parsed


def test_parse_targets_invalido():
    command = ValidarSintaxisCommand()
    with pytest.raises(ValueError):
        command._parse_targets("fantasy")
