"""Abstracciones internas para builders de cobra_installer.

La arquitectura separa la selección del entorno de build de la orquestación del
proyecto. Por ahora solo el builder local ejecuta PyInstaller directamente en el
host; docker/vm/ci/remote quedan reservados para implementaciones futuras.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

from .logger import BuildLogger
from .project import BuildOptions, CobraInstallerError
from .pyinstaller_runner import PyInstallerRunResult, run_pyinstaller
from .targets import BuilderKind

_RESERVED_BUILDERS = {
    BuilderKind.DOCKER: "Docker",
    BuilderKind.VM: "máquina virtual",
    BuilderKind.CI: "runner CI/CD",
    BuilderKind.REMOTE: "builder remoto",
}


@runtime_checkable
class BuildBackend(Protocol):
    """Contrato mínimo para ejecutar el paso backend de un build Cobra."""

    kind: BuilderKind

    def run_pyinstaller(
        self, spec_path: Path, options: BuildOptions, logger: BuildLogger
    ) -> PyInstallerRunResult:
        """Ejecuta PyInstaller o una estrategia equivalente para generar el artefacto."""


@dataclass(frozen=True, slots=True)
class LocalPyInstallerBuilder:
    """Backend local que delega el empaquetado en PyInstaller sobre el host actual."""

    kind: BuilderKind = BuilderKind.LOCAL
    runner: Callable[[Path, BuildOptions, BuildLogger], PyInstallerRunResult] = (
        run_pyinstaller
    )

    def run_pyinstaller(
        self, spec_path: Path, options: BuildOptions, logger: BuildLogger
    ) -> PyInstallerRunResult:
        """Ejecuta PyInstaller localmente usando las opciones normalizadas."""

        return self.runner(spec_path, options, logger)


def resolve_build_backend(kind: BuilderKind | str | None) -> BuildBackend:
    """Devuelve el backend implementado o falla con un mensaje explícito.

    Los builders docker/vm/ci/remote se aceptan como valores reservados para que
    la API pública ya refleje la arquitectura prevista, pero todavía no pueden
    ejecutar builds.
    """

    builder_kind = BuilderKind.from_value(kind)
    if builder_kind is BuilderKind.LOCAL:
        return LocalPyInstallerBuilder()

    planned = _RESERVED_BUILDERS[builder_kind]
    reserved = ", ".join(item.value for item in BuilderKind)
    raise CobraInstallerError(
        "Builder no disponible todavía: "
        f"{builder_kind.value!r}. La arquitectura de cobra_installer ya está "
        f"preparada para builders ({reserved}), pero el builder basado en "
        f"{planned} todavía no está implementado. Usa builder='local' por ahora."
    )


__all__ = [
    "BuildBackend",
    "BuilderKind",
    "LocalPyInstallerBuilder",
    "resolve_build_backend",
]
