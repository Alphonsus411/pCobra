import importlib.util
import io
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sandbox_path = ROOT / "src" / "pcobra" / "core" / "sandbox.py"
spec = importlib.util.spec_from_file_location("sandbox", sandbox_path)
sandbox = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sandbox)
ejecutar_en_sandbox_js = sandbox.ejecutar_en_sandbox_js
compilar_en_sandbox_cpp = sandbox.compilar_en_sandbox_cpp
ejecutar_en_contenedor = sandbox.ejecutar_en_contenedor


@pytest.mark.timeout(5)
def test_js_timeout_invalido():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    salida = ejecutar_en_sandbox_js("console.log('hola')", timeout=-1)
    assert "agotado" in salida


@pytest.mark.timeout(5)
def test_compilar_cpp_sin_contenedor():
    with patch.object(sandbox, "ejecutar_en_contenedor", side_effect=RuntimeError("docker")):
        with pytest.raises(RuntimeError, match="Contenedor.*C\+\+"):
            compilar_en_sandbox_cpp("int main() { return 0; }")


def test_contenedor_backend_invalido():
    with pytest.raises(ValueError):
        ejecutar_en_contenedor("print(1)", "malicioso")


@pytest.mark.timeout(5)
def test_js_detecta_reemplazo_binario(monkeypatch, tmp_path):
    fake_node = tmp_path / "node"
    fake_node.write_text("#!/bin/sh\nexit 0\n")
    fake_node.chmod(0o755)

    monkeypatch.setattr(shutil, "which", lambda _: str(fake_node))
    monkeypatch.setattr(
        sandbox.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout="3.9.19"),
    )

    original_popen = sandbox.subprocess.Popen

    def fake_popen(cmd, *a, **k):
        proc = original_popen(cmd, *a, **k)
        fake_node.unlink()
        fake_node.write_text("#!/bin/sh\nexit 0\n")
        fake_node.chmod(0o755)
        return proc

    monkeypatch.setattr(sandbox.subprocess, "Popen", fake_popen)

    with pytest.raises(sandbox.SecurityError):
        ejecutar_en_sandbox_js("console.log('hola')")


def test_contenedor_trunca_salida(monkeypatch, tmp_path):
    datos = b"A" * (sandbox.MAX_CONTAINER_OUTPUT_BYTES + 100)

    fake_docker = tmp_path / "docker"
    fake_docker.write_text("#!/bin/sh\nexit 0\n")
    fake_docker.chmod(0o755)
    monkeypatch.setattr(sandbox.shutil, "which", lambda *_: str(fake_docker))

    class FakeStdout:
        def __init__(self, data: bytes) -> None:
            self._data = data
            self._pos = 0

        def readline(self) -> bytes:
            if self._pos >= len(self._data):
                return b""
            chunk = self._data[self._pos :]
            self._pos = len(self._data)
            return chunk

        def read(self, size: int = -1) -> bytes:
            if self._pos >= len(self._data):
                return b""
            if size < 0:
                size = len(self._data) - self._pos
            chunk = self._data[self._pos : self._pos + size]
            self._pos += len(chunk)
            return chunk

    class FakeProc:
        def __init__(self, data: bytes) -> None:
            self.stdout = FakeStdout(data)
            self.stdin = io.BytesIO()
            self.returncode: int | None = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def kill(self) -> None:
            self.returncode = -9

        def wait(self) -> int:
            if self.returncode is None:
                self.returncode = 0
            return self.returncode

        def poll(self) -> int:
            return self.returncode

    monkeypatch.setattr(sandbox.subprocess, "Popen", lambda *a, **k: FakeProc(datos))
    monkeypatch.setattr(sandbox.os, "name", "nt")

    resultado = ejecutar_en_contenedor("print('hola')", "python")

    assert resultado.endswith("\n[output truncated]")
    cuerpo, _ = resultado.rsplit("\n", 1)
    assert len(cuerpo.encode()) == sandbox.MAX_CONTAINER_OUTPUT_BYTES
