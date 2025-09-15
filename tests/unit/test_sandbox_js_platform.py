import importlib.util
import os
import shutil
import select
import subprocess
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sandbox_path = ROOT / "src" / "pcobra" / "core" / "sandbox.py"
spec = importlib.util.spec_from_file_location("sandbox", sandbox_path)
sandbox = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sandbox)
ejecutar_en_sandbox_js = sandbox.ejecutar_en_sandbox_js


def _fake_os(name: str) -> types.SimpleNamespace:
    data = {k: getattr(os, k) for k in dir(os)}
    data["name"] = name
    return types.SimpleNamespace(**data)


def _skip_if_no_vm2():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    try:
        subprocess.run(["node", "-e", "require('vm2')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("vm2 no disponible")


@pytest.mark.timeout(5)
def test_js_posix_usa_select(monkeypatch):
    _skip_if_no_vm2()
    llamada = {"value": False}

    def fake_select(rlist, wlist, xlist, timeout=None):
        llamada["value"] = True
        return select.select(rlist, wlist, xlist, timeout)

    monkeypatch.setattr(select, "select", fake_select)
    monkeypatch.setattr(sandbox, "os", _fake_os("posix"))
    salida = ejecutar_en_sandbox_js("console.log('hola')")
    assert salida.strip() == "hola"
    assert llamada["value"]


@pytest.mark.timeout(5)
def test_js_windows_evita_select(monkeypatch):
    _skip_if_no_vm2()

    def fake_select(*args, **kwargs):
        raise AssertionError("select no debe llamarse en Windows")

    monkeypatch.setattr(select, "select", fake_select)
    monkeypatch.setattr(sandbox, "os", _fake_os("nt"))
    salida = ejecutar_en_sandbox_js("console.log('hola')")
    assert salida.strip() == "hola"
