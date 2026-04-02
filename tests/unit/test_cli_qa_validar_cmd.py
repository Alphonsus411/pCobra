from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from cobra.cli.commands import qa_validar_cmd as cmd_module
from cobra.cli.commands.qa_validar_cmd import QaValidarCommand
from cobra.cli.commands.validar_sintaxis_cmd import TargetSummary, ValidationResult


def _args(**kwargs) -> Namespace:
    base = {
        "modo": "mixto",
        "archivo": "programa.co",
        "strict": False,
        "solo_cobra": False,
        "targets": "",
        "scope": "all",
        "report_json": None,
    }
    base.update(kwargs)
    return Namespace(**base)


def test_qa_validar_exit_code_0_cuando_todo_ok(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(
        cmd_module.ValidarSintaxisCommand,
        "_run_transpilers_syntax",
        lambda *_: ({"python": TargetSummary(ok=1, fail=0, skipped=0)}, False),
    )
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 0)

    rc = command.run(_args(targets="python,javascript"))

    assert rc == 0


def test_qa_validar_exit_code_1_si_falla_runtime(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(cmd_module.ValidarSintaxisCommand, "_run_transpilers_syntax", lambda *_: ({}, False))
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 1)

    rc = command.run(_args(targets="python"))

    assert rc == 1


def test_qa_validar_propaga_errores_en_orquestacion(monkeypatch):
    command = QaValidarCommand()
    mensajes: list[str] = []

    monkeypatch.setattr(cmd_module, "mostrar_error", lambda msg: mensajes.append(msg))
    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(cmd_module.ValidarSintaxisCommand, "_run_transpilers_syntax", lambda *_: ({}, False))
    monkeypatch.setattr(
        cmd_module.VerifyCommand,
        "run",
        lambda *_: (_ for _ in ()).throw(RuntimeError("fallo runtime interno")),
    )

    rc = command.run(_args(targets="python"))

    assert rc == 1
    assert any("fallo runtime interno" in mensaje for mensaje in mensajes)


def test_qa_validar_strict_falla_si_no_hay_runtime_ejecutable(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(cmd_module.ValidarSintaxisCommand, "_run_transpilers_syntax", lambda *_: ({}, False))

    rc = command.run(_args(strict=True, targets="wasm", scope="runtime"))

    assert rc == 1


def test_qa_validar_no_strict_tambien_falla_si_no_hay_runtime_ejecutable(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(cmd_module.ValidarSintaxisCommand, "_run_transpilers_syntax", lambda *_: ({}, False))

    rc = command.run(_args(strict=False, targets="wasm", scope="runtime"))

    assert rc == 1


def test_qa_validar_reporte_json_agregado(monkeypatch, tmp_path: Path):
    command = QaValidarCommand()
    output = tmp_path / "qa.json"

    monkeypatch.setattr(cmd_module, "_validate_python_syntax", lambda: ValidationResult("ok", "py"))
    monkeypatch.setattr(cmd_module, "_validate_cobra_parse", lambda: ValidationResult("ok", "cobra"))
    monkeypatch.setattr(cmd_module.ValidarSintaxisCommand, "_run_transpilers_syntax", lambda *_: ({}, False))
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 0)

    rc = command.run(_args(targets="python", report_json=str(output)))

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert set(payload) == {"syntax", "transpilers", "runtime_equivalence"}
