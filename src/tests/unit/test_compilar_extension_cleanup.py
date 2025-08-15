import sys
from types import ModuleType
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

fake_pybind11 = ModuleType('pybind11')
fake_helpers = ModuleType('pybind11.setup_helpers')


class DummyExt:
    def __init__(self, name, sources, extra_compile_args=None):
        self.name = name
        self.sources = sources


class DummyCmd:
    def __init__(self, dist):
        self.build_lib = ''
        self.build_temp = ''
        self.ext_modules = dist.ext_modules

    def finalize_options(self):
        pass

    def run(self):
        Path(self.build_lib).mkdir(parents=True, exist_ok=True)
        (Path(self.build_lib) / f"{self.ext_modules[0].name}.so").touch()

    def get_ext_filename(self, name: str) -> str:
        return f"{name}.so"


fake_helpers.Pybind11Extension = DummyExt
fake_helpers.build_ext = DummyCmd
sys.modules.setdefault('pybind11', fake_pybind11)
sys.modules.setdefault('pybind11.setup_helpers', fake_helpers)

fake_setuptools = ModuleType('setuptools')


class DummyDist:
    def __init__(self, attrs):
        self.ext_modules = attrs["ext_modules"]


fake_setuptools.Distribution = DummyDist
sys.modules.setdefault('setuptools', fake_setuptools)


def test_compilar_extension_elimina_directorio():
    import core.pybind_bridge as bridge
    importlib.reload(bridge)

    path = bridge.compilar_extension('mod', 'codigo')
    assert not Path(path).exists()
    assert not Path(path).parent.exists()
