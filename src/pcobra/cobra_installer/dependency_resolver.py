"""Adaptador compatible para el resolvedor de grafos de CobraHub."""

from pcobra.cobra.hub.resolver import (
    CobraDependencyError,
    DeclaredDependency,
    DependencyResolutionResult,
    LockedDependency,
    detect_cobra_imports,
    read_declared_dependencies,
    read_lockfile,
    resolve_project_dependencies,
    write_lockfile,
)

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
