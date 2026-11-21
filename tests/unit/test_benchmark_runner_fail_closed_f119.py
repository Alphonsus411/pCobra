"""Pruebas aisladas de fallo cerrado para el runner de benchmarks."""

import subprocess
import sys
from unittest.mock import MagicMock

import pytest

from scripts.benchmarks import run_benchmarks as runner


def test_runtime_no_cero_resource(monkeypatch):
    """No se debe aceptar una medición si el proceso termina con error."""
    monkeypatch.setattr(runner, "resource", MagicMock())
    monkeypatch.setattr(runner, "psutil", None)

    def fail(*args, **kwargs):
        assert kwargs["check"] is True
        raise subprocess.CalledProcessError(9, args[0])

    monkeypatch.setattr(runner.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        runner.run_and_measure([sys.executable, "--version"])


def test_runtime_no_cero_psutil(monkeypatch):
    """La ruta psutil también debe comprobar el código de salida."""
    monkeypatch.setattr(runner, "resource", None)
    monkeypatch.setattr(runner, "psutil", MagicMock())

    proc = MagicMock()
    proc.pid = 123
    proc.poll.return_value = 9
    proc.wait.return_value = 9
    proc.returncode = 9
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **k: proc)

    with pytest.raises(subprocess.CalledProcessError):
        runner.run_and_measure(["runtime-inexistente-simulado"])


def test_runtime_no_cero_sin_medidor(monkeypatch):
    """Sin medidor de memoria, el fallo de ejecución sigue siendo fatal."""
    monkeypatch.setattr(runner, "resource", None)
    monkeypatch.setattr(runner, "psutil", None)

    def fail(*args, **kwargs):
        assert kwargs["check"] is True
        raise subprocess.CalledProcessError(7, args[0])

    monkeypatch.setattr(runner.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        runner.run_and_measure([sys.executable, "--version"])


def test_runner_usa_pipeline_oficial_y_no_omite_fallos(monkeypatch, tmp_path, capsys):
    """Un error de transpilación debe impedir publicar un JSON parcial."""
    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner, "validate_backend_metadata", lambda *a, **k: None)
    monkeypatch.setattr(runner, "validate_local_targets_policy", lambda *a, **k: None)
    monkeypatch.setattr(
        runner, "executable_benchmark_backends", lambda *a, **k: ("python",)
    )
    monkeypatch.setattr(
        runner, "BACKEND_METADATA", {"python": {"ext": "py", "run": ["python"]}}
    )
    monkeypatch.setattr(sys, "argv", ["run_benchmarks.py"])

    def fail(cmd, **kwargs):
        assert cmd[1] == "-c"
        assert "backend_pipeline.build" in cmd[2]
        assert cmd[3].endswith(".cobra")
        assert cmd[4] == "python"
        raise subprocess.CalledProcessError(2, cmd)

    monkeypatch.setattr(runner.subprocess, "check_output", fail)
    with pytest.raises(RuntimeError, match="transpilación"):
        runner.main()
    assert capsys.readouterr().out == ""
