from io import StringIO
from unittest.mock import patch
import importlib.metadata

from src.cli.cli import main
from src.cli.plugin_loader import PluginCommand


class DummyPlugin(PluginCommand):
    name = "dummy"
    version = "2.3"

    def register_subparser(self, subparsers):
        pass

    def run(self, args):
        pass


def test_cli_plugins_muestra_registro():
    ep = importlib.metadata.EntryPoint(
        name="dummy",
        value="src.tests.test_cli_plugins_cmd:DummyPlugin",
        group="cobra.plugins",
    )
    with patch("src.cli.plugin_loader.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["plugins"])
    assert "dummy 2.3" in out.getvalue().strip()

