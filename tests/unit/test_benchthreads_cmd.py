import json
from pathlib import Path
from src.cli.cli import main
from src.cli.commands import benchthreads_cmd
import pytest

@pytest.mark.timeout(10)
def test_benchthreads_generates_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(benchthreads_cmd, "_measure", lambda f: (0.1, 0.05, 1))
    salida = tmp_path / "threads.json"
    main(["benchthreads", "--output", str(salida)])
    data = json.loads(salida.read_text())
    modos = {d["modo"] for d in data}
    assert {"secuencial", "cli_hilos", "kernel_hilos"} == modos
    for d in data:
        assert isinstance(d["time"], float)
        assert "cpu" in d and "io" in d

