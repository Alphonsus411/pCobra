import importlib
import sys

# Import modules from cobra
cobra_cli_pkg = importlib.import_module("cobra.cli")
cobra_init = importlib.import_module("cobra.cli.commands.init_cmd")
cobra_semver = importlib.import_module("cobra.cli.utils.semver")

# Ensure relative imports map to the same modules
sys.modules.setdefault("cli", cobra_cli_pkg)
sys.modules.setdefault("cli.commands.init_cmd", cobra_init)
sys.modules.setdefault("cli.utils.semver", cobra_semver)

from cli.commands.init_cmd import InitCommand as InitCommand_cli
from cobra.cli.commands.init_cmd import InitCommand as InitCommand_cobra

from cli.utils.semver import es_version_valida as es_version_cli
from cobra.cli.utils.semver import es_version_valida as es_version_cobra


def test_init_command_is_same_module():
    assert InitCommand_cli is InitCommand_cobra


def test_semver_function_is_same_module():
    assert es_version_cli is es_version_cobra
