from __future__ import annotations

import os
import py_compile
import subprocess
import sys
from pathlib import Path

from pcobra.cobra_installer import (
    BuildOptions,
    CobraProject,
    TranspileResult,
    transpile_project,
)


def test_transpile_project_prepara_build_python_y_recursos(tmp_path: Path) -> None:
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
    (project_root / "data.json").write_text("{}", encoding="utf-8")
    (project_root / "vendor.co").write_bytes(b"paquete-local")

    project = CobraProject(
        project_root=project_root,
        entrypoint=entrypoint,
        cobra_toml=project_root / "cobra.toml",
        cobra_lock=project_root / "cobra.lock",
        assets=(project_root / "assets",),
        config_dirs=(project_root / "config",),
        documentation=(project_root / "README.md",),
        auxiliary_resources=(project_root / "data.json",),
        co_packages=(project_root / "vendor.co",),
    )

    result = transpile_project(
        project,
        tmp_path / "build-temp",
        BuildOptions(project_root=project_root, entrypoint=entrypoint),
    )

    assert isinstance(result, TranspileResult)
    assert result.generated_code.is_file()
    assert "hola" in result.generated_code.read_text(encoding="utf-8")
    py_compile.compile(str(result.generated_code), doraise=True)
    py_compile.compile(str(result.entrypoint), doraise=True)
    assert (result.runtime_dir / "__init__.py").is_file()
    assert (result.runtime_dir / "cobra" / "core" / "nativos").is_dir()
    assert result.corelibs_dir.is_dir()
    assert (result.runtime_dir / "_stubs").is_dir()
    assert (result.runtime_dir / "standard_library").is_dir()
    assert (result.assets_dir / "assets" / "logo.txt").read_text(encoding="utf-8") == "asset"
    assert (result.config_dir / "config" / "settings.json").is_file()
    assert (result.documentation_dir / "README.md").is_file()
    assert (result.auxiliary_dir / "cobra.toml").is_file()
    assert (result.auxiliary_dir / "cobra.lock").is_file()
    assert (result.auxiliary_dir / "data.json").is_file()
    assert (result.packages_dir / "vendor.co").is_file()
    assert result.dependency_resolution is not None


def test_transpile_project_permite_omitir_resolucion_cobrahub(tmp_path: Path) -> None:
    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text("imprimir('sin deps')\n", encoding="utf-8")
    (project_root / "cobra.toml").write_text("[dependencies]\nremoto = '1.0.0'\n", encoding="utf-8")

    result = transpile_project(
        CobraProject(project_root=project_root, entrypoint=entrypoint),
        tmp_path / "build-no-deps",
        BuildOptions(
            project_root=project_root,
            entrypoint=entrypoint,
            include_dependencies=False,
        ),
    )

    assert result.generated_code.is_file()
    assert result.dependency_resolution is None


def test_transpile_project_runtime_autonomo_ejecuta_codigo_generado(tmp_path: Path) -> None:
    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text("imprimir('runtime ok')\n", encoding="utf-8")

    result = transpile_project(
        CobraProject(project_root=project_root, entrypoint=entrypoint),
        tmp_path / "build-runtime",
        BuildOptions(
            project_root=project_root,
            entrypoint=entrypoint,
            include_dependencies=False,
        ),
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(result.runtime_dir.parent)
    completed = subprocess.run(
        [sys.executable, str(result.entrypoint)],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.strip() == "runtime ok"
