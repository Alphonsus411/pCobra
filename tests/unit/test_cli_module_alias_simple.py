import importlib
import sys

# Import modules from pcobra
pcobra_cli_pkg = importlib.import_module("pcobra.cli")
pcobra_init = importlib.import_module("pcobra.cli.commands.init_cmd")
pcobra_semver = importlib.import_module("pcobra.cli.utils.semver")

# Ensure relative imports map to the same modules
sys.modules.setdefault("cli", pcobra_cli_pkg)
sys.modules.setdefault("cli.commands.init_cmd", pcobra_init)
sys.modules.setdefault("cli.utils.semver", pcobra_semver)

from cli.commands.init_cmd import InitCommand as InitCommand_cli
from pcobra.cli.commands.init_cmd import InitCommand as InitCommand_pcobra

from cli.utils.semver import es_version_valida as es_version_cli
from pcobra.cli.utils.semver import es_version_valida as es_version_pcobra


def test_init_command_is_same_module():
    assert InitCommand_cli is InitCommand_pcobra


def test_semver_function_is_same_module():
    assert es_version_cli is es_version_pcobra
