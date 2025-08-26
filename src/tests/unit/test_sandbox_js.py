import importlib.util
import os
import shutil
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sandbox_path = ROOT / "core" / "sandbox.py"
spec = importlib.util.spec_from_file_location("sandbox", sandbox_path)
sandbox = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sandbox)
ejecutar_en_sandbox_js = sandbox.ejecutar_en_sandbox_js


@pytest.mark.timeout(5)
def test_sandbox_js_template_string():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    salida = ejecutar_en_sandbox_js("console.log(`hola ${1 + 1}`)")
    assert salida.strip() == "hola 2"


@pytest.mark.timeout(5)
def test_sandbox_js_inyeccion_no_ejecuta():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    codigo = "`);console.log('inseguro');//"
    salida = ejecutar_en_sandbox_js(codigo)
    assert "SyntaxError" in salida


@pytest.mark.timeout(5)
def test_sandbox_js_timeout():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    codigo = "while(true){}"
    salida = ejecutar_en_sandbox_js(codigo, timeout=1)
    assert "agotado" in salida


@pytest.mark.timeout(5)
def test_sandbox_js_sin_process():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    salida = ejecutar_en_sandbox_js("process.exit(0)")
    assert "process is not defined" in salida


@pytest.mark.timeout(5)
def test_sandbox_js_sin_comandos_externos():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    codigo = "require('child_process').exec('echo hola')"
    salida = ejecutar_en_sandbox_js(codigo)
    assert "Cannot find module" in salida


@pytest.mark.timeout(5)
def test_sandbox_js_ignora_node_options(monkeypatch):
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    monkeypatch.setenv("NODE_OPTIONS", "--eval \"process.stdout.write('pwned')\"")
    salida = ejecutar_en_sandbox_js("console.log('hola')")
    assert salida.strip() == "hola"
    assert "pwned" not in salida


@pytest.mark.timeout(5)
def test_sandbox_js_filtra_env_vars(monkeypatch):
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    env_vars = {
        "NODE_OPTIONS": "--eval \"process.stdout.write('pwned')\"",
        "PATH": "/tmp",
        "SAFE": "1",
        "MAL-ENV": "bad",
    }
    salida = ejecutar_en_sandbox_js("console.log('hola')", env_vars=env_vars)
    assert salida.strip() == "hola"
    assert "pwned" not in salida


@pytest.mark.timeout(5)
def test_sandbox_js_env_vars_permitidas(monkeypatch):
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")

    capturadas = {}
    original_popen = subprocess.Popen

    def fake_popen(cmd, *args, **kwargs):
        capturadas.update(kwargs.get("env", {}))
        return original_popen(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    env_vars = {
        "NODE_OPTIONS": "--eval \"process.stdout.write('pwned')\"",
        "PATH": "/tmp",
        "API_KEY": "secreta",
    }

    salida = ejecutar_en_sandbox_js("console.log('hola')", env_vars=env_vars)
    assert salida.strip() == "hola"
    assert "pwned" not in salida
    assert capturadas.get("API_KEY") == "secreta"
    assert capturadas.get("NODE_OPTIONS") is None
    assert capturadas.get("PATH") != "/tmp"


@pytest.mark.timeout(5)
def test_sandbox_js_trunca_salida_grande():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    codigo = "console.log('a'.repeat(20000))"
    salida = ejecutar_en_sandbox_js(codigo)
    assert len(salida.encode()) <= sandbox.MAX_JS_OUTPUT_BYTES + 100
    assert "truncated" in salida


@pytest.mark.timeout(5)
def test_sandbox_js_trunca_stderr_grande_no_bloquea():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    codigo = "console.error('e'.repeat(20000))"
    salida = ejecutar_en_sandbox_js(codigo)
    assert len(salida.encode()) <= sandbox.MAX_JS_OUTPUT_BYTES + 100
    assert "truncated" in salida
    assert not salida.startswith("Error:")


@pytest.mark.timeout(5)
def test_sandbox_js_limita_memoria():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")
    codigo = "const a=[]; while(true) a.push(new Array(1e6).fill('x'));"
    salida = ejecutar_en_sandbox_js(codigo, memoria_mb=16)
    assert "heap out of memory" in salida.lower()


@pytest.mark.timeout(5)
def test_sandbox_js_elimina_archivo_inexistente(monkeypatch):
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")

    original_popen = subprocess.Popen

    def fake_popen(cmd, *args, **kwargs):
        proc = original_popen(cmd, *args, **kwargs)
        tmp_path = cmd[-1]

        class Wrapped:
            def __init__(self, proc, tmp_path):
                self.proc = proc
                self.tmp_path = tmp_path
                self.stdout = proc.stdout

            def __getattr__(self, name):
                return getattr(self.proc, name)

            def __enter__(self):
                self.proc.__enter__()
                self.stdout = self.proc.stdout
                return self

            def __exit__(self, exc_type, exc, tb):
                os.unlink(self.tmp_path)
                return self.proc.__exit__(exc_type, exc, tb)

        return Wrapped(proc, tmp_path)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    salida = ejecutar_en_sandbox_js("console.log('hola')")
    assert salida.strip() == "hola"
