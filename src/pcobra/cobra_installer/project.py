"""Tipos compartidos para el instalador Cobra."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


class CobraInstallerError(RuntimeError):
    """Error base para fallos controlados durante el empaquetado Cobra."""


@dataclass(frozen=True, slots=True)
class BuildOptions:
    """Opciones mínimas para construir un artefacto instalable."""

    project_root: Path | str = Path.cwd()
    entrypoint: Path | str | None = None
    output_dir: Path | str | None = None
    name: str | None = None
    target: str = "current"
    clean: bool = False
    include_dependencies: bool = True
    extra_args: Sequence[str] = field(default_factory=tuple)

    def normalized(self) -> "BuildOptions":
        """Devuelve una copia con rutas absolutas y valores derivados."""

        root = Path(self.project_root).expanduser().resolve()
        entrypoint = None
        if self.entrypoint is not None:
            raw_entrypoint = Path(self.entrypoint).expanduser()
            entrypoint = raw_entrypoint if raw_entrypoint.is_absolute() else root / raw_entrypoint
            entrypoint = entrypoint.resolve()
        output_dir = Path(self.output_dir).expanduser() if self.output_dir is not None else root / "dist"
        if not output_dir.is_absolute():
            output_dir = root / output_dir
        return BuildOptions(
            project_root=root,
            entrypoint=entrypoint,
            output_dir=output_dir.resolve(),
            name=self.name,
            target=self.target,
            clean=self.clean,
            include_dependencies=self.include_dependencies,
            extra_args=tuple(self.extra_args),
        )


@dataclass(frozen=True, slots=True)
class BuildResult:
    """Resultado estable de un proceso de construcción."""

    success: bool
    artifact_path: Path | None = None
    project_root: Path | None = None
    output_dir: Path | None = None
    target: str = "current"
    metadata: Mapping[str, object] = field(default_factory=dict)
    logs: tuple[str, ...] = ()
