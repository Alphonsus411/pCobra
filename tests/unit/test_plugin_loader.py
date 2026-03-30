import importlib.metadata
import hashlib
from unittest.mock import patch

from pathlib import Path
import sys
import types
from importlib import import_module
import pytest

from pcobra.cobra.cli.plugin import (
    descubrir_plugins,
    PluginCommand,
    PluginPolicyError,
    cargar_plugin_seguro,
    configure_plugin_policy,
)
from pcobra.cobra.cli.plugin_registry import obtener_registro, limpiar_registro

# Añadimos la carpeta de plugins de ejemplo al path para poder importar
# el plugin md2cobra durante las pruebas.
ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = ROOT / "examples" / "plugins"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PLUGIN_DIR))
sys.modules.setdefault("src.tests.test_plugin_loader", sys.modules[__name__])

class DummyPlugin(PluginCommand):
    name = "dummy"
    version = "1.0"
    def register_subparser(self, subparsers):
        pass
    def run(self, args):
        pass

def test_descubrir_plugins_carga_plugins():
    ep = importlib.metadata.EntryPoint(
        name="dummy",
        value="src.tests.test_plugin_loader:DummyPlugin",
        group="cobra.plugins",
    )
    with patch("pcobra.cobra.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=["prefix:src.tests"])
        plugins = descubrir_plugins()
    assert len(plugins) == 1
    assert plugins[0].name == "dummy"
    assert obtener_registro() == {"dummy": "1.0"}


def test_descubrir_plugins_md2cobra():
    """Comprueba que el plugin md2cobra se carga correctamente."""
    ep = importlib.metadata.EntryPoint(
        name="md2cobra",
        value="md2cobra_plugin:MarkdownToCobraCommand",
        group="cobra.plugins",
    )
    with patch("pcobra.cobra.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=["md2cobra_plugin:MarkdownToCobraCommand"])
        plugins = descubrir_plugins()
    assert any(p.__class__.__name__ == "MarkdownToCobraCommand" for p in plugins)
    assert obtener_registro() == {"md2cobra": "1.0"}


def test_plugin_ruta_invalida():
    """No se debe cargar un plugin con ruta mal formada."""
    ep = importlib.metadata.EntryPoint(
        name="malo",
        value="invalido",
        group="cobra.plugins",
    )
    with patch("pcobra.cobra.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=["prefix:invalido"])
        plugins = descubrir_plugins()
    assert plugins == []
    assert obtener_registro() == {}


def test_cargar_plugin_seguro_modulo_inexistente():
    """Un módulo inexistente no debe registrarse."""
    ep_value = "no.existe:Nope"
    with patch("pcobra.cobra.cli.plugin.import_module", side_effect=ModuleNotFoundError):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=[ep_value])
        plugin = cargar_plugin_seguro(ep_value)
    assert plugin is None
    assert obtener_registro() == {}


def test_cargar_plugin_seguro_instanciacion_falla():
    """Si la clase del plugin lanza excepción al crearse, no se registra."""

    class BoomPlugin(PluginCommand):
        name = "boom"

        def __init__(self):
            raise RuntimeError("boom")

        def register_subparser(self, subparsers):
            pass

        def run(self, args):
            pass

    module = types.SimpleNamespace(BoomPlugin=BoomPlugin)
    with patch("pcobra.cobra.cli.plugin.import_module", return_value=module):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=["fake.mod:BoomPlugin"])
        plugin = cargar_plugin_seguro("fake.mod:BoomPlugin")
    assert plugin is None
    assert obtener_registro() == {}


def test_plugin_sin_atributo_name():
    class SinNombrePlugin(PluginCommand):
        version = "1.0"
        def register_subparser(self, subparsers):
            pass
        def run(self, args):
            pass

    ep = importlib.metadata.EntryPoint(
        name="noname",
        value="tests.test_plugin_loader:SinNombrePlugin",
        group="cobra.plugins",
    )
    with patch("pcobra.cobra.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=["tests.test_plugin_loader:SinNombrePlugin"])
        plugins = descubrir_plugins()
    assert plugins == []
    assert obtener_registro() == {}


def test_cargar_plugin_seguro_sha256_contenido_correcto():
    module = import_module("tests.unit.test_plugin_loader")
    digest = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()

    limpiar_registro()
    configure_plugin_policy(safe_mode=True, allowlist=[f"sha256:{digest}"])
    plugin = cargar_plugin_seguro("tests.unit.test_plugin_loader:DummyPlugin")

    assert plugin is not None
    assert plugin.name == "dummy"


def test_cargar_plugin_seguro_sha256_incorrecto():
    limpiar_registro()
    configure_plugin_policy(safe_mode=True, allowlist=["sha256:" + ("0" * 64)])

    with pytest.raises(PluginPolicyError) as excinfo:
        cargar_plugin_seguro("tests.unit.test_plugin_loader:DummyPlugin")

    assert "sha256 del contenido" in str(excinfo.value)


def test_cargar_plugin_seguro_rechaza_sha256_de_ruta_legado():
    route = "tests.unit.test_plugin_loader:DummyPlugin"
    route_digest = hashlib.sha256(route.encode("utf-8")).hexdigest()

    limpiar_registro()
    configure_plugin_policy(safe_mode=True, allowlist=[f"sha256:{route_digest}"])

    with pytest.raises(PluginPolicyError) as excinfo:
        cargar_plugin_seguro(route)

    assert "sha256 de ruta retirado" in str(excinfo.value)


def test_cargar_plugin_seguro_modulo_sin_file_con_sha256():
    module = types.SimpleNamespace(SinFilePlugin=DummyPlugin)
    with patch("pcobra.cobra.cli.plugin.import_module", return_value=module):
        limpiar_registro()
        configure_plugin_policy(safe_mode=True, allowlist=["sha256:" + ("1" * 64)])
        with pytest.raises(PluginPolicyError) as excinfo:
            cargar_plugin_seguro("fake.mod:SinFilePlugin")

    assert "módulo_sin___file__" in str(excinfo.value)


def test_cargar_plugin_seguro_modulo_no_legible_con_sha256(caplog):
    limpiar_registro()
    configure_plugin_policy(safe_mode=True, allowlist=["sha256:" + ("2" * 64)])

    with patch("pcobra.cobra.cli.plugin._read_module_file_bytes", return_value=None):
        with pytest.raises(PluginPolicyError):
            cargar_plugin_seguro("tests.unit.test_plugin_loader:DummyPlugin")

    assert "no se pudo leer el archivo del módulo" in caplog.text


def test_cargar_plugin_seguro_allowlist_prefix():
    limpiar_registro()
    configure_plugin_policy(safe_mode=True, allowlist=["prefix:tests.unit"])
    plugin = cargar_plugin_seguro("tests.unit.test_plugin_loader:DummyPlugin")
    assert plugin is not None
