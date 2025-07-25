import json
from pathlib import Path

import pytest

from cli.cli import main


@pytest.mark.timeout(10)
def test_bench_profile_creates_json(tmp_path, monkeypatch):
    import cli.commands.bench_cmd as bc

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        bc.BenchCommand, "_run_benchmarks", lambda self: [{"backend": "cobra", "time": 0.1, "memory_kb": 1}]
    )

    main(["bench", "--profile"])

    data = json.loads(Path("bench_results.json").read_text())
    assert data == [{"backend": "cobra", "time": 0.1, "memory_kb": 1}]
