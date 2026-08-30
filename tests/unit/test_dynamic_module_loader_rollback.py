import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

from pcobra.cobra import usar_loader
from pcobra.core import database, pybind_bridge


def test_modulo_nuevo_fallido_no_permanece_en_sys_modules(tmp_path):
    nombre = "modulo_nuevo_fallido"
    (tmp_path / f"{nombre}.py").write_text(
        "parcial = True\nraise RuntimeError('fallo')\n"
    )

    with pytest.raises(RuntimeError, match="fallo"):
        usar_loader._cargar_modulo_local_desde_directorio(nombre, tmp_path)

    assert nombre not in sys.modules


@pytest.mark.parametrize("valor_previo", [ModuleType("previo"), None])
def test_modulo_previamente_existente_se_restaura_exactamente(
    tmp_path, monkeypatch, valor_previo
):
    nombre = "modulo_previamente_existente"
    ruta = tmp_path / f"{nombre}.py"
    ruta.write_text("raise ValueError('fallo')\n")
    monkeypatch.setitem(sys.modules, nombre, valor_previo)

    with pytest.raises(ValueError, match="fallo"):
        usar_loader._cargar_modulo_local_desde_ruta(nombre, ruta)

    assert sys.modules[nombre] is valor_previo


def test_reintento_tras_fallo_carga_el_modulo_correctamente(tmp_path):
    nombre = "modulo_reintentable"
    ruta = tmp_path / f"{nombre}.py"
    ruta.write_text("raise RuntimeError('primer intento')\n")

    with pytest.raises(RuntimeError, match="primer intento"):
        usar_loader._cargar_modulo_local_desde_directorio(nombre, tmp_path)
    ruta.write_text("resultado = 42\n")

    modulo = usar_loader._cargar_modulo_local_desde_directorio(nombre, tmp_path)

    assert modulo.resultado == 42
    assert nombre not in sys.modules


def test_pybind_restaura_entrada_previa_tras_carga_exitosa(tmp_path, monkeypatch):
    ruta = tmp_path / "extension.so"
    ruta.touch()
    previo = ModuleType("extension_previa")

    class LoaderExitoso:
        name = "extension"

        def __init__(self, nombre, path):
            self.name = nombre

        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module.resultado = 42

    monkeypatch.setattr(pybind_bridge, "_ALLOWED_PREFIXES", [str(tmp_path)])
    monkeypatch.setattr(
        pybind_bridge.importlib.machinery, "ExtensionFileLoader", LoaderExitoso
    )
    monkeypatch.setitem(sys.modules, "extension", previo)

    cargado = pybind_bridge.cargar_extension(str(ruta))

    assert cargado.resultado == 42
    assert sys.modules["extension"] is previo


def test_paquete_con_init_fallido_no_permanece_en_sys_modules(tmp_path):
    nombre = "paquete_fallido"
    paquete = tmp_path / nombre
    paquete.mkdir()
    (paquete / "__init__.py").write_text(
        "instancia_parcial = object()\nraise LookupError('init fallido')\n"
    )

    with pytest.raises(LookupError, match="init fallido"):
        usar_loader._cargar_modulo_local_desde_directorio(nombre, tmp_path)

    assert nombre not in sys.modules


def test_instancia_parcial_no_es_observable_tras_el_fallo(tmp_path):
    nombre = "modulo_parcial"
    (tmp_path / f"{nombre}.py").write_text(
        "import sys\ninstancia_parcial = sys.modules[__name__]\nraise RuntimeError('fallo')\n"
    )

    with pytest.raises(RuntimeError, match="fallo") as error:
        usar_loader._cargar_modulo_local_desde_directorio(nombre, tmp_path)

    assert nombre not in sys.modules
    assert not hasattr(error.value, "instancia_parcial")


def test_pybind_restaura_entrada_previa_si_falla_el_loader(tmp_path, monkeypatch):
    ruta = tmp_path / "extension.so"
    ruta.touch()
    previo = ModuleType("extension_previa")

    class LoaderFallido:
        name = "extension"

        def __init__(self, nombre, path):
            self.name = nombre

        def create_module(self, spec):
            return None

        def exec_module(self, module):
            assert sys.modules[self.name] is module
            raise RuntimeError("extension fallida")

    monkeypatch.setattr(pybind_bridge, "_ALLOWED_PREFIXES", [str(tmp_path)])
    monkeypatch.setattr(
        pybind_bridge.importlib.machinery, "ExtensionFileLoader", LoaderFallido
    )
    monkeypatch.setitem(sys.modules, "extension", previo)

    with pytest.raises(RuntimeError, match="extension fallida"):
        pybind_bridge.cargar_extension(str(ruta))

    assert sys.modules["extension"] is previo


def test_database_elimina_modulo_principal_parcial_si_falla(monkeypatch, tmp_path):
    importlib.reload(database)
    constants = ModuleType("sqliteplus.utils.constants")
    monkeypatch.setitem(sys.modules, "sqliteplus.utils.constants", constants)
    monkeypatch.setattr(database, "_SQLITEPLUS_CLASS", None)

    class LoaderFallido:
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            assert sys.modules["sqliteplus_utils_sync"] is module
            raise RuntimeError("database fallida")

    module_path = tmp_path / "sqliteplus_sync.py"
    module_path.touch()
    dist = SimpleNamespace(locate_file=lambda path: module_path)
    spec = SimpleNamespace(name="sqliteplus_utils_sync", loader=LoaderFallido())
    monkeypatch.setattr(database, "distribution", lambda name: dist)
    monkeypatch.setattr(
        database.importlib_util, "spec_from_file_location", lambda *args: spec
    )
    monkeypatch.setattr(
        database.importlib_util,
        "module_from_spec",
        lambda loaded_spec: ModuleType(loaded_spec.name),
    )

    with pytest.raises(RuntimeError, match="database fallida"):
        database._load_sqliteplus_class()

    assert "sqliteplus_utils_sync" not in sys.modules


def test_database_elimina_modulo_constants_parcial_si_falla(monkeypatch, tmp_path):
    importlib.reload(database)
    constants_name = "sqliteplus.utils.constants"
    monkeypatch.delitem(sys.modules, constants_name, raising=False)

    class LoaderFallido:
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            assert sys.modules[constants_name] is module
            raise RuntimeError("constants fallido")

    constants_path = tmp_path / "constants.py"
    constants_path.touch()
    sync_path = tmp_path / "sqliteplus_sync.py"
    sync_path.touch()
    dist = SimpleNamespace(
        locate_file=lambda path: (
            constants_path if path == "utils/constants.py" else sync_path
        )
    )
    spec = SimpleNamespace(name=constants_name, loader=LoaderFallido())
    monkeypatch.setattr(database, "distribution", lambda name: dist)
    monkeypatch.setattr(
        database.importlib_util, "spec_from_file_location", lambda *args: spec
    )
    monkeypatch.setattr(
        database.importlib_util,
        "module_from_spec",
        lambda loaded_spec: ModuleType(loaded_spec.name),
    )

    with pytest.raises(RuntimeError, match="constants fallido"):
        database._load_sqliteplus_class()

    assert constants_name not in sys.modules
