"""Pruebas aisladas de fallo cerrado para el runner de benchmarks."""

import os
import subprocess
import sys
from unittest.mock import MagicMock

import pytest

from scripts.benchmarks import run_benchmarks as runner


@pytest.mark.skipif(
    not (
        runner.LINUX_TIME.is_file() if sys.platform == "linux" else hasattr(os, "wait4")
    ),
    reason="Requiere el medidor nativo",
)
def test_runtime_no_cero_resource():
    """No se debe aceptar una medición si el proceso termina con error."""
    cmd = [
        sys.executable,
        "-c",
        "import sys; sys.stderr.write('fallo de prueba'); sys.exit(9)",
    ]
    with pytest.raises(subprocess.CalledProcessError) as error:
        runner.run_and_measure(cmd)
    assert error.value.returncode == 9
    assert error.value.cmd == cmd
    assert error.value.stderr == b"fallo de prueba"


@pytest.mark.skipif(
    sys.platform != "linux" or not runner.LINUX_TIME.is_file(),
    reason="Requiere GNU time en Linux",
)
def test_memoria_resource_se_mide_por_proceso():
    cmd = [sys.executable, "-c", "data = bytearray(96 * 1024**2)"]
    _, primer_pico = runner.run_and_measure(cmd)
    _, segundo_pico = runner.run_and_measure(cmd)
    _, pico_pequeno = runner.run_and_measure([sys.executable, "-c", "pass"])
    assert primer_pico >= 96 * 1024
    assert segundo_pico >= 96 * 1024
    assert 0 < pico_pequeno < segundo_pico


def test_runtime_no_cero_psutil(monkeypatch):
    """La ruta psutil también debe comprobar el código de salida."""
    monkeypatch.setattr(runner, "resource", None)
    monkeypatch.setattr(runner, "LINUX_TIME", MagicMock(is_file=lambda: False))
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
    monkeypatch.setattr(runner, "LINUX_TIME", MagicMock(is_file=lambda: False))
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
