from __future__ import annotations

import json
from pathlib import Path

import pytest

from pcobra.cobra_installer import BuildMode, BuildOptions, build_project
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


@pytest.mark.parametrize(
    ("mode", "expected_artifact", "spec_assertions"),
    (
        (
            BuildMode.ONEDIR,
            Path("dist/main/main"),
            ("coll = COLLECT(", "exclude_binaries=True", "    a.binaries,"),
        ),
        (
            BuildMode.ONEFILE,
            Path("dist/main"),
            ("    a.binaries,", "    a.zipfiles,", "    a.datas,"),
        ),
    ),
)
def test_installer_build_parametriza_modo_y_genera_manifest_sin_pyinstaller_real(
    tmp_path: Path,
    monkeypatch,
    mode: BuildMode,
    expected_artifact: Path,
    spec_assertions: tuple[str, ...],
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
        artifact = tmp_path / expected_artifact
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("binario mock", encoding="utf-8")
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
        BuildOptions(project_root=tmp_path, include_dependencies=False, mode=mode),
    )

    dist_dir = tmp_path / "dist"
    manifest_path = dist_dir / "cobra_build_manifest.json"
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result.success is True
    assert result.dist_dir == dist_dir
    assert dist_dir.is_dir()
    assert manifest_path.is_file()
    assert transpile_calls == [(entrypoint, tmp_path / "build")]
    spec_path = dist_dir / "main.spec"
    spec_text = spec_path.read_text(encoding="utf-8")

    assert pyinstaller_calls == [spec_path]
    assert result.metadata["manifest"] == str(manifest_path)
    assert result.metadata["spec"] == str(spec_path)
    assert result.pyinstaller_version == "6.mock"
    assert result.mode is mode
    assert result.artifact_path == dist_dir
    assert manifest_payload["project"] == "demo-build"
    assert manifest_payload["backend"] == "python"
    assert manifest_payload["mode"] == mode.value
    assert manifest_payload["build_mode"] == mode.value
    assert manifest_payload["executable_path"] == str(tmp_path / expected_artifact)
    for assertion in spec_assertions:
        assert assertion in spec_text
    if mode is BuildMode.ONEFILE:
        assert "coll = COLLECT(" not in spec_text
