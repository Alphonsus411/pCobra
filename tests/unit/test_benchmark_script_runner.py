from pathlib import Path

import pytest

from scripts.benchmarks import run_benchmarks as runner


def test_transpilar_benchmark_usa_pipeline_con_backend_explicito(tmp_path, monkeypatch):
    source = tmp_path / "program.co"
    source.write_text("imprimir(1)\n", encoding="utf-8")
    llamadas = []

    def fake_build(path, hints):
        llamadas.append((path, hints))
        return {"backend": "python", "code": "print(1)\n"}

    monkeypatch.setattr(runner.backend_pipeline, "build", fake_build)

    assert runner.transpilar_benchmark(source, "python") == "print(1)\n"
    assert llamadas == [
        (
            str(source),
            {"preferred_backend": "python", "source_file": str(source)},
        )
    ]


def test_transpilar_benchmark_rechaza_backend_distinto(tmp_path, monkeypatch):
    source = tmp_path / "program.co"
    source.write_text("imprimir(1)\n", encoding="utf-8")
    monkeypatch.setattr(
        runner.backend_pipeline,
        "build",
        lambda *_args, **_kwargs: {"backend": "javascript", "code": ""},
    )

    with pytest.raises(RuntimeError, match="backend distinto"):
        runner.transpilar_benchmark(source, "python")


def test_normalize_rust_program_envuelve_snippet_con_imports_del_transpilador():
    snippet = "use crate::corelibs::*;\nlet x = 0;\nprintln!(\"{x}\");\n"

    assert runner.normalize_rust_program(snippet) == (
        "mod corelibs {}\n"
        "mod standard_library {}\n\n"
        "fn main() {\n"
        "    use crate::corelibs::*;\n"
        "    let x = 0;\n"
        "    println!(\"{x}\");\n"
        "}\n"
    )


def test_normalize_rust_program_no_envuelve_programa_completo():
    program = "fn main() {\n    println!(\"ok\");\n}\n"

    assert runner.normalize_rust_program(program) == program


def test_main_rechaza_resultados_vacios(monkeypatch):
    monkeypatch.setattr(
        runner, "validate_backend_metadata", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        runner, "validate_local_targets_policy", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        runner, "executable_benchmark_backends", lambda *_args, **_kwargs: ()
    )
    monkeypatch.setattr("sys.argv", ["run_benchmarks.py"])

    with pytest.raises(RuntimeError, match="todos los backends"):
        runner.main()
