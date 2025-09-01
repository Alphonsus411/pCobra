import sys
from types import ModuleType
from pathlib import Path
import importlib
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

fake_pybind11 = ModuleType('pybind11')
fake_helpers = ModuleType('pybind11.setup_helpers')
fake_helpers.Pybind11Extension = object
fake_helpers.build_ext = object
sys.modules.setdefault('pybind11', fake_pybind11)
sys.modules.setdefault('pybind11.setup_helpers', fake_helpers)
fake_setuptools = ModuleType('setuptools')
fake_setuptools.Distribution = object
sys.modules.setdefault('setuptools', fake_setuptools)


def test_cargar_extension_invalid_path(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    monkeypatch.setenv("COBRA_ALLOWED_EXT_PATHS", str(allowed))
    import core.pybind_bridge as bridge
    importlib.reload(bridge)
    invalid = tmp_path / "other" / "x.so"
    invalid.parent.mkdir()
    invalid.touch()
    with pytest.raises(ValueError):
        bridge.cargar_extension(str(invalid))


def test_cargar_extension_invalid_parent(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    monkeypatch.setenv("COBRA_ALLOWED_EXT_PATHS", str(allowed))
    import core.pybind_bridge as bridge
    importlib.reload(bridge)
    outside = allowed.parent / "x.so"
    outside.touch()
    with pytest.raises(ValueError):
        bridge.cargar_extension(str(outside))

