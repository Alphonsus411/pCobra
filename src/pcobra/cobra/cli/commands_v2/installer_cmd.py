"""Comando público para construir instaladores Cobra."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Any

import pcobra.cobra_installer as cobra_installer
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra_installer import BuildOptions, CobraInstallerError


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
        build_parser.add_argument(
            "project_path",
            nargs="?",
            default=".",
            help="Ruta del proyecto Cobra a empaquetar",
        )
        build_parser.add_argument(
            "--target", choices=("windows", "linux", "macos"), required=True
        )
        build_parser.add_argument(
            "--mode", choices=("onefile", "onedir"), default="onedir"
        )
        build_parser.add_argument("--name", dest="name")
        build_parser.add_argument("--icon", dest="icon", type=Path)
        build_parser.add_argument(
            "--builder",
            choices=("local", "docker", "vm", "ci", "remote"),
            default="local",
        )
        build_parser.add_argument(
            "--install-pyinstaller",
            action="store_true",
            help="Permite instalar PyInstaller automáticamente si no está disponible",
        )
        build_parser.add_argument(
            "--no-open-dist",
            action="store_true",
            help="No abre la carpeta dist al terminar (comportamiento por defecto en CLI)",
        )
        build_parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        if getattr(args, "installer_action", None) != "build":
            raise CobraInstallerError(
                "Acción de installer no soportada. Usa: cobra installer build ."
            )

        options = BuildOptions(
            project_root=args.project_path,
            target=args.target,
            mode=args.mode,
            name=args.name,
            icon=args.icon,
            builder=args.builder,
            install_pyinstaller=bool(args.install_pyinstaller),
            log_callback=print,
        )
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", RuntimeWarning)
                result = cobra_installer.build_project(args.project_path, options)
            for warning in caught:
                print(f"Aviso: {_friendly_installer_error(str(warning.message))}")
        except CobraInstallerError as exc:
            print(f"Error: {_friendly_installer_error(str(exc))}")
            return 1

        artifact = result.artifact_path or result.output_dir or result.dist_dir
        print(f"Build completado correctamente: {artifact}")
        return 0


def _friendly_installer_error(message: str) -> str:
    """Normaliza fallos frecuentes a mensajes accionables para usuarios CLI."""

    text = message.strip() or "fallo desconocido del instalador."
    lowered = text.lower()
    if (
        "no es válida" in lowered
        or "no es válido" in lowered
        or "no se encontró entrypoint" in lowered
    ):
        return f"Proyecto inválido: {text}"
    if "no existe" in lowered or "no es un directorio" in lowered or "no es una carpeta" in lowered:
        return f"Dependencia o ruta inexistente: {text}"
    if "hash" in lowered or "sha256" in lowered or "checksum" in lowered:
        return f"Hash incorrecto: {text}"
    if "conflicto de versiones" in lowered or "version conflict" in lowered:
        return f"Conflicto de versiones: {text}"
    if (
        "pyinstaller no está instalado" in lowered
        or "no está instalado o no es importable" in lowered
    ):
        return f"PyInstaller no disponible: {text}"
    if "cross-compilation" in lowered or "cross compilation" in lowered:
        return f"Cross-compilation solicitada: {text}"
    return text
