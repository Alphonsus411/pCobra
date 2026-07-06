"""Orquestación principal de construcción fuera del IDLE."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Mapping, Sequence

import pcobra

from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.cli.execution_pipeline import prevalidar_y_parsear_codigo

from .dependency_resolver import DependencyResolutionResult, resolve_project_dependencies
from .manifest import create_manifest
from .project import BuildOptions, BuildResult, CobraInstallerError, CobraProject, discover_project
from .spec_writer import SpecBuildContext, write_spec
from .validator import discover_entrypoint, validate_build_options

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
    python_dir: Path | None = None
    generated_code: Path | None = None
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
    python_dir = target / "python"
    packages_dir = target / "packages"
    assets_dir = target / "assets"
    config_dir = target / "config"
    documentation_dir = target / "docs"
    auxiliary_dir = target / "resources"
    for directory in (
        pcobra_runtime,
        python_dir,
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
    copied_project_packages = _copy_many(normalized_project.co_packages, packages_dir, root)
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
    source_entrypoint = normalized_project.entrypoint or normalized_options.entrypoint
    generated_code = _write_transpiled_python_entrypoint(source_entrypoint, root, python_dir)
    entrypoint = target / "pyinstaller_entrypoint.py"
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
        python_dir=python_dir,
        generated_code=generated_code,
        copied_resources={
            "runtime": runtime_copies,
            "packages": (*copied_hub_packages, *copied_explicit_packages, *copied_project_packages),
            "assets": copied_assets,
            "config": copied_config,
            "documentation": copied_docs,
            "auxiliary": copied_auxiliary,
            "entrypoint": (entrypoint,),
            "python": (python_dir / "__main__.py",) if generated_code is not None else (),
        },
        dependency_resolution=dependency_resolution,
        logs=(
            f"Runtime Cobra copiado en {pcobra_runtime}.",
            f"Entrypoint Python para PyInstaller creado en {entrypoint}.",
            f"Entrypoint Python transpilado creado en {python_dir / '__main__.py'}.",
        ),
    )


def build_project(options: BuildOptions | None = None, **overrides: object) -> BuildResult:
    """Construye un proyecto Cobra usando una API programática estable.

    La implementación inicial prepara directorios, manifiesto y especificación
    mínima para que PyInstaller/CLI puedan integrarse sin acoplar lógica al IDLE.
    """

    base = options or BuildOptions()
    if overrides:
        base = replace(base, **overrides)
    normalized = validate_build_options(base)
    entrypoint = normalized.entrypoint or discover_entrypoint(Path(normalized.project_root))
    if entrypoint is None:
        raise CobraInstallerError(
            f"No se encontró un punto de entrada Cobra en {normalized.project_root}"
        )

    output_dir = Path(normalized.output_dir or Path(normalized.project_root) / "dist")
    output_dir.mkdir(parents=True, exist_ok=True)
    name = normalized.name or entrypoint.stem
    manifest_path = create_manifest(normalized, entrypoint, output_dir, name)
    project = discover_project(Path(normalized.project_root))
    if project.entrypoint != entrypoint:
        project = CobraProject(
            project_root=project.project_root,
            entrypoint=entrypoint,
            cobra_toml=project.cobra_toml,
            cobra_lock=project.cobra_lock,
            assets=project.assets,
            config=project.config,
            co_packages=project.co_packages,
            documentation=project.documentation,
            config_dirs=project.config_dirs,
            auxiliary_resources=project.auxiliary_resources,
        )
    runtime = prepare_runtime(
        Path(normalized.temp_dir or Path(normalized.project_root) / "build"),
        project,
        None,
        normalized,
    )
    spec_path = write_spec(
        SpecBuildContext(
            options=normalized,
            runtime=runtime,
            output_dir=output_dir,
            executable_name=name,
        )
    )
    return BuildResult(
        success=True,
        artifact_path=spec_path,
        project_root=Path(normalized.project_root),
        output_dir=output_dir,
        target=normalized.target,
        architecture=normalized.architecture,
        mode=normalized.mode,
        executable_name=name,
        temp_dir=Path(normalized.temp_dir) if normalized.temp_dir is not None else None,
        dist_dir=output_dir,
        metadata={"entrypoint": str(entrypoint), "manifest": str(manifest_path), "name": name},
        logs=("Proyecto preparado para empaquetado.",),
    )


def package_current_project(project_root: str | Path | None = None, **kwargs: object) -> BuildResult:
    """Empaqueta el proyecto actual; punto único que debe llamar el IDLE."""

    options = BuildOptions(project_root=project_root or Path.cwd(), **kwargs)
    return build_project(options)


def _write_transpiled_python_entrypoint(
    source_entrypoint: Path | None, project_root: Path, python_dir: Path
) -> Path | None:
    if source_entrypoint is None:
        return None
    source = Path(source_entrypoint).expanduser().resolve()
    if not source.is_file():
        return None

    ast = prevalidar_y_parsear_codigo(source.read_text(encoding="utf-8"))
    generated = PythonAdapter().compile(
        ast,
        {"source_file": source, "project_root": project_root},
    )
    generated_path = python_dir / f"{source.stem}.py"
    generated_path.write_text(generated, encoding="utf-8")
    (python_dir / "__main__.py").write_text(
        _transpiled_entrypoint_code(generated_path.name), encoding="utf-8"
    )
    return generated_path


def _transpiled_entrypoint_code(module_filename: str) -> str:
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


def _pyinstaller_entrypoint_code(source_entrypoint: Path | None, build_dir: Path) -> str:
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
        "    raise SystemExit(cobra_main(['run', str(source_entrypoint)]))\n"
    )


_RUNTIME_COBRA_SUBPACKAGES = (
    # Importados por pcobra.__init__ y por las rutas de resolución/transpilación
    # usadas por `pcobra.cobra.cli.cli run`.
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
