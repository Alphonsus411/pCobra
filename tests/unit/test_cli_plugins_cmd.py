from io import StringIO
from unittest.mock import patch
import importlib.metadata
import sys

from src.cli.cli import main
from src.cli.plugin import PluginCommand
from src.cli.plugin_registry import limpiar_registro


class DummyPlugin(PluginCommand):
    name = "dummy"
    version = "8.0.0"

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

sys.modules.setdefault("src.tests.test_cli_plugins_cmd", sys.modules[__name__])


def test_cli_plugins_muestra_registro():
    ep = importlib.metadata.EntryPoint(
        name="dummy",
        value="src.tests.test_cli_plugins_cmd:DummyPlugin",
        group="cobra.plugins",
    )
    limpiar_registro()
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["plugins"])
    assert "dummy 8.0.0" in out.getvalue().strip()


def test_cli_plugin_ejemplo_hola():
    ep = importlib.metadata.EntryPoint(
        name="hola",
        value="src.tests.test_cli_plugins_cmd:HolaPlugin",
        group="cobra.plugins",
    )
    limpiar_registro()
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["hola"])
    assert "¡Hola desde un plugin!" in out.getvalue().strip()


def test_cli_plugins_sin_plugins():
    limpiar_registro()
    with patch("src.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints(())):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["plugins"])
    assert "No hay plugins instalados" in out.getvalue()

