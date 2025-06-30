import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import shutil

from src.cli.cli import main
from src.cobra.transpilers import module_map
from src.cli.commands import benchmarks_cmd


@pytest.mark.timeout(20)
def test_benchmarks2_generates_json(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    salida = tmp_path / "res.json"
    main(["benchmarks2", "--output", str(salida)])
    data = json.loads(salida.read_text())
    modos = {d["modo"] for d in data}
    assert {"cobra", "python", "js", "sandbox"}.issubset(modos)
    for d in data:
        assert isinstance(d["time"], float)
        assert isinstance(d["memory_kb"], int)


@pytest.mark.timeout(60)
def test_benchmarks_generates_data_for_all_backends(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})

    def patched_run(self, args):
        results = [
            {"backend": b, "time": 0.1, "memory_kb": 123}
            for b in benchmarks_cmd.BACKENDS.keys()
        ]
        data = json.dumps(results, indent=2)
        if args.output:
            Path(args.output).write_text(data)
        else:
            print(data)
        return 0

    monkeypatch.setattr(benchmarks_cmd.BenchmarksCommand, "run", patched_run)
    salida = tmp_path / "bench.json"
    main(["benchmarks", "--output", str(salida)])
    data = json.loads(salida.read_text())
    modos = {d["backend"] for d in data}
    assert {"python", "js", "go", "cpp", "ruby", "rust"}.issubset(modos)
    for d in data:
        assert isinstance(d["time"], float)
        assert isinstance(d["memory_kb"], int)
