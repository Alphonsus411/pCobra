import subprocess
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from types import ModuleType
import sys
import importlib

import pytest

# Fakes para evitar dependencias de pybind11 al importar core.nativos
fake_pybind11 = ModuleType('pybind11')
fake_helpers = ModuleType('pybind11.setup_helpers')
fake_helpers.Pybind11Extension = object
fake_helpers.build_ext = object
sys.modules.setdefault('pybind11', fake_pybind11)
sys.modules.setdefault('pybind11.setup_helpers', fake_helpers)
fake_setuptools = ModuleType('setuptools')
fake_setuptools.Distribution = object
sys.modules.setdefault('setuptools', fake_setuptools)


def _compilar_lib(dir_: Path) -> Path:
    src = dir_ / "lib.c"
    src.write_text("int triple(int x){return x*3;}")
    lib = dir_ / "libtriple.so"
    subprocess.run([
        "gcc",
        "-shared",
        "-fPIC",
        str(src),
        "-o",
        str(lib),
    ], check=True)
    return lib


@pytest.mark.timeout(5)
def test_ctypes_bridge_executes_function(tmp_path, monkeypatch):
    to_python = pytest.importorskip("cobra.transpilers.transpiler.to_python")
    ast_nodes = pytest.importorskip("core.ast_nodes")
    TranspiladorPython = to_python.TranspiladorPython
    NodoAsignacion = ast_nodes.NodoAsignacion
    NodoValor = ast_nodes.NodoValor
    NodoLlamadaFuncion = ast_nodes.NodoLlamadaFuncion
    NodoImprimir = ast_nodes.NodoImprimir
    monkeypatch.setenv("COBRA_ALLOWED_LIB_PATHS", str(tmp_path))
    import core.ctypes_bridge as bridge
    importlib.reload(bridge)
    lib = _compilar_lib(tmp_path)
    ast = [
        NodoAsignacion(
            "triple",
            NodoLlamadaFuncion(
                "cargar_funcion",
                [NodoValor(f"'{lib}'"), NodoValor("'triple'")],
            ),
        ),
        NodoImprimir(NodoLlamadaFuncion("triple", [NodoValor(4)])),
    ]
    code = TranspiladorPython().generate_code(ast)
    with patch("sys.stdout", new_callable=StringIO) as out:
        exec(code, {})
    assert out.getvalue().strip() == "12"


def test_ctypes_bridge_invalid_path(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    monkeypatch.setenv("COBRA_ALLOWED_LIB_PATHS", str(allowed))
    import core.ctypes_bridge as bridge
    importlib.reload(bridge)
    invalid = tmp_path / "other" / "lib.so"
    with pytest.raises(ValueError):
        bridge.cargar_biblioteca(str(invalid))


def test_ctypes_bridge_invalid_parent(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    monkeypatch.setenv("COBRA_ALLOWED_LIB_PATHS", str(allowed))
    import core.ctypes_bridge as bridge
    importlib.reload(bridge)
    outside = allowed.parent / "lib.so"
    with pytest.raises(ValueError):
        bridge.cargar_biblioteca(str(outside))


def test_ctypes_bridge_symlink_blocked(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("COBRA_ALLOWED_LIB_PATHS", str(allowed))
    import core.ctypes_bridge as bridge
    importlib.reload(bridge)
    lib = _compilar_lib(outside)
    link = allowed / "libtriple.so"
    link.symlink_to(lib)
    with pytest.raises(ValueError):
        bridge.cargar_biblioteca(str(link))
