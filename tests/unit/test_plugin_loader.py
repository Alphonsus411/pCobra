import importlib.metadata
from unittest.mock import patch

from pathlib import Path
import sys
import types

from src.cli.plugin import (
    descubrir_plugins,
    PluginCommand,
    cargar_plugin_seguro,
)
from src.cli.plugin_registry import obtener_registro, limpiar_registro

# Añadimos la carpeta de plugins de ejemplo al path para poder importar
# el plugin md2cobra durante las pruebas.
ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = ROOT / "examples" / "plugins"
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
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
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
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
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
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
        plugins = descubrir_plugins()
    assert plugins == []
    assert obtener_registro() == {}


def test_cargar_plugin_seguro_modulo_inexistente():
    """Un módulo inexistente no debe registrarse."""
    ep_value = "no.existe:Nope"
    with patch("src.cli.plugin.import_module", side_effect=ModuleNotFoundError):
        limpiar_registro()
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
    with patch("src.cli.plugin.import_module", return_value=module):
        limpiar_registro()
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
        value="src.tests.test_plugin_loader:SinNombrePlugin",
        group="cobra.plugins",
    )
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        limpiar_registro()
        plugins = descubrir_plugins()
    assert plugins == []
    assert obtener_registro() == {}
