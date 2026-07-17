"""Adaptadores compatibles para el resolvedor de grafos de CobraHub."""

from pathlib import Path
from typing import Mapping

from pcobra.cobra.hub.lockfile import (
    read_lockfile as _read_lockfile,
    write_lockfile as _write_lockfile,
)
from pcobra.cobra.hub.models import CobraHubResolution, LockedDependency
from pcobra.cobra.hub.errors import CobraHubError
from pcobra.cobra_installer.project import CobraInstallerError

from pcobra.cobra.hub.resolver import (
    CobraDependencyError as _HubDependencyError,
    DeclaredDependency,
    DependencyResolutionResult,
    LockedDependency,
    detect_cobra_imports,
    read_declared_dependencies,
    resolve_project_dependencies as _resolve_project_dependencies,
)


class CobraDependencyError(CobraInstallerError):
    """Excepción histórica de resolución expuesta por CobraInstaller."""


def resolve_project_dependencies(*args, **kwargs):
    """Traduce los fallos de dominio para preservar la API del Installer."""

    try:
        return _resolve_project_dependencies(*args, **kwargs)
    except _HubDependencyError as exc:
        raise CobraDependencyError(str(exc)) from exc
    except CobraHubError as exc:
        raise CobraInstallerError(str(exc)) from exc


def read_lockfile(path: str | Path) -> dict[str, LockedDependency]:
    """Conserva el punto de entrada histórico del instalador."""

    return _read_lockfile(path)


def write_lockfile(
    path: str | Path,
    resolved: Mapping[str, CobraHubResolution | LockedDependency],
    *,
    legacy_v1: bool = False,
) -> None:
    """Escribe v2, o v1 al solicitar explícitamente ``legacy_v1=True``."""

    _write_lockfile(path, resolved, version=1 if legacy_v1 else 2)

__all__ = [
    "CobraDependencyError",
    "DeclaredDependency",
    "LockedDependency",
    "DependencyResolutionResult",
    "detect_cobra_imports",
    "read_declared_dependencies",
    "read_lockfile",
    "resolve_project_dependencies",
    "write_lockfile",
]
