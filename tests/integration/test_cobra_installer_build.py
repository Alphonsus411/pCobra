from __future__ import annotations

import json
from pathlib import Path

from pcobra.cobra_installer import BuildOptions, build_project
from pcobra.cobra_installer.pyinstaller_runner import PyInstallerRunResult


def _create_minimal_cobra_project(root: Path) -> tuple[Path, Path]:
    """Crea un proyecto Cobra mínimo con entrypoint y cobra.toml."""

    entrypoint = root / "main.cobra"
    manifest = root / "cobra.toml"
    entrypoint.write_text("imprimir('build mock')\n", encoding="utf-8")
    manifest.write_text(
        '[project]\nname = "demo-build"\nversion = "1.0.0"\n'
        '[build]\nentrypoint = "main.cobra"\nbackend = "python"\n',
        encoding="utf-8",
    )
    return entrypoint, manifest


def test_installer_build_transpila_y_genera_dist_manifest_sin_pyinstaller_real(
    tmp_path: Path, monkeypatch
) -> None:
    import pcobra.cobra_installer.runtime_builder as runtime_builder

    entrypoint, _manifest = _create_minimal_cobra_project(tmp_path)
    transpile_calls: list[tuple[Path, Path]] = []
    real_transpile_project = runtime_builder.transpile_project

    def spy_transpile_project(project, build_dir, options):
        transpile_calls.append((Path(project.entrypoint), Path(build_dir)))
        return real_transpile_project(project, build_dir, options)

    pyinstaller_calls: list[Path] = []

    def fake_run_pyinstaller(spec_path, options, logger):
        pyinstaller_calls.append(Path(spec_path))
        logger.info("PyInstaller mockeado: no se genera ejecutable real")
        return PyInstallerRunResult(
            success=True,
            version="6.mock",
            returncode=0,
            command=("python", "-m", "PyInstaller", str(spec_path)),
        )

    monkeypatch.setattr(runtime_builder, "transpile_project", spy_transpile_project)
    monkeypatch.setattr(runtime_builder, "run_pyinstaller", fake_run_pyinstaller)

    result = build_project(
        tmp_path,
        BuildOptions(project_root=tmp_path, include_dependencies=False),
    )

    dist_dir = tmp_path / "dist"
    manifest_path = dist_dir / "cobra_build_manifest.json"
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result.success is True
    assert result.dist_dir == dist_dir
    assert dist_dir.is_dir()
    assert manifest_path.is_file()
    assert transpile_calls == [(entrypoint, tmp_path / "build")]
    assert pyinstaller_calls == [dist_dir / "main.spec"]
    assert result.metadata["manifest"] == str(manifest_path)
    assert result.pyinstaller_version == "6.mock"
    assert manifest_payload["project"] == "demo-build"
    assert manifest_payload["backend"] == "python"
    assert manifest_payload["executable_path"] == str(dist_dir / "main" / "main")
