from __future__ import annotations

import argparse

from pcobra.cobra.cli.cli import AppConfig, CommandRegistry


EXPECTED_PUBLIC_V2_COMMANDS = {"run", "build", "test", "mod", "repl"}


def test_app_config_v2_routes_include_repl_command_v2() -> None:
    routes = {
        (route.module_path, route.class_name)
        for route in AppConfig.V2_COMMAND_ROUTES
    }

    assert (
        "pcobra.cobra.cli.commands_v2.repl_cmd",
        "ReplCommandV2",
    ) in routes


def test_app_config_v2_routes_do_not_expose_interactive_as_public_command() -> None:
    route_modules = {route.module_path for route in AppConfig.V2_COMMAND_ROUTES}
    route_classes = {route.class_name for route in AppConfig.V2_COMMAND_ROUTES}

    assert "pcobra.cobra.cli.commands.interactive_cmd" not in route_modules
    assert "InteractiveCommand" not in route_classes


def test_public_v2_subcommands_match_contract_exactly() -> None:
    registry = CommandRegistry()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    commands = registry.register_base_commands(
        subparsers,
        ui="v2",
        profile="public",
    )

    assert set(commands) == EXPECTED_PUBLIC_V2_COMMANDS
