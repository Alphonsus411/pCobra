import json
import os
from pathlib import Path
from cli.cli import main
from cli.commands import benchthreads_cmd
import tempfile

orig_ntf = tempfile.NamedTemporaryFile
import pytest

@pytest.mark.timeout(10)
def test_benchthreads_generates_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(benchthreads_cmd, "_measure", lambda f: (0.1, 0.05, 1))

    created = []

    def fake_run(self, args):
        env = os.environ.copy()
        tmp = orig_ntf(suffix=".toml", delete=False)
        created.append(Path(tmp.name))
        tmp.close()
        env["COBRA_TOML"] = tmp.name
        Path(args.output).write_text(
            json.dumps(
                [
                    {
                        "modo": "cli_hilos",
                        "time": 0.1,
                        "cpu": 0.05,
                        "io": 1,
                    }
                ]
            )
        )
        os.unlink(tmp.name)
        return 0

    monkeypatch.setattr(benchthreads_cmd.BenchThreadsCommand, "run", fake_run)

    def fake_tempfile(*args, **kwargs):
        tmp = orig_ntf(*args, **kwargs)
        created.append(Path(tmp.name))
        return tmp

    monkeypatch.setattr(benchthreads_cmd.tempfile, "NamedTemporaryFile", fake_tempfile)
    salida = tmp_path / "threads.json"
    main(["benchthreads", "--output", str(salida)])
    data = json.loads(salida.read_text())
    modos = {d["modo"] for d in data}
    assert modos == {"cli_hilos"}
    for d in data:
        assert isinstance(d["time"], float)
        assert "cpu" in d and "io" in d
    for p in created:
        assert not p.exists()

