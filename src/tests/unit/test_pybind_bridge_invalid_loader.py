import sys
from types import ModuleType
from pathlib import Path
from unittest.mock import patch
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))

fake_pybind11 = ModuleType('pybind11')
fake_helpers = ModuleType('pybind11.setup_helpers')
fake_helpers.Pybind11Extension = object
fake_helpers.build_ext = object
sys.modules.setdefault('pybind11', fake_pybind11)
sys.modules.setdefault('pybind11.setup_helpers', fake_helpers)
fake_setuptools = ModuleType('setuptools')
fake_setuptools.Distribution = object
sys.modules.setdefault('setuptools', fake_setuptools)


def test_cargar_extension_loader_invalido(tmp_path, monkeypatch):
    ruta = tmp_path / "x.so"
    ruta.touch()
    monkeypatch.setenv("COBRA_ALLOWED_EXT_PATHS", str(tmp_path))
    import importlib
    import src.core.pybind_bridge as bridge
    importlib.reload(bridge)
    with patch("importlib.util.spec_from_loader", return_value=None):
        with pytest.raises(ImportError, match="No se pudo obtener un spec"):
            bridge.cargar_extension(str(ruta))

