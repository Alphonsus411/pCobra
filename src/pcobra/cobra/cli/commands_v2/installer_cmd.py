"""Comando público para construir instaladores Cobra."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Any

import pcobra.cobra_installer as cobra_installer
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.exit_codes import CobraExitCode
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
        register_installer_build_arguments(build_parser)
        build_parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        if getattr(args, "installer_action", None) != "build":
            raise CobraInstallerError(
                "Acción de installer no soportada. Usa: cobra installer build ."
            )
        return run_installer_build(args)


def register_installer_build_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_project_path: bool = True,
    hide_target_help: bool = False,
) -> None:
    """Registra las opciones canónicas de ``installer build`` en un parser."""

    if include_project_path:
        parser.add_argument(
            "project_path",
            nargs="?",
            default=".",
            help="Ruta del proyecto Cobra a empaquetar",
        )
    target_help = (
        argparse.SUPPRESS
        if hide_target_help
        else "Sistema operativo objetivo: current, windows, linux o macos"
    )
    parser.add_argument(
        "--target",
        default="current",
        help=target_help,
    )
    parser.add_argument("--mode", choices=("onefile", "onedir"), default="onedir")
    parser.add_argument("--name", dest="name")
    parser.add_argument("--icon", dest="icon", type=Path)
    parser.add_argument(
        "--builder",
        choices=("local", "docker", "vm", "ci", "remote"),
        default="local",
    )
    parser.add_argument(
        "--install-pyinstaller",
        action="store_true",
        help="Permite instalar PyInstaller automáticamente si no está disponible",
    )
    parser.add_argument(
        "--no-open-dist",
        action="store_true",
        help="No abre la carpeta dist al terminar (comportamiento por defecto en CLI)",
    )


def run_installer_build(args: Any) -> int:
    """Ejecuta la construcción de instaladores reutilizada por aliases CLI."""

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
        message = str(exc)
        print(f"Error: {_friendly_installer_error(message)}")
        return int(_installer_exit_code(message))
    except Exception as exc:  # pragma: no cover - salvaguarda de frontera CLI
        message = str(exc).strip() or "fallo interno inesperado del instalador."
        print(f"Error: Error interno inesperado: {message}")
        return int(CobraExitCode.UNEXPECTED_INTERNAL_ERROR)

    artifact = result.artifact_path or result.output_dir or result.dist_dir
    print(f"Build completado correctamente: {artifact}")
    return int(CobraExitCode.SUCCESS)


def _friendly_installer_error(message: str) -> str:
    """Normaliza fallos frecuentes a mensajes accionables para usuarios CLI."""

    text = message.strip() or "fallo desconocido del instalador."
    lowered = text.lower()
    if _is_invalid_target_error(lowered):
        return f"Target inválido: {text}"
    if (
        "no es válida" in lowered
        or "no es válido" in lowered
        or "no se encontró entrypoint" in lowered
    ):
        return f"Proyecto inválido: {text}"
    if (
        "no existe" in lowered
        or "no es un directorio" in lowered
        or "no es una carpeta" in lowered
    ):
        return f"Dependencia o ruta inexistente: {text}"
    if "hash" in lowered or "sha256" in lowered or "checksum" in lowered:
        return f"Hash incorrecto: {text}"
    if _is_version_conflict_error(lowered):
        return f"Conflicto de versiones: {text}"
    if (
        "pyinstaller no está instalado" in lowered
        or "no está instalado o no es importable" in lowered
    ):
        return f"PyInstaller no disponible: {text}"
    if "cross-compilation" in lowered or "cross compilation" in lowered:
        return f"Cross-compilation solicitada: {text}"
    return text


def _installer_exit_code(message: str) -> CobraExitCode:
    """Clasifica errores controlados del instalador en códigos de salida estables."""

    lowered = (message or "").strip().lower()
    if _is_invalid_target_error(lowered):
        return CobraExitCode.INVALID_TARGET
    if _is_pyinstaller_unavailable_error(lowered):
        return CobraExitCode.PYINSTALLER_UNAVAILABLE
    if _is_hash_mismatch_error(lowered):
        return CobraExitCode.HASH_MISMATCH
    if _is_version_conflict_error(lowered):
        return CobraExitCode.VERSION_CONFLICT
    if _is_missing_dependency_error(lowered):
        return CobraExitCode.MISSING_DEPENDENCY
    if _is_invalid_project_error(lowered):
        return CobraExitCode.INVALID_PROJECT
    return CobraExitCode.UNEXPECTED_INTERNAL_ERROR


def _is_invalid_project_error(lowered: str) -> bool:
    return (
        "no es válida" in lowered
        or "no es válido" in lowered
        or "no se encontró entrypoint" in lowered
    )


def _is_missing_dependency_error(lowered: str) -> bool:
    return (
        "dependencia cobra no encontrada" in lowered
        or "no existe" in lowered
        or "no es un directorio" in lowered
        or "no es una carpeta" in lowered
    )


def _is_hash_mismatch_error(lowered: str) -> bool:
    return "hash" in lowered or "sha256" in lowered or "checksum" in lowered


def _is_version_conflict_error(lowered: str) -> bool:
    return (
        "conflicto de versiones" in lowered
        or "conflicto de versión" in lowered
        or "version conflict" in lowered
        or "versión incorrecta" in lowered
    )


def _is_pyinstaller_unavailable_error(lowered: str) -> bool:
    return (
        "pyinstaller no está instalado" in lowered
        or "no está instalado o no es importable" in lowered
    )


def _is_invalid_target_error(lowered: str) -> bool:
    return (
        "target inválido" in lowered
        or "target invalid" in lowered
        or "target seleccionado" in lowered
        or "target" in lowered and "no soport" in lowered
        or "invalid target" in lowered
    )
