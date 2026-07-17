"""Modelos neutrales compartidos por CobraHub y CobraInstaller."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class CobraHubResolution:
    """Paquete Cobra localizado, validado y acompañado de metadatos Hub v2."""

    name: str
    version: str
    path: Path
    sha256: str
    source: str
    dependencies: dict[str, str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeclaredDependency:
    """Dependencia declarada por el usuario en ``cobra.toml``."""

    name: str
    version: str
    source: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LockedDependency:
    """Entrada normalizada procedente de ``cobra.lock``."""

    name: str
    version: str
    sha256: str | None = None
    source: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DependencyResolutionResult:
    """Resultado enriquecido v2 de resolver el grafo de un proyecto."""

    declared: dict[str, DeclaredDependency]
    used_imports: set[str]
    resolved: dict[str, CobraHubResolution]
    lockfile_path: Path
    lockfile_created: bool = False
    conflicts: tuple[str, ...] = ()
    missing_declarations: tuple[str, ...] = ()
    dependency_chains: Mapping[str, str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
