"""Orquestación principal de construcción fuera del IDLE."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Mapping, Sequence

import pcobra

from .builders import LocalPyInstallerBuilder, resolve_build_backend
from .logger import BuildLogger, emit_many
from pcobra.cobra.hub.models import DependencyResolutionResult

from .dependency_resolver import resolve_project_dependencies
from .manifest import create_manifest, expected_artifact_path
from .project import (
    BuildOptions,
    BuildResult,
    CobraInstallerError,
    CobraProject,
    discover_project,
)
from .pyinstaller_runner import run_pyinstaller
from .spec_writer import SpecBuildContext, write_spec
from .transpile import TranspileResult, transpile_project
from .validator import validate_build_options, validate_project

__all__ = [
    "RuntimePreparationResult",
    "build_project",
    "package_current_project",
    "prepare_runtime",
]


@dataclass(frozen=True, slots=True)
class RuntimePreparationResult:
    """Resultado estable de preparar el runtime que consumirá PyInstaller."""

    build_dir: Path
    runtime_dir: Path
    corelibs_dir: Path
    standard_library_dir: Path
    cobra_dir: Path
    packages_dir: Path
    assets_dir: Path
    config_dir: Path
    documentation_dir: Path
    auxiliary_dir: Path
    entrypoint: Path
    copied_resources: Mapping[str, tuple[Path, ...]] = field(default_factory=dict)
    dependency_resolution: DependencyResolutionResult | None = None
    logs: tuple[str, ...] = ()


def prepare_runtime(
    build_dir: str | Path,
    project: CobraProject,
    dependencies: DependencyResolutionResult | Sequence[Path | str] | None,
    options: BuildOptions,
) -> RuntimePreparationResult:
    """Prepara un árbol mínimo de runtime Cobra listo para PyInstaller.

    Copia de forma selectiva las piezas necesarias para ejecutar código Cobra:
    ``pcobra/core``, ``pcobra/corelibs``, ``pcobra/standard_library`` y una
    superficie acotada de ``pcobra/cobra``. Además empaqueta recursos del
    proyecto, paquetes ``.co`` locales o resueltos por CobraHub, y genera un
    ``pyinstaller_entrypoint.py`` determinista que ajusta ``sys.path`` antes de
    ejecutar el entrypoint Python generado o, si aún no existe, el entrypoint
    Cobra mediante la CLI pública.
    """

    normalized_project = project.normalized()
    normalized_options = options.normalized()
    root = Path(normalized_project.project_root)
    target = Path(build_dir).expanduser().resolve()
    if normalized_options.clean and target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    runtime_root = target / "runtime"
    pcobra_runtime = runtime_root / "pcobra"
    packages_dir = target / "packages"
    assets_dir = target / "assets"
    config_dir = target / "config"
    documentation_dir = target / "docs"
    auxiliary_dir = target / "resources"
    for directory in (
        pcobra_runtime,
        packages_dir,
        assets_dir,
        config_dir,
        documentation_dir,
        auxiliary_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    runtime_copies = _copy_pcobra_runtime(pcobra_runtime)

    dependency_resolution: DependencyResolutionResult | None = None
    if isinstance(dependencies, DependencyResolutionResult):
        dependency_resolution = dependencies
    elif dependencies is None and normalized_options.include_dependencies:
        dependency_resolution = resolve_project_dependencies(root)

    copied_hub_packages = _copy_hub_packages(dependency_resolution, packages_dir)
    copied_explicit_packages = _copy_dependency_paths(dependencies, packages_dir, root)
    copied_project_packages = _copy_many(
        normalized_project.co_packages, packages_dir, root
    )
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
    entrypoint = target / "pyinstaller_entrypoint.py"
    source_entrypoint = normalized_project.entrypoint or normalized_options.entrypoint
    entrypoint.write_text(
        _pyinstaller_entrypoint_code(source_entrypoint, target), encoding="utf-8"
    )

    return RuntimePreparationResult(
        build_dir=target,
        runtime_dir=pcobra_runtime,
        corelibs_dir=pcobra_runtime / "corelibs",
        standard_library_dir=pcobra_runtime / "standard_library",
        cobra_dir=pcobra_runtime / "cobra",
        packages_dir=packages_dir,
        assets_dir=assets_dir,
        config_dir=config_dir,
        documentation_dir=documentation_dir,
        auxiliary_dir=auxiliary_dir,
        entrypoint=entrypoint,
        copied_resources={
            "runtime": runtime_copies,
            "packages": (
                *copied_hub_packages,
                *copied_explicit_packages,
                *copied_project_packages,
            ),
            "assets": copied_assets,
            "config": copied_config,
            "documentation": copied_docs,
            "auxiliary": copied_auxiliary,
            "entrypoint": (entrypoint,),
        },
        dependency_resolution=dependency_resolution,
        logs=(
            f"Runtime Cobra copiado en {pcobra_runtime}.",
            f"Entrypoint Python para PyInstaller creado en {entrypoint}.",
        ),
    )


def build_project(
    project_path: Path | str | BuildOptions | None = None,
    options: BuildOptions | None = None,
    **overrides: object,
) -> BuildResult:
    """Construye un proyecto Cobra completo y devuelve la ruta de ``dist``.

    El flujo orquesta las piezas públicas del instalador: descubre el proyecto,
    valida su estructura, lee ``cobra.toml``, lee o genera ``cobra.lock`` al
    resolver dependencias CobraHub, transpila con el backend Python oficial,
    ensambla runtime, genera ``.spec``, ejecuta PyInstaller y escribe el
    manifiesto final. El progreso se emite en tiempo real mediante
    ``BuildOptions.log_callback`` para que CLI e IDLE puedan mostrarlo sin
    acoplarse a esta implementación.

    Por compatibilidad, el primer argumento puede seguir siendo un
    ``BuildOptions``. La forma recomendada es
    ``build_project(project_path, options)``.
    """

    if isinstance(project_path, BuildOptions) and options is None:
        base = project_path
    else:
        base = options or BuildOptions(project_root=project_path or Path.cwd())
        if project_path is not None:
            base = replace(base, project_root=project_path)
    if overrides:
        base = replace(base, **overrides)
    normalized = validate_build_options(base)
    build_backend = resolve_build_backend(normalized.builder)
    if isinstance(build_backend, LocalPyInstallerBuilder):
        build_backend = LocalPyInstallerBuilder(runner=run_pyinstaller)
    logger = BuildLogger(legacy_callback=normalized.log_callback)
    logs: list[str] = []

    total_steps = 10

    def step(stage: str, message: str, number: int) -> None:
        logs.append(message)
        logger.step(message, stage=stage, step=number, total_steps=total_steps)

    step("deteccion_proyecto", "1/12 Descubriendo proyecto Cobra...", 1)
    project = discover_project(Path(normalized.project_root))
    if normalized.entrypoint and project.entrypoint != normalized.entrypoint:
        project = CobraProject(
            project_root=project.project_root,
            entrypoint=normalized.entrypoint,
            cobra_toml=project.cobra_toml,
            cobra_lock=project.cobra_lock,
            assets=project.assets,
            config=project.config,
            co_packages=project.co_packages,
            documentation=project.documentation,
            config_dirs=project.config_dirs,
            auxiliary_resources=project.auxiliary_resources,
        ).normalized()

    step("validacion", "Validando estructura del proyecto...", 2)
    validation = validate_project(project)
    if not validation.is_valid:
        detail = "; ".join(error.message for error in validation.errors)
        raise CobraInstallerError(f"La estructura del proyecto no es válida: {detail}")

    logger.info("Leyendo cobra.toml...", stage="validacion")
    config = dict(project.config)
    normalized = replace(normalized, config={**config, **dict(normalized.config)})

    logger.info("Leyendo o generando cobra.lock...", stage="resolucion_dependencias")
    logger.info(
        "Detectando imports Cobra no declarados...", stage="resolucion_dependencias"
    )
    step("resolucion_dependencias", "Resolviendo dependencias CobraHub...", 3)
    dependencies = None
    if normalized.include_dependencies:
        dependencies = resolve_project_dependencies(Path(project.project_root))
        if dependencies.lockfile_created:
            project = replace(
                project, cobra_lock=dependencies.lockfile_path
            ).normalized()
            logger.info(
                f"cobra.lock generado en {dependencies.lockfile_path}.",
                stage="descarga_cache_cobrahub",
            )
    step("descarga_cache_cobrahub", "Descarga/cache CobraHub preparada.", 4)

    build_dir = Path(normalized.temp_dir or Path(normalized.project_root) / "build")
    if normalized.clean and build_dir.exists():
        shutil.rmtree(build_dir)

    logger.info("Preparando carpeta temporal...", stage="preparacion_runtime")
    build_dir.mkdir(parents=True, exist_ok=True)

    step("transpilacion", "Transpilando con el backend Python oficial...", 5)
    transpiled = transpile_project(project, build_dir, normalized, dependencies)
    logs.extend(transpiled.logs)
    emit_many(logger, transpiled.logs, stage="transpilacion")

    step("preparacion_runtime", "Preparando runtime Cobra...", 6)
    runtime = _runtime_from_transpile(transpiled)

    output_dir = Path(normalized.output_dir or Path(normalized.project_root) / "dist")
    output_dir.mkdir(parents=True, exist_ok=True)
    name = normalized.name or Path(project.entrypoint or transpiled.generated_code).stem

    step("generacion_spec", "Generando especificación .spec de PyInstaller...", 7)
    spec_path = write_spec(
        SpecBuildContext(
            options=normalized,
            runtime=runtime,
            output_dir=output_dir,
            executable_name=name,
        )
    )

    step("ejecucion_pyinstaller", "Ejecutando PyInstaller...", 8)
    pyinstaller = build_backend.run_pyinstaller(spec_path, normalized, logger)

    step("escritura_manifiesto", "Escribiendo manifiesto de build...", 9)
    manifest_path = create_manifest(
        normalized, Path(project.entrypoint), output_dir, name
    )
    logs.append(f"Manifiesto generado en {manifest_path}.")
    logger.info(
        f"Manifiesto generado en {manifest_path}.", stage="escritura_manifiesto"
    )
    step("finalizacion", "Build Cobra finalizado correctamente.", 10)

    return BuildResult(
        success=True,
        artifact_path=expected_artifact_path(output_dir, name, normalized),
        project_root=Path(normalized.project_root),
        output_dir=output_dir,
        target=normalized.target,
        architecture=normalized.architecture,
        builder=normalized.builder,
        builder_config=normalized.builder_config,
        mode=normalized.mode,
        executable_name=name,
        temp_dir=build_dir,
        dist_dir=output_dir,
        pyinstaller_version=pyinstaller.version,
        metadata={
            "entrypoint": str(project.entrypoint),
            "generated_code": str(transpiled.generated_code),
            "manifest": str(manifest_path),
            "spec": str(spec_path),
            "name": name,
            "pyinstaller_command": list(pyinstaller.command),
        },
        logs=tuple(logs),
    )


def package_current_project(
    project_root: str | Path | None = None, **kwargs: object
) -> BuildResult:
    """Empaqueta el proyecto actual; punto único que debe llamar el IDLE."""

    options = BuildOptions(project_root=project_root or Path.cwd(), **kwargs)
    return build_project(options)


def _runtime_from_transpile(transpile: TranspileResult) -> RuntimePreparationResult:
    return RuntimePreparationResult(
        build_dir=transpile.build_dir,
        runtime_dir=transpile.runtime_dir,
        corelibs_dir=transpile.corelibs_dir,
        standard_library_dir=transpile.runtime_dir / "standard_library",
        cobra_dir=transpile.runtime_dir / "cobra",
        packages_dir=transpile.packages_dir,
        assets_dir=transpile.assets_dir,
        config_dir=transpile.config_dir,
        documentation_dir=transpile.documentation_dir,
        auxiliary_dir=transpile.auxiliary_dir,
        entrypoint=transpile.entrypoint,
        copied_resources=transpile.copied_resources,
        dependency_resolution=transpile.dependency_resolution,
        logs=transpile.logs,
    )


def _copy_pcobra_runtime(destination_root: Path) -> tuple[Path, ...]:
    pcobra_root = Path(pcobra.__file__).resolve().parent
    copied: list[Path] = []
    for filename in ("__init__.py", "__main__.py", "cli.py"):
        source = pcobra_root / filename
        if source.is_file():
            destination = destination_root / filename
            _copy_path(source, destination)
            copied.append(destination)
    for name in ("_stubs", "core", "corelibs", "standard_library"):
        source = pcobra_root / name
        if source.exists():
            destination = destination_root / name
            _copy_path(source, destination)
            copied.append(destination)
    source_layout = _create_runtime_source_layout(destination_root)
    if source_layout is not None:
        copied.append(source_layout)
    cobra_root = destination_root / "cobra"
    cobra_root.mkdir(parents=True, exist_ok=True)
    cobra_source = pcobra_root / "cobra"
    for filename in ("__init__.py", "packaging.py", "usar_loader.py", "usar_policy.py"):
        source = cobra_source / filename
        if source.is_file():
            destination = cobra_root / filename
            _copy_path(source, destination)
            copied.append(destination)
    for name in _RUNTIME_COBRA_SUBPACKAGES:
        source = cobra_source / name
        if source.exists():
            destination = cobra_root / name
            _copy_path(source, destination)
            copied.append(destination)
    return tuple(copied)


def _create_runtime_source_layout(destination_root: Path) -> Path | None:
    """Crea la ruta ``src/pcobra`` esperada por contratos de arranque.

    Algunos contratos internos validan rutas históricas ``src/pcobra/...`` en
    tiempo de importación. En el árbol de PyInstaller el paquete vive bajo
    ``runtime/pcobra``; por eso se crea una réplica mínima y filtrada solo de
    las bibliotecas canónicas consultadas por esos contratos.
    """

    source_layout = destination_root.parent.parent / "src" / "pcobra"
    copied = False
    for name in ("corelibs", "standard_library"):
        source = destination_root / name
        if source.exists():
            _copy_path(source, source_layout / name)
            copied = True
    return source_layout if copied else None


def _copy_hub_packages(
    resolution: DependencyResolutionResult | None, packages_dir: Path
) -> tuple[Path, ...]:
    if resolution is None:
        return ()
    copied: list[Path] = []
    for package in resolution.resolved.values():
        destination = packages_dir / package.path.name
        _copy_path(package.path, destination)
        copied.append(destination)
    return tuple(copied)


def _copy_dependency_paths(
    dependencies: DependencyResolutionResult | Sequence[Path | str] | None,
    packages_dir: Path,
    project_root: Path,
) -> tuple[Path, ...]:
    if dependencies is None or isinstance(dependencies, DependencyResolutionResult):
        return ()
    return _copy_many(dependencies, packages_dir, project_root)


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
        shutil.copytree(source, destination, ignore=_ignore_runtime_noise)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _ignore_runtime_noise(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path_name = Path(name)
        if name in _IGNORED_NAMES or path_name.suffix in _IGNORED_SUFFIXES:
            ignored.add(name)
    return ignored


def _relative_or_name(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)


def _existing_optional_paths(*paths: Path | str | None) -> tuple[Path | str, ...]:
    return tuple(path for path in paths if path is not None and Path(path).exists())


def _pyinstaller_entrypoint_code(
    source_entrypoint: Path | None, build_dir: Path
) -> str:
    source_literal = str(source_entrypoint) if source_entrypoint is not None else ""
    return (
        '"""Entrypoint estable generado por cobra_installer para PyInstaller."""\n'
        "from __future__ import annotations\n\n"
        "import runpy\n"
        "import sys\n"
        "from pathlib import Path\n\n"
        "BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))\n"
        "for relative in ('runtime', 'packages', 'python'):\n"
        "    candidate = BASE_DIR / relative\n"
        "    if candidate.exists():\n"
        "        sys.path.insert(0, str(candidate))\n\n"
        "generated_main = BASE_DIR / 'python' / '__main__.py'\n"
        "if generated_main.is_file():\n"
        "    runpy.run_path(str(generated_main), run_name='__main__')\n"
        "else:\n"
        f"    source_entrypoint = Path({source_literal!r})\n"
        "    if not source_entrypoint.is_file():\n"
        "        raise SystemExit('No se encontró entrypoint Python generado ni fuente Cobra original.')\n"
        "    from pcobra.cobra.cli.cli import main as cobra_main\n"
        "    raise SystemExit(cobra_main(['ejecutar', str(source_entrypoint)]))\n"
    )


_RUNTIME_COBRA_SUBPACKAGES = (
    # Importados por pcobra.__init__ y por las rutas de resolución/transpilación
    # usadas por `pcobra.cobra.cli.cli ejecutar`.
    "architecture",
    "backends",
    "bindings",
    "build",
    "cli",
    "config",
    "core",
    "imports",
    "macro",
    "semantico",
    "stdlib_contract",
    "transpilers",
)

_IGNORED_NAMES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "benchmarks",
    "docs",
    "documentation",
    "examples",
    "node_modules",
    "tests",
    "venv",
}
_IGNORED_SUFFIXES = {".md", ".pyc", ".pyo"}
