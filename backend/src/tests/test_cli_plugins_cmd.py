from io import StringIO
from unittest.mock import patch
import importlib.metadata

from src.cli.cli import main
from src.cli.plugin_loader import PluginCommand


class DummyPlugin(PluginCommand):
    name = "dummy"
    version = "4.4"

    def register_subparser(self, subparsers):
        pass

    def run(self, args):
        pass


class HolaPlugin(PluginCommand):
    name = "hola"
    version = "1.0"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)

    def run(self, args):
        print("¡Hola desde un plugin!")


def test_cli_plugins_muestra_registro():
    ep = importlib.metadata.EntryPoint(
        name="dummy",
        value="src.tests.test_cli_plugins_cmd:DummyPlugin",
        group="cobra.plugins",
    )
    with patch("src.cli.plugin_loader.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["plugins"])
    assert "dummy 4.4" in out.getvalue().strip()


def test_cli_plugin_ejemplo_hola():
    ep = importlib.metadata.EntryPoint(
        name="hola",
        value="src.tests.test_cli_plugins_cmd:HolaPlugin",
        group="cobra.plugins",
    )
    with patch("src.cli.plugin_loader.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["hola"])
    assert "¡Hola desde un plugin!" in out.getvalue().strip()

