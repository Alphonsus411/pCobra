from __future__ import annotations

import py_compile
from pathlib import Path

from pcobra.cobra_installer import (
    BuildOptions,
    CobraProject,
    RuntimePreparationResult,
    prepare_runtime,
)
from pcobra.cobra_installer.dependency_resolver import DependencyResolutionResult
from pcobra.cobra_installer.hub_resolver import CobraHubResolution


def test_prepare_runtime_copia_runtime_recursos_y_entrypoint_filtrados(tmp_path: Path) -> None:
    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text("imprimir('hola')\n", encoding="utf-8")
    (project_root / "cobra.toml").write_text("name = 'demo'\n", encoding="utf-8")
    (project_root / "cobra.lock").write_text('{"packages": []}\n', encoding="utf-8")
    (project_root / "assets").mkdir()
    (project_root / "assets" / "logo.txt").write_text("asset", encoding="utf-8")
    (project_root / "config").mkdir()
    (project_root / "config" / "settings.json").write_text("{}", encoding="utf-8")
    (project_root / "README.md").write_text("# Demo", encoding="utf-8")
    (project_root / "vendor.co").write_bytes(b"paquete-local")
    resolved_package = tmp_path / "remoto-1.0.0.co"
    resolved_package.write_bytes(b"paquete-remoto")
    resolution = DependencyResolutionResult(
        declared={},
        used_imports=set(),
        resolved={
            "remoto": CobraHubResolution(
                name="remoto",
                version="1.0.0",
                path=resolved_package,
                sha256="0" * 64,
                source="test",
            )
        },
        lockfile_path=project_root / "cobra.lock",
    )

    result = prepare_runtime(
        tmp_path / "build-runtime",
        CobraProject(
            project_root=project_root,
            entrypoint=entrypoint,
            cobra_toml=project_root / "cobra.toml",
            cobra_lock=project_root / "cobra.lock",
            assets=(project_root / "assets",),
            config_dirs=(project_root / "config",),
            documentation=(project_root / "README.md",),
            co_packages=(project_root / "vendor.co",),
        ),
        resolution,
        BuildOptions(project_root=project_root, entrypoint=entrypoint),
    )

    assert isinstance(result, RuntimePreparationResult)
    py_compile.compile(str(result.entrypoint), doraise=True)
    assert (result.runtime_dir / "__init__.py").is_file()
    assert (result.runtime_dir / "core").is_dir()
    assert result.corelibs_dir.is_dir()
    assert result.standard_library_dir.is_dir()
    assert (result.cobra_dir / "core" / "parser.py").is_file()
    assert (result.cobra_dir / "cli" / "cli.py").is_file()
    assert not (result.runtime_dir / "cobra" / "benchmarks").exists()
    assert not any(result.runtime_dir.rglob("__pycache__"))
    assert (result.packages_dir / "remoto-1.0.0.co").read_bytes() == b"paquete-remoto"
    assert (result.packages_dir / "vendor.co").read_bytes() == b"paquete-local"
    assert (result.assets_dir / "assets" / "logo.txt").read_text(encoding="utf-8") == "asset"
    assert (result.config_dir / "config" / "settings.json").is_file()
    assert (result.documentation_dir / "README.md").is_file()
    assert (result.auxiliary_dir / "cobra.toml").is_file()
    assert (result.auxiliary_dir / "cobra.lock").is_file()
    assert "runtime" in result.copied_resources
    assert result.dependency_resolution is resolution


def test_prepare_runtime_acepta_dependencias_como_rutas_y_no_resuelve_si_se_omiten(tmp_path: Path) -> None:
    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text("imprimir('sin deps')\n", encoding="utf-8")
    paquete = tmp_path / "manual.co"
    paquete.write_bytes(b"manual")

    result = prepare_runtime(
        tmp_path / "build-runtime",
        CobraProject(project_root=project_root, entrypoint=entrypoint),
        (paquete,),
        BuildOptions(
            project_root=project_root,
            entrypoint=entrypoint,
            include_dependencies=False,
        ),
    )

    assert (result.packages_dir / "manual.co").read_bytes() == b"manual"
    assert result.dependency_resolution is None
