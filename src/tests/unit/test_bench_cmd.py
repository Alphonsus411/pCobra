import json
from pathlib import Path

import pytest

from cli.cli import main
import cli.commands.bench_cmd as bc
import tempfile

orig_ntf = tempfile.NamedTemporaryFile


@pytest.mark.timeout(10)
def test_bench_profile_creates_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(bc, "run_and_measure", lambda *a, **k: (0.1, 1))
    monkeypatch.setattr(bc.subprocess, "check_output", lambda *a, **k: "")
    monkeypatch.setattr(bc.subprocess, "check_call", lambda *a, **k: None)
    monkeypatch.setattr(bc.shutil, "which", lambda x: x)
    monkeypatch.setattr(bc, "BACKENDS", {})
    created = []
    def fake_tmp(*args, **kwargs):
        tmp = orig_ntf(*args, **kwargs)
        created.append(Path(tmp.name))
        return tmp
    monkeypatch.setattr(bc.tempfile, "NamedTemporaryFile", fake_tmp)

    main(["bench", "--profile"])

    data = json.loads(Path("bench_results.json").read_text())
    assert data == [{"backend": "cobra", "time": 0.1, "memory_kb": 1}]
    for p in created:
        assert not p.exists()
