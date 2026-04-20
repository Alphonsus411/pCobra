import json
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest


class DummyTranspiler:
    def generate_code(self, ast):  # pylint: disable=unused-argument
        return "ok"


@pytest.mark.timeout(10)
def test_bench_transpilers_generates_results(tmp_path, monkeypatch):
    bt = importlib.import_module("cobra.cli.commands.bench_transpilers_cmd")
    bt_pcobra = importlib.import_module("pcobra.cobra.cli.commands.bench_transpilers_cmd")

    for module in (bt, bt_pcobra):
        monkeypatch.setattr(module, "cli_transpilers", lambda: {"dummy": DummyTranspiler})
        monkeypatch.setattr(module, "timeit", lambda func, number=1: 0.01)
        monkeypatch.setattr(module, "obtener_ast", lambda _code: object())
        monkeypatch.setattr(module, "PROGRAM_DIR", tmp_path)

    salida = tmp_path / "out.json"
    cmd = bt.BenchTranspilersCommand()
    result = cmd.run(SimpleNamespace(output=str(salida), profile=False))
    assert result == 0

    data = json.loads(salida.read_text())
    assert {d["size"] for d in data} == {"small", "medium", "large"}
    for d in data:
        assert d["lang"] == "dummy"
        assert d["time"] == 0.01


@pytest.mark.timeout(10)
def test_bench_transpilers_profile_creates_file(tmp_path, monkeypatch):
    bt = importlib.import_module("cobra.cli.commands.bench_transpilers_cmd")
    bt_pcobra = importlib.import_module("pcobra.cobra.cli.commands.bench_transpilers_cmd")

    monkeypatch.chdir(tmp_path)
    for module in (bt, bt_pcobra):
        monkeypatch.setattr(module, "cli_transpilers", lambda: {"dummy": DummyTranspiler})
        monkeypatch.setattr(module, "timeit", lambda func, number=1: 0.01)
        monkeypatch.setattr(module, "obtener_ast", lambda _code: object())
        monkeypatch.setattr(module, "PROGRAM_DIR", tmp_path)

    salida = tmp_path / "out.json"
    cmd = bt.BenchTranspilersCommand()
    result = cmd.run(SimpleNamespace(output=str(salida), profile=True))
    assert result == 0

    assert Path("bench_transpilers.prof").exists()


@pytest.mark.timeout(10)
def test_ensure_program_reads_and_writes_in_program_dir(tmp_path, monkeypatch):
    bt = importlib.import_module("cobra.cli.commands.bench_transpilers_cmd")

    program_dir = tmp_path / "scripts" / "benchmarks" / "programs"
    monkeypatch.setattr(bt, "PROGRAM_DIR", program_dir)

    cmd = bt.BenchTranspilersCommand()
    generated = cmd._ensure_program("small")

    small_file = program_dir / "small.co"
    assert small_file.exists()
    assert generated == small_file.read_text(encoding="utf-8")

    expected = "imprimir('desde-test')\n"
    small_file.write_text(expected, encoding="utf-8")

    reloaded = cmd._ensure_program("small")
    assert reloaded == expected
