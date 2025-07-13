import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from cli.cli import main


class DummyTranspiler:
    def generate_code(self, ast):  # pylint: disable=unused-argument
        return "ok"


@pytest.mark.timeout(10)
def test_bench_transpilers_generates_results(tmp_path, monkeypatch):
    import cli.commands.bench_transpilers_cmd as bt

    monkeypatch.setattr(bt, "TRANSPILERS", {"dummy": DummyTranspiler})
    monkeypatch.setattr(bt, "timeit", lambda func, number=1: 0.01)
    monkeypatch.setattr(bt, "PROGRAM_DIR", tmp_path)

    salida = tmp_path / "out.json"
    main(["benchtranspilers", "--output", str(salida)])

    data = json.loads(salida.read_text())
    assert {d["size"] for d in data} == {"small", "medium", "large"}
    for d in data:
        assert d["lang"] == "dummy"
        assert d["time"] == 0.01


@pytest.mark.timeout(10)
def test_bench_transpilers_profile_creates_file(tmp_path, monkeypatch):
    import cli.commands.bench_transpilers_cmd as bt

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(bt, "TRANSPILERS", {"dummy": DummyTranspiler})
    monkeypatch.setattr(bt, "timeit", lambda func, number=1: 0.01)
    monkeypatch.setattr(bt, "PROGRAM_DIR", tmp_path)

    salida = tmp_path / "out.json"
    main(["benchtranspilers", "--output", str(salida), "--profile"])

    assert Path("bench_transpilers.prof").exists()
