from types import SimpleNamespace

import pytest

import cobra.cli.commands.benchmarks_cmd as bm


@pytest.mark.timeout(10)
def test_benchmarks_command_runs(monkeypatch):
    """El comando ejecuta el script y muestra resultados."""
    called: list[object] = []

    def fake_run(config):
        called.append(config)
        return [{"backend": "python", "time": 0.1, "memory_kb": 1}]

    mensajes: list[str] = []
    monkeypatch.setattr(bm, "run_benchmarks", fake_run)
    monkeypatch.setattr(bm, "mostrar_info", lambda m: mensajes.append(m))

    rc = bm.BenchmarksCommand().run(
        SimpleNamespace(backend=None, iteraciones=1, perfil="avanzado")
    )

    assert rc == 0
    assert called
    assert any("python" in m for m in mensajes)


@pytest.mark.timeout(10)
def test_benchmarks_command_handles_errors(monkeypatch):
    """Devuelve código adecuado si el script falla."""
    def fake_run(_config):
        raise FileNotFoundError

    errores: list[str] = []
    monkeypatch.setattr(bm, "run_benchmarks", fake_run)
    monkeypatch.setattr(bm, "mostrar_error", lambda m: errores.append(m))

    rc = bm.BenchmarksCommand().run(
        SimpleNamespace(backend=None, iteraciones=1, perfil="avanzado")
    )

    assert rc == 2
    assert errores
