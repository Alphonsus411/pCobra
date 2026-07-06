from __future__ import annotations

import py_compile
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
    assert result.corelibs_dir.is_dir()
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


def test_build_project_orquesta_flujo_completo_con_callback(
    tmp_path: Path, monkeypatch
) -> None:
    from pcobra.cobra_installer import build_project
    from pcobra.cobra_installer.pyinstaller_runner import PyInstallerRunResult
    import pcobra.cobra_installer.runtime_builder as runtime_builder

    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text("imprimir('hola build')\n", encoding="utf-8")
    (project_root / "cobra.toml").write_text(
        '[project]\nname = "demo"\n', encoding="utf-8"
    )

    calls: list[Path] = []

    def fake_run_pyinstaller(spec_path, options, logger):
        calls.append(Path(spec_path))
        logger.info("pyinstaller simulado")
        return PyInstallerRunResult(
            success=True,
            version="6.test",
            returncode=0,
            command=("python", "-m", "PyInstaller", str(spec_path)),
        )

    monkeypatch.setattr(runtime_builder, "run_pyinstaller", fake_run_pyinstaller)
    progress: list[str] = []

    result = build_project(
        project_root,
        BuildOptions(project_root=project_root, log_callback=progress.append),
    )

    assert result.success is True
    assert result.artifact_path == project_root / "dist"
    assert result.dist_dir == project_root / "dist"
    assert result.pyinstaller_version == "6.test"
    assert (project_root / "cobra.lock").is_file()
    assert calls and calls[0].name == "main.spec"
    spec_content = calls[0].read_text(encoding="utf-8")
    assert str(project_root / "build" / "python" / "main.py") in spec_content
    assert "'.'" in spec_content
    assert any("1/12 Descubriendo" in item for item in progress)
    assert "pyinstaller simulado" in progress
    assert (project_root / "dist" / "cobra_build_manifest.json").is_file()
