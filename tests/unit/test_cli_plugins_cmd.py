from io import StringIO
from unittest.mock import patch
import importlib.metadata
import sys

from cobra.cli.cli import main
from pcobra.cobra.cli.plugin import PluginCommand as CanonicalPluginCommand
from pcobra.cobra.cli.plugin_registry import limpiar_registro


class DummyPlugin(CanonicalPluginCommand):
    name = "dummy"
    version = "10.0.12"

    def register_subparser(self, subparsers):
        pass

    def run(self, args):
        pass


class HolaPlugin(CanonicalPluginCommand):
    name = "hola"
    version = "1.0"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)

    def run(self, args):
        print("¡Hola desde un plugin!")


sys.modules.setdefault("tests.test_cli_plugins_cmd", sys.modules[__name__])


def test_cli_plugins_muestra_registro(monkeypatch):
    from pcobra.cobra.cli.cli import AppConfig
    from pcobra.cobra.cli.commands.plugins_cmd import PluginsCommand

    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    monkeypatch.setattr(AppConfig, "BASE_COMMAND_CLASSES", [PluginsCommand])
    ep = importlib.metadata.EntryPoint(
        name="dummy",
        value="tests.test_cli_plugins_cmd:DummyPlugin",
        group="cobra.plugins",
    )
    limpiar_registro()
    with patch(
        "pcobra.cobra.cli.plugin.entry_points",
        return_value=importlib.metadata.EntryPoints((ep,)),
    ):
        with patch("sys.stdout", new_callable=StringIO) as out:
            assert main(
                [
                    "--plugins-allowlist",
                    "tests.test_cli_plugins_cmd:DummyPlugin",
                    "plugins",
                ]
            ) == 0
    assert "dummy 10.0.12" in out.getvalue().strip()


def test_cli_plugin_ejemplo_hola(monkeypatch):
    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    ep = importlib.metadata.EntryPoint(
        name="hola",
        value="tests.test_cli_plugins_cmd:HolaPlugin",
        group="cobra.plugins",
    )
    limpiar_registro()
    with patch(
        "pcobra.cobra.cli.plugin.entry_points",
        return_value=importlib.metadata.EntryPoints((ep,)),
    ):
        with patch("sys.stdout", new_callable=StringIO) as out:
            assert main(
                ["--plugins-allowlist", "tests.test_cli_plugins_cmd:HolaPlugin", "hola"]
            ) == 0
    assert "¡Hola desde un plugin!" in out.getvalue().strip()


def test_cli_plugins_sin_plugins():
    limpiar_registro()
    with patch(
        "cobra.cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints(())
    ):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["plugins"])
    assert "No hay plugins instalados" in out.getvalue()
