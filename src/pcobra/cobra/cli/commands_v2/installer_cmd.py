"""Comando público para construir instaladores Cobra."""

from __future__ import annotations

import argparse
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.services.installer_build_service import (
    register_installer_build_arguments,
    run_installer_build,
)
from pcobra.cobra_installer import CobraInstallerError


class InstallerCommandV2(BaseCommand):
    """Agrupa acciones de empaquetado instalable para proyectos Cobra."""

    name = "installer"
    capability = "codegen"

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(
            self.name,
            help="Construye instaladores/autoejecutables de proyectos Cobra",
        )
        installer_subparsers = parser.add_subparsers(
            dest="installer_action",
            parser_class=argparse.ArgumentParser,
            required=True,
        )
        build_parser = installer_subparsers.add_parser(
            "build",
            help="Construye un artefacto con PyInstaller",
        )
        register_installer_build_arguments(build_parser)
        build_parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        if getattr(args, "installer_action", None) != "build":
            raise CobraInstallerError(
                "Acción de installer no soportada. Usa: cobra installer build ."
            )
        return run_installer_build(args)
