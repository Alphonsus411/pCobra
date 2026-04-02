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


def test_run_external_command_pasa_timeout_a_subprocess(monkeypatch):
    captured: dict[str, object] = {}

    class _CompletedProcess:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_subprocess_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return _CompletedProcess()

    monkeypatch.setattr(sv.subprocess, "run", fake_subprocess_run)

    ok, output = sv.run_external_command(["cmd", "--flag"], timeout_seconds=7)

    assert ok is True
    assert output == ""
    assert captured["kwargs"]["timeout"] == 7


@pytest.mark.parametrize(
    ("validator", "tool_name", "code", "expected_target"),
    [
        (sv._validate_javascript, "node", "console.log('ok')\n", "javascript"),
        (sv._validate_rust, "rustc", "fn main() {}\n", "rust"),
        (sv._validate_go, "go", "package main\nfunc main(){}\n", "go"),
        (sv._validate_cpp, "clang++", "int main() { return 0; }\n", "cpp"),
        (sv._validate_java, "javac", "class Main { public static void main(String[] args) {} }\n", "java"),
        (sv._validate_wasm, "wat2wasm", "(module)\n", "wasm"),
    ],
)
def test_validadores_externos_retornan_fail_en_timeout(monkeypatch, validator, tool_name, code, expected_target):
    monkeypatch.setattr(sv.shutil, "which", lambda cmd: f"/usr/bin/{cmd}" if cmd == tool_name else None)

    def fake_run_external_command(_command, cwd=None, timeout_seconds=None):
        raise sv.subprocess.TimeoutExpired(cmd=_command, timeout=timeout_seconds or 1)

    monkeypatch.setattr(sv, "run_external_command", fake_run_external_command)

    result = validator(code)

    assert result.status == "fail"
    assert "timeout" in result.message.lower()
    assert expected_target in result.message.lower()


def test_validator_asm_detecta_tokens_no_resueltos():
    result = sv.VALIDATORS["asm"]("<pendiente>\nMOV R1, 3")
    assert result.status == "fail"
    assert "no resueltos" in result.message


def test_validate_go_falla_si_build_falla_aunque_gofmt_exista(monkeypatch):
    monkeypatch.setattr(sv.shutil, "which", lambda cmd: f"/usr/bin/{cmd}" if cmd in {"go", "gofmt"} else None)

    def fake_run_external_command(command, cwd=None, timeout_seconds=None):
        if command[0].endswith("go") and command[1] == "build":
            return False, "undefined: variableInexistente"
        raise AssertionError(f"comando inesperado: {command}")

    monkeypatch.setattr(sv, "run_external_command", fake_run_external_command)

    result = sv._validate_go("package main\nfunc main(){ variableInexistente() }\n")
    assert result.status == "fail"
    assert "undefined" in result.message


def test_validate_go_ok_con_build_y_gofmt_opcional(monkeypatch):
    monkeypatch.setattr(sv.shutil, "which", lambda cmd: "/usr/bin/go" if cmd == "go" else None)
    monkeypatch.setattr(sv, "run_external_command", lambda _command, cwd=None, timeout_seconds=None: (True, ""))

    result = sv._validate_go("package main\nfunc main(){}\n")
    assert result.status == "ok"
    assert "go build correcto" in result.message
    assert "sin diagnóstico de gofmt" in result.message


def test_validate_go_ok_con_estilo_pendiente_en_gofmt(monkeypatch):
    monkeypatch.setattr(sv.shutil, "which", lambda cmd: f"/usr/bin/{cmd}" if cmd in {"go", "gofmt"} else None)
    monkeypatch.setattr(sv, "run_external_command", lambda _command, cwd=None, timeout_seconds=None: (True, ""))

    class _CompletedProcess:
        returncode = 0
        stdout = "main.go\n"
        stderr = ""

    monkeypatch.setattr(sv.subprocess, "run", lambda *args, **kwargs: _CompletedProcess())

    result = sv._validate_go("package main\nfunc main(){}\n")
    assert result.status == "ok"
    assert "detectó diferencias de formato" in result.message


def test_validate_python_syntax_incluye_tests_cli_y_core(monkeypatch, tmp_path):
    tests_dir = tmp_path / "tests"
    cli_file = tests_dir / "cli" / "test_cli_sample.py"
    core_file = tests_dir / "core" / "test_core_sample.py"
    for file_path in (cli_file, core_file):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("x = 1\n", encoding="utf-8")

    compiled_files: list[Path] = []

    monkeypatch.setattr(sv, "TESTS_DIR", tests_dir)
    monkeypatch.setattr(sv.compileall, "compile_dir", lambda *_args, **_kwargs: True)

    def _fake_compile(path, doraise):
        assert doraise is True
        compiled_files.append(Path(path))
        return None

    monkeypatch.setattr(sv.py_compile, "compile", _fake_compile)

    result = sv.validate_python_syntax()

    assert result.status == "ok"
    assert cli_file in compiled_files
    assert core_file in compiled_files


def test_validate_python_syntax_excluye_dirs_no_deseados(monkeypatch, tmp_path):
    tests_dir = tmp_path / "tests"
    valid_file = tests_dir / "cli" / "test_cli_sample.py"
    excluded_file = tests_dir / ".venv" / "lib" / "ignored.py"
    for file_path in (valid_file, excluded_file):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("x = 1\n", encoding="utf-8")

    compiled_files: list[Path] = []

    monkeypatch.setattr(sv, "TESTS_DIR", tests_dir)
    monkeypatch.setattr(sv.compileall, "compile_dir", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        sv.py_compile,
        "compile",
        lambda path, doraise: compiled_files.append(Path(path)),
    )

    result = sv.validate_python_syntax()

    assert result.status == "ok"
    assert valid_file in compiled_files
    assert excluded_file not in compiled_files


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
