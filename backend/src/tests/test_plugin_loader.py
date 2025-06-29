import importlib.metadata
from unittest.mock import patch

from src.cli.plugin import descubrir_plugins, PluginCommand
from src.cli.plugin_registry import obtener_registro, limpiar_registro

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
    assert isinstance(plugins[0], DummyPlugin)
    assert obtener_registro() == {"dummy": "1.0"}
