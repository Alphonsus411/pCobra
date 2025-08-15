import importlib.util
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

