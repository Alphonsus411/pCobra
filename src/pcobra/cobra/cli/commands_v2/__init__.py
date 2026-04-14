from os import environ

from pcobra.cobra.cli.commands_v2.build_cmd import BuildCommandV2
from pcobra.cobra.cli.commands_v2.mod_cmd import ModCommandV2
from pcobra.cobra.cli.commands_v2.run_cmd import RunCommandV2
from pcobra.cobra.cli.commands_v2.test_cmd import TestCommandV2

COBRA_ENABLE_LEGACY_CLI_ENV = "COBRA_ENABLE_LEGACY_CLI"


def is_legacy_cli_enabled() -> bool:
    return environ.get(COBRA_ENABLE_LEGACY_CLI_ENV, "").strip() == "1"


if is_legacy_cli_enabled():
    from pcobra.cobra.cli.commands_v2.legacy_cmd import LegacyCommandGroupV2
else:
    LegacyCommandGroupV2 = None

__all__ = [
    "RunCommandV2",
    "BuildCommandV2",
    "TestCommandV2",
    "ModCommandV2",
    "LegacyCommandGroupV2",
    "COBRA_ENABLE_LEGACY_CLI_ENV",
    "is_legacy_cli_enabled",
]
