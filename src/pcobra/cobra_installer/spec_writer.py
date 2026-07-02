"""Generación de especificaciones de empaquetado para PyInstaller."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from .project import BuildOptions
from .targets import BuildMode

if TYPE_CHECKING:  # pragma: no cover
    from .runtime_builder import RuntimePreparationResult


@dataclass(frozen=True, slots=True)
class SpecBuildContext:
    """Contexto completo necesario para escribir un ``.spec`` de PyInstaller."""

    options: BuildOptions
    runtime: "RuntimePreparationResult"
    output_dir: Path | str
    executable_name: str
    hidden_imports: Sequence[str] = field(default_factory=tuple)
    additional_datas: Sequence[tuple[Path | str, str]] = field(default_factory=tuple)


def write_spec(build_context: SpecBuildContext) -> Path:
    """Escribe un archivo ``.spec`` de PyInstaller para un runtime Cobra preparado.

    El spec referencia el entrypoint Python generado por ``prepare_runtime`` e
    incluye automáticamente las carpetas de runtime Cobra, corelibs, paquetes
    CobraHub/locales, assets, configuración, documentación y recursos auxiliares.
    No ejecuta PyInstaller; solo produce el archivo de configuración.
    """

    context = build_context
    options = context.options.normalized()
    runtime = context.runtime
    output_dir = Path(context.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    name = _python_literal(context.executable_name)
    spec_path = output_dir / f"{context.executable_name}.spec"
    mode = BuildMode.from_value(options.mode)

    datas = _collect_datas(runtime, context.additional_datas)
    hidden_imports = _collect_hidden_imports(context.hidden_imports)
    icon_line = f"    icon={_python_literal(str(options.icon))},\n" if options.icon else ""

    analysis = _analysis_block(runtime, options, datas, hidden_imports)
    if mode is BuildMode.ONEFILE:
        body = _onefile_body(analysis, name, icon_line)
    else:
        body = _onedir_body(analysis, name, icon_line)

    spec_path.write_text(body, encoding="utf-8")
    return spec_path


def _analysis_block(
    runtime: "RuntimePreparationResult",
    options: BuildOptions,
    datas: tuple[tuple[str, str], ...],
    hidden_imports: tuple[str, ...],
) -> str:
    return (
        "# -*- mode: python ; coding: utf-8 -*-\n"
        "# Spec generado automáticamente por cobra_installer.\n\n"
        f"block_cipher = None\n\n"
        "a = Analysis(\n"
        f"    [{_python_literal(str(runtime.entrypoint))}],\n"
        f"    pathex={[str(runtime.build_dir), str(options.project_root)]!r},\n"
        "    binaries=[],\n"
        f"    datas={datas!r},\n"
        f"    hiddenimports={hidden_imports!r},\n"
        "    hookspath=[],\n"
        "    hooksconfig={},\n"
        "    runtime_hooks=[],\n"
        "    excludes=[],\n"
        "    win_no_prefer_redirects=False,\n"
        "    win_private_assemblies=False,\n"
        "    cipher=block_cipher,\n"
        "    noarchive=False,\n"
        ")\n"
        "pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)\n"
    )


def _onefile_body(analysis: str, name: str, icon_line: str) -> str:
    return analysis + (
        "exe = EXE(\n"
        "    pyz,\n"
        "    a.scripts,\n"
        "    a.binaries,\n"
        "    a.zipfiles,\n"
        "    a.datas,\n"
        "    [],\n"
        f"    name={name},\n"
        "    debug=False,\n"
        "    bootloader_ignore_signals=False,\n"
        "    strip=False,\n"
        "    upx=True,\n"
        "    upx_exclude=[],\n"
        "    runtime_tmpdir=None,\n"
        "    console=True,\n"
        f"{icon_line}"
        ")\n"
    )


def _onedir_body(analysis: str, name: str, icon_line: str) -> str:
    return analysis + (
        "exe = EXE(\n"
        "    pyz,\n"
        "    a.scripts,\n"
        "    [],\n"
        f"    name={name},\n"
        "    debug=False,\n"
        "    bootloader_ignore_signals=False,\n"
        "    strip=False,\n"
        "    upx=True,\n"
        "    console=True,\n"
        "    exclude_binaries=True,\n"
        f"{icon_line}"
        ")\n"
        "coll = COLLECT(\n"
        "    exe,\n"
        "    a.binaries,\n"
        "    a.zipfiles,\n"
        "    a.datas,\n"
        "    strip=False,\n"
        "    upx=True,\n"
        f"    name={name},\n"
        ")\n"
    )


def _collect_datas(
    runtime: "RuntimePreparationResult",
    additional_datas: Sequence[tuple[Path | str, str]],
) -> tuple[tuple[str, str], ...]:
    candidates: list[tuple[Path, str]] = [
        (runtime.runtime_dir, "runtime/pcobra"),
        (runtime.corelibs_dir, "runtime/pcobra/corelibs"),
        (runtime.standard_library_dir, "runtime/pcobra/standard_library"),
        (runtime.cobra_dir, "runtime/pcobra/cobra"),
        (runtime.packages_dir, "packages"),
        (runtime.assets_dir, "assets"),
        (runtime.config_dir, "config"),
        (runtime.documentation_dir, "docs"),
        (runtime.auxiliary_dir, "resources"),
    ]
    candidates.extend((Path(source), destination) for source, destination in additional_datas)

    datas: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for source, destination in candidates:
        if not source.exists():
            continue
        item = (str(source), destination)
        if item in seen:
            continue
        seen.add(item)
        datas.append(item)
    return tuple(datas)


def _collect_hidden_imports(extra_hidden_imports: Sequence[str]) -> tuple[str, ...]:
    defaults = (
        "pcobra",
        "pcobra.core",
        "pcobra.corelibs",
        "pcobra.standard_library",
        "pcobra.cobra.cli.cli",
        "pcobra.cobra.transpilers.transpiler.to_python",
    )
    return tuple(dict.fromkeys((*defaults, *extra_hidden_imports)))


def _python_literal(value: str) -> str:
    return repr(value)
