from types import SimpleNamespace
from importlib import import_module

import pytest

from pcobra.cobra.qa import syntax_validation as validation
from scripts import smoke_transpilers_syntax as smoke


@pytest.mark.parametrize("fails", [False, True])
def test_smoke_preserva_estado_y_muestra_solo_diagnosticos_de_fallo(
    monkeypatch, capsys, fails
):
    registry = import_module("pcobra.cobra.transpilers.registry")
    syntax_validation = import_module("pcobra.cobra.qa.syntax_validation")
    events = [
        {"target": "rust", "fixture": "ok.cobra", "status": "ok", "message": "ok"},
        {
            "target": "rust",
            "fixture": "fallo.cobra",
            "status": "fail",
            "message": "rustc: error de prueba",
        },
    ]
    result = SimpleNamespace(
        has_failures=fails,
        events=events if fails else events[:1],
        report=SimpleNamespace(
            targets={"rust": SimpleNamespace(ok=1, fail=int(fails), skipped=0)}
        ),
    )
    monkeypatch.setattr(registry, "official_transpiler_targets", lambda: ("rust",))
    monkeypatch.setattr(
        registry, "build_official_transpilers", lambda: {"rust": object}
    )
    monkeypatch.setattr(
        syntax_validation, "execute_syntax_validation", lambda **_: result
    )

    assert smoke.main() == int(fails)
    out = capsys.readouterr().out
    assert ("rust | fallo.cobra: rustc: error de prueba" in out) is fails
    assert "rust | ok.cobra:" not in out


def test_execute_conserva_eventos_de_validacion(monkeypatch, tmp_path):
    fixture = tmp_path / "programa.cobra"
    fixture.write_text("dato", encoding="utf-8")
    event = {
        "target": "rust",
        "fixture": str(fixture),
        "status": "fail",
        "message": "timeout",
    }
    report = validation.SyntaxReport(
        python=validation.ValidationResult("skipped", ""),
        cobra=validation.ValidationResult("skipped", ""),
        targets={"rust": validation.TargetSummary(fail=1)},
        errors_by_target={"rust": ["timeout"]},
    )
    monkeypatch.setattr(validation, "TRANSPILER_FIXTURES", [fixture])
    monkeypatch.setattr(
        validation,
        "run_transpiler_syntax_validation",
        lambda **_: (report, [event], True),
    )
    execution = validation.execute_syntax_validation(
        profile="transpiladores", targets_raw="rust", strict=False, transpilers={}
    )
    assert execution.has_failures
    assert execution.events == [event]
    assert execution.report.errors_by_target == {"rust": ["timeout"]}
