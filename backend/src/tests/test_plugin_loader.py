import importlib.metadata
from unittest.mock import patch

from src.cli.plugin_loader import descubrir_plugins, PluginCommand

class DummyPlugin(PluginCommand):
    name = "dummy"
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
    with patch("src.cli.plugin_loader.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        plugins = descubrir_plugins()
    assert len(plugins) == 1
    assert isinstance(plugins[0], DummyPlugin)
