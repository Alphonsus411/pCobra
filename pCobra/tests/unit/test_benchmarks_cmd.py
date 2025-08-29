import json
from types import SimpleNamespace

import pytest

import cobra.cli.commands.benchmarks_cmd as bm


@pytest.mark.timeout(10)
def test_benchmarks_command_runs(monkeypatch):
    """El comando ejecuta el script y muestra resultados."""
    fake_out = json.dumps([
        {"backend": "python", "time": 0.1, "memory_kb": 1}
    ])
    called: dict[str, list[str]] = {}

    def fake_check_output(cmd, text=True):  # pragma: no cover - reemplazo
        called["cmd"] = cmd
        return fake_out

    mensajes: list[str] = []
    monkeypatch.setattr(bm.subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(bm, "mostrar_info", lambda m: mensajes.append(m))

    rc = bm.BenchmarksCommand().run(SimpleNamespace(backend=None, iteraciones=1))

    assert rc == 0
    assert "run_benchmarks.py" in called["cmd"][1]
    assert any("python" in m for m in mensajes)


@pytest.mark.timeout(10)
def test_benchmarks_command_handles_errors(monkeypatch):
    """Devuelve código adecuado si el script falla."""
    def fake_check_output(cmd, text=True):  # pragma: no cover - reemplazo
        raise bm.subprocess.CalledProcessError(1, cmd)

    errores: list[str] = []
    monkeypatch.setattr(bm.subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(bm, "mostrar_error", lambda m: errores.append(m))

    rc = bm.BenchmarksCommand().run(SimpleNamespace(backend=None, iteraciones=1))

    assert rc == 3
    assert errores

