from pathlib import Path

import pytest

from pcobra.cobra.qa import syntax_validation as sv


class _LexerTokenizar:
    def tokenizar(self):
        return ["ok"]


class _LexerAnalizar:
    def analizar_token(self):
        return ["ok2"]


def test_tokenize_usa_tokenizar_si_esta_disponible():
    assert sv._tokenize(_LexerTokenizar()) == ["ok"]


def test_tokenize_usa_analizar_token_como_fallback():
    assert sv._tokenize(_LexerAnalizar()) == ["ok2"]


def test_tokenize_falla_si_no_hay_metodos_esperados():
    with pytest.raises(AttributeError):
        sv._tokenize(object())


def test_run_external_command_ok():
    ok, output = sv.run_external_command(["python", "-c", "print('hola')"])
    assert ok is True
    assert output == ""


def test_run_external_command_fail():
    ok, output = sv.run_external_command(["python", "-c", "import sys; sys.stderr.write('boom'); sys.exit(2)"])
    assert ok is False
    assert "boom" in output


def test_validator_asm_detecta_tokens_no_resueltos():
    result = sv.VALIDATORS["asm"]("<pendiente>\nMOV R1, 3")
    assert result.status == "fail"
    assert "no resueltos" in result.message


def test_run_transpiler_syntax_validation_resumen_ok_y_fail(monkeypatch):
    monkeypatch.setattr(sv, "load_ast_for_fixture", lambda _fixture: ["ast"])

    class OkTranspiler:
        def generate_code(self, _ast):
            return "print('ok')"

    class FailTranspiler:
        def generate_code(self, _ast):
            raise RuntimeError("fallo-transpiler")

    transpilers = {
        "python": OkTranspiler,
        "asm": OkTranspiler,
        "rust": FailTranspiler,
    }

    report, events, has_failures = sv.run_transpiler_syntax_validation(
        fixtures=[Path("fixture.co")],
        targets=["python", "asm", "rust"],
        transpilers=transpilers,
        strict=False,
    )

    assert report.targets["python"].ok == 1
    assert report.targets["asm"].ok == 1
    assert report.targets["rust"].fail == 1
    assert has_failures is True
    assert any(event["target"] == "rust" and event["status"] == "fail" for event in events)


def test_run_transpiler_syntax_validation_strict_con_skipped(monkeypatch):
    monkeypatch.setattr(sv, "load_ast_for_fixture", lambda _fixture: ["ast"])
    monkeypatch.setitem(sv.VALIDATORS, "custom", lambda _code: sv.ValidationResult("skipped", "tool ausente"))

    class CustomTranspiler:
        def generate_code(self, _ast):
            return "code"

    report, _, has_failures = sv.run_transpiler_syntax_validation(
        fixtures=[Path("fixture.co")],
        targets=["custom"],
        transpilers={"custom": CustomTranspiler},
        strict=True,
    )

    assert report.targets["custom"].skipped == 1
    assert has_failures is True
    assert report.errors_by_target["custom"] == ["tool ausente"]
