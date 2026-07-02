from __future__ import annotations

from pathlib import Path

from pcobra.cobra_installer import BuildMode, BuildOptions
from pcobra.cobra_installer.runtime_builder import RuntimePreparationResult
from pcobra.cobra_installer.spec_writer import SpecBuildContext, write_spec


def _runtime_tree(tmp_path: Path) -> RuntimePreparationResult:
    build_dir = tmp_path / "build"
    runtime_dir = build_dir / "runtime" / "pcobra"
    corelibs_dir = runtime_dir / "corelibs"
    standard_library_dir = runtime_dir / "standard_library"
    cobra_dir = runtime_dir / "cobra"
    packages_dir = build_dir / "packages"
    assets_dir = build_dir / "assets"
    config_dir = build_dir / "config"
    documentation_dir = build_dir / "docs"
    auxiliary_dir = build_dir / "resources"
    entrypoint = build_dir / "pyinstaller_entrypoint.py"
    for path in (
        corelibs_dir,
        standard_library_dir,
        cobra_dir,
        packages_dir,
        assets_dir,
        config_dir,
        documentation_dir,
        auxiliary_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text("print('entrypoint')\n", encoding="utf-8")
    return RuntimePreparationResult(
        build_dir=build_dir,
        runtime_dir=runtime_dir,
        corelibs_dir=corelibs_dir,
        standard_library_dir=standard_library_dir,
        cobra_dir=cobra_dir,
        packages_dir=packages_dir,
        assets_dir=assets_dir,
        config_dir=config_dir,
        documentation_dir=documentation_dir,
        auxiliary_dir=auxiliary_dir,
        entrypoint=entrypoint,
    )


def test_write_spec_onedir_incluye_runtime_recursos_imports_y_nombre(tmp_path: Path) -> None:
    runtime = _runtime_tree(tmp_path)
    extra_data = tmp_path / "extra-data"
    extra_data.mkdir()

    spec_path = write_spec(
        SpecBuildContext(
            options=BuildOptions(project_root=tmp_path, mode=BuildMode.ONEDIR),
            runtime=runtime,
            output_dir=tmp_path / "dist",
            executable_name="demo_app",
            hidden_imports=("cobrahub.paquete",),
            additional_datas=((extra_data, "extras"),),
        )
    )

    content = spec_path.read_text(encoding="utf-8")
    assert spec_path == tmp_path / "dist" / "demo_app.spec"
    assert str(runtime.entrypoint) in content
    assert "('" in content and "runtime/pcobra" in content
    assert "runtime/pcobra/corelibs" in content
    assert "packages" in content
    assert "assets" in content
    assert "config" in content
    assert "docs" in content
    assert "resources" in content
    assert "extras" in content
    assert "pcobra.cobra.cli.cli" in content
    assert "cobrahub.paquete" in content
    assert "exclude_binaries=True" in content
    assert "coll = COLLECT" in content
    assert "name='demo_app'" in content


def test_write_spec_onefile_incluye_icono_y_sin_collect(tmp_path: Path) -> None:
    runtime = _runtime_tree(tmp_path)
    icon = tmp_path / "icon.ico"
    icon.write_bytes(b"ico")

    spec_path = write_spec(
        SpecBuildContext(
            options=BuildOptions(project_root=tmp_path, mode=BuildMode.ONEFILE, icon=icon),
            runtime=runtime,
            output_dir=tmp_path / "dist",
            executable_name="demo_onefile",
        )
    )

    content = spec_path.read_text(encoding="utf-8")
    assert spec_path.name == "demo_onefile.spec"
    assert "a.binaries" in content
    assert "a.datas" in content
    assert "coll = COLLECT" not in content
    assert f"icon='{icon}'" in content
    assert "name='demo_onefile'" in content
