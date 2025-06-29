import importlib.metadata
from unittest.mock import patch

from pathlib import Path
import sys

from src.cli.plugin import descubrir_plugins, PluginCommand
from src.cli.plugin_registry import obtener_registro, limpiar_registro

# Añadimos la carpeta de plugins de ejemplo al path para poder importar
# el plugin md2cobra durante las pruebas.
ROOT = Path(__file__).resolve().parents[3]
PLUGIN_DIR = ROOT / "examples" / "plugins"
sys.path.insert(0, str(PLUGIN_DIR))

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
