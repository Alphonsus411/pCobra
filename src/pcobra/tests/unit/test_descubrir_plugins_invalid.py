import sys
from unittest.mock import patch
import importlib.metadata

# Ensure CLI modules are importable
import cobra.cli as cobra_cli
import cobra.cli.commands as cobra_cmds
import cobra.cli.plugin_registry as cobra_reg
sys.modules.setdefault("cli", cobra_cli)
sys.modules.setdefault("cli.commands", cobra_cmds)
sys.modules.setdefault("cli.plugin_registry", cobra_reg)

from cli.plugin import descubrir_plugins
from cli.plugin_registry import obtener_registro, limpiar_registro
from tests.fake_plugins import GoodPlugin, NotPlugin, BadInitPlugin


def test_descubrir_plugins_varios_invalidos(caplog):
    ep_good = importlib.metadata.EntryPoint(
        name="good",
        value="tests.fake_plugins:GoodPlugin",
        group="cobra.plugins",
    )
    ep_bad = importlib.metadata.EntryPoint(
        name="bad",
        value="tests.fake_plugins:NotPlugin",
        group="cobra.plugins",
    )
    ep_crash = importlib.metadata.EntryPoint(
        name="crash",
        value="tests.fake_plugins:BadInitPlugin",
        group="cobra.plugins",
    )
    eps = importlib.metadata.EntryPoints((ep_good, ep_bad, ep_crash))
    with patch("cli.plugin.entry_points", return_value=eps):
        limpiar_registro()
        with caplog.at_level("WARNING"):
            plugins = descubrir_plugins()
    # Only the valid plugin should be returned
    assert [p.__class__ for p in plugins] == [GoodPlugin]
    # Registry only contains the valid plugin
    assert obtener_registro() == {"good": "1.0"}
    # Errors for the invalid plugins should have been logged
    assert any("no implementa PluginInterface" in r.message for r in caplog.records)
    assert any("Error instanciando plugin" in r.message for r in caplog.records)
