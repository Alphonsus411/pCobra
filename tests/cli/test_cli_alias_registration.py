from __future__ import annotations

import argparse

from pcobra.cobra.cli.cli import CommandRegistry
from pcobra.cobra.cli.public_command_policy import PROFILE_DEVELOPMENT, PROFILE_PUBLIC
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser


def _subparser_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    raise AssertionError(f"No se encontró acción de subparsers en {parser.prog!r}")


def _command_parser(
    *, ui: str = "v2", profile: str = PROFILE_PUBLIC
) -> tuple[CustomArgumentParser, argparse._SubParsersAction]:
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    CommandRegistry().register_base_commands(subparsers, ui=ui, profile=profile)
    return parser, subparsers


def test_aliases_legacy_de_paquete_siguen_registrados_en_cli_publica() -> None:
    _, comandos = _command_parser()

    paquete = comandos.choices["paquete"]
    acciones_paquete = _subparser_action(paquete)

    assert "instalar" in acciones_paquete.choices
    assert "extraer" in acciones_paquete.choices

    crear = acciones_paquete.choices["crear"]
    destinos_posicionales = [
        action.dest
        for action in crear._actions
        if not action.option_strings and action.dest != "help"
    ]
    assert destinos_posicionales == ["fuente", "paquete"]


def test_comandos_recomendados_de_hub_siguen_registrados_en_cli_publica() -> None:
    _, comandos = _command_parser()

    hub = comandos.choices["hub"]
    acciones_hub = _subparser_action(hub)

    assert {"publicar", "buscar", "instalar"}.issubset(acciones_hub.choices)


def test_comandos_legacy_de_modulos_siguen_registrados_en_perfil_desarrollo_v1() -> None:
    _, comandos = _command_parser(ui="v1", profile=PROFILE_DEVELOPMENT)

    modulos = comandos.choices["modulos"]
    acciones_modulos = _subparser_action(modulos)

    assert {"publicar", "buscar"}.issubset(acciones_modulos.choices)
