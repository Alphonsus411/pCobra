from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from cobra.cli.commands import validar_sintaxis_cmd as cmd_module
from cobra.cli.commands.validar_sintaxis_cmd import ValidarSintaxisCommand
from pcobra.cobra.qa import syntax_validation as sv


def _args(**kwargs) -> Namespace:
    base = {
        "modo": "mixto",
        "strict": False,
        "solo_cobra": False,
        "targets": "",
        "perfil": "completo",
        "report_json": None,
    }
    base.update(kwargs)
    return Namespace(**base)


def _execution(*, has_failures: bool = False, profile: str = "completo") -> sv.SyntaxValidationExecution:
    return sv.SyntaxValidationExecution(
        report=sv.SyntaxReport(
            python=sv.ValidationResult("ok", "py"),
            cobra=sv.ValidationResult("ok", "cobra"),
            targets={"javascript": sv.TargetSummary(ok=1, fail=0, skipped=0)} if profile != "solo-cobra" else {},
            strict=False,
            errors_by_target={},
        ),
        profile=profile,
        targets_requested=[] if profile == "solo-cobra" else ["javascript"],
        has_failures=has_failures,
    )


def test_validar_sintaxis_solo_cobra_ok(monkeypatch):
    command = ValidarSintaxisCommand()
    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(profile="solo-cobra"))

    rc = command.run(_args(solo_cobra=True, perfil="transpiladores"))
    assert rc == 0


def test_validar_sintaxis_respeta_validar_politica_modo(monkeypatch):
    command = ValidarSintaxisCommand()
    mensajes: list[str] = []

    monkeypatch.setattr(cmd_module, "mostrar_error", lambda msg: mensajes.append(msg))
    monkeypatch.setattr(cmd_module, "validar_politica_modo", lambda *_, **__: (_ for _ in ()).throw(ValueError("modo bloqueado")))

    rc = command.run(_args())

    assert rc == 1
    assert any("modo bloqueado" in msg for msg in mensajes)


def test_validar_sintaxis_strict_convierte_error_en_exit_code_1(monkeypatch):
    command = ValidarSintaxisCommand()
    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(has_failures=True))

    rc = command.run(_args(strict=True, targets="javascript"))
    assert rc == 1


def test_validar_sintaxis_report_json_en_archivo(monkeypatch, tmp_path: Path):
    command = ValidarSintaxisCommand()
    output = tmp_path / "reporte.json"

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution())

    rc = command.run(_args(report_json=str(output)))

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == sv.SYNTAX_REPORT_SCHEMA_VERSION
    assert "python" in payload and "cobra" in payload


def test_validar_sintaxis_report_json_incluye_errors_by_target_si_existe(monkeypatch, tmp_path: Path):
    command = ValidarSintaxisCommand()
    output = tmp_path / "reporte.json"

    execution = _execution(has_failures=True)
    execution.report.errors_by_target = {"javascript": ['{"stage":"validator","error":"boom"}']}
    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: execution)

    rc = command.run(_args(report_json=str(output), targets="javascript"))

    assert rc == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["errors_by_target"]["javascript"]


@pytest.mark.parametrize("targets", ["javascript,go", "python"])
def test_parse_targets_validos(targets: str):
    command = ValidarSintaxisCommand()
    parsed = command._parse_targets(targets)
    assert parsed


def test_parse_targets_invalido():
    command = ValidarSintaxisCommand()
    with pytest.raises(ValueError):
        command._parse_targets("fantasy")
