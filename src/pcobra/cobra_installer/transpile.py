"""Transpilación de proyectos Cobra a una carpeta temporal de build.

Este módulo prepara el árbol intermedio que consumen los empaquetadores: código
Python generado con el backend oficial, entrypoint Python, runtime/corelibs y los
recursos del proyecto necesarios para ejecutar la aplicación fuera del árbol de
fuentes original.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

import pcobra

from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.cli.execution_pipeline import prevalidar_y_parsear_codigo

from .dependency_resolver import DependencyResolutionResult, resolve_project_dependencies
from .project import BuildOptions, CobraInstallerError, CobraProject

__all__ = ["TranspileResult", "transpile_project"]


@dataclass(frozen=True, slots=True)
class TranspileResult:
    """Resultado estable de preparar un proyecto Cobra transpilado a Python."""

    build_dir: Path
    generated_code: Path
    entrypoint: Path
    runtime_dir: Path
    corelibs_dir: Path
    packages_dir: Path
    assets_dir: Path
    config_dir: Path
    documentation_dir: Path
    auxiliary_dir: Path
    copied_resources: Mapping[str, tuple[Path, ...]] = field(default_factory=dict)
    dependency_resolution: DependencyResolutionResult | None = None
    logs: tuple[str, ...] = ()


def transpile_project(
    project: CobraProject, build_dir: Path, options: BuildOptions
) -> TranspileResult:
    """Transpila ``project`` a Python y prepara sus recursos en ``build_dir``.

    La generación de Python reutiliza el adaptador oficial ``PythonAdapter`` que
    envuelve ``TranspiladorPython``. La función no modifica Lexer, Parser, AST ni
    transpiladores: sólo invoca el pipeline público existente para obtener el AST
    y después delega al backend Python oficial.
    """

    normalized_project = project.normalized()
    normalized_options = options.normalized()
    root = Path(normalized_project.project_root)
    entrypoint = Path(
        normalized_project.entrypoint or normalized_options.entrypoint or root / "main.cobra"
    )
    if not entrypoint.is_file():
        raise CobraInstallerError(f"El entrypoint Cobra no existe: {entrypoint}")

    target = Path(build_dir).expanduser().resolve()
    if normalized_options.clean and target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    python_dir = target / "python"
    runtime_dir = target / "runtime" / "pcobra"
    packages_dir = target / "packages"
    assets_dir = target / "assets"
    config_dir = target / "config"
    documentation_dir = target / "docs"
    auxiliary_dir = target / "resources"
    for directory in (
        python_dir,
        runtime_dir,
        packages_dir,
        assets_dir,
        config_dir,
        documentation_dir,
        auxiliary_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    source = entrypoint.read_text(encoding="utf-8")
    ast = prevalidar_y_parsear_codigo(source)
    generated = PythonAdapter().compile(
        ast,
        {"source_file": entrypoint, "project_root": root},
    )
    generated_path = python_dir / f"{entrypoint.stem}.py"
    generated_path.write_text(generated, encoding="utf-8")

    final_entrypoint = python_dir / "__main__.py"
    final_entrypoint.write_text(_entrypoint_code(generated_path.name), encoding="utf-8")

    copied_runtime = _copy_runtime(runtime_dir)
    dependency_resolution = None
    copied_packages: tuple[Path, ...] = ()
    if normalized_options.include_dependencies:
        dependency_resolution = resolve_project_dependencies(root)
        copied_packages = _copy_hub_packages(dependency_resolution, packages_dir)

    copied_assets = _copy_many(
        (*normalized_project.assets, *normalized_options.assets), assets_dir, root
    )
    copied_config = _copy_many(normalized_project.config_dirs, config_dir, root)
    copied_docs = _copy_many(normalized_project.documentation, documentation_dir, root)
    copied_auxiliary = _copy_many(
        _existing_optional_paths(
            normalized_project.cobra_toml,
            normalized_project.cobra_lock,
            *normalized_project.auxiliary_resources,
        ),
        auxiliary_dir,
        root,
    )
    copied_co_packages = _copy_many(normalized_project.co_packages, packages_dir, root)

    logs = (
        f"Código Python generado en {generated_path}.",
        f"Entrypoint Python final creado en {final_entrypoint}.",
        f"Runtime Cobra copiado en {runtime_dir}.",
    )
    return TranspileResult(
        build_dir=target,
        generated_code=generated_path,
        entrypoint=final_entrypoint,
        runtime_dir=runtime_dir,
        corelibs_dir=runtime_dir / "corelibs",
        packages_dir=packages_dir,
        assets_dir=assets_dir,
        config_dir=config_dir,
        documentation_dir=documentation_dir,
        auxiliary_dir=auxiliary_dir,
        copied_resources={
            "runtime": copied_runtime,
            "packages": (*copied_packages, *copied_co_packages),
            "assets": copied_assets,
            "config": copied_config,
            "documentation": copied_docs,
            "auxiliary": copied_auxiliary,
        },
        dependency_resolution=dependency_resolution,
        logs=logs,
    )


def _entrypoint_code(module_filename: str) -> str:
    return (
        '"""Entrypoint Python generado por cobra_installer."""\n'
        "from __future__ import annotations\n\n"
        "import runpy\n"
        "from pathlib import Path\n\n"
        "if __name__ == '__main__':\n"
        "    runpy.run_path(\n"
        f"        str(Path(__file__).with_name({module_filename!r})), run_name='__main__'\n"
        "    )\n"
    )


def _copy_runtime(runtime_dir: Path) -> tuple[Path, ...]:
    pcobra_root = Path(pcobra.__file__).resolve().parent
    copied: list[Path] = []
    for name in ("cobra", "corelibs", "standard_library", "core", "_stubs"):
        source = pcobra_root / name
        if source.exists():
            destination = runtime_dir / name
            _copy_path(source, destination)
            copied.append(destination)
    init_source = pcobra_root / "__init__.py"
    if init_source.exists():
        destination = runtime_dir / "__init__.py"
        shutil.copy2(init_source, destination)
        copied.append(destination)
    return tuple(copied)


def _copy_hub_packages(
    resolution: DependencyResolutionResult, packages_dir: Path
) -> tuple[Path, ...]:
    copied: list[Path] = []
    for package in resolution.resolved.values():
        destination = packages_dir / package.path.name
        shutil.copy2(package.path, destination)
        copied.append(destination)
    return tuple(copied)


def _copy_many(
    paths: Sequence[Path | str], destination_root: Path, project_root: Path
) -> tuple[Path, ...]:
    copied: list[Path] = []
    seen: set[Path] = set()
    for raw in paths:
        source = Path(raw).expanduser().resolve()
        if source in seen or not source.exists():
            continue
        seen.add(source)
        destination = destination_root / _relative_or_name(source, project_root)
        _copy_path(source, destination)
        copied.append(destination)
    return tuple(copied)


def _copy_path(source: Path, destination: Path) -> None:
    if source.is_dir():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", ".pytest_cache", ".mypy_cache"
            ),
        )
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _relative_or_name(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)


def _existing_optional_paths(*paths: Path | str | None) -> tuple[Path | str, ...]:
    return tuple(path for path in paths if path is not None)
