from __future__ import annotations

import json
from pathlib import Path

from pcobra.cobra_installer import (
    BuildManifest,
    BuildMode,
    BuildOptions,
    CobraProject,
    DependencyInfo,
    TargetOS,
)
from pcobra.cobra_installer.manifest import create_manifest


def test_cobra_project_normaliza_recursos_desde_raiz(tmp_path: Path) -> None:
    project = CobraProject(
        project_root=tmp_path,
        entrypoint="src/main.co",
        assets=("assets/logo.png",),
        co_packages=("paquetes/ui.co",),
        documentation=("docs/manual.md",),
        config={"profile": "release"},
    ).normalized()

    assert project.entrypoint == tmp_path / "src/main.co"
    assert project.cobra_toml == tmp_path / "cobra.toml"
    assert project.cobra_lock == tmp_path / "cobra.lock"
    assert project.assets == (tmp_path / "assets/logo.png",)
    assert project.co_packages == (tmp_path / "paquetes/ui.co",)
    assert project.documentation == (tmp_path / "docs/manual.md",)
    assert project.config == {"profile": "release"}


def test_build_options_normaliza_modo_dist_temp_icono_y_assets(tmp_path: Path) -> None:
    options = BuildOptions(
        project_root=tmp_path,
        entrypoint="main.co",
        dist_dir="salida",
        temp_dir="tmp-build",
        icon="assets/app.ico",
        assets=("assets/app.ico",),
        target=TargetOS.LINUX,
        architecture="x86_64",
        mode="onefile",
    ).normalized()

    assert options.entrypoint == tmp_path / "main.co"
    assert options.output_dir == tmp_path / "salida"
    assert options.dist_dir == tmp_path / "salida"
    assert options.temp_dir == tmp_path / "tmp-build"
    assert options.icon == tmp_path / "assets/app.ico"
    assert options.assets == (tmp_path / "assets/app.ico",)
    assert options.target == TargetOS.LINUX
    assert options.architecture == "x86_64"
    assert options.mode == BuildMode.ONEFILE


def test_build_manifest_serializa_campos_del_build(tmp_path: Path) -> None:
    manifest = BuildManifest(
        project=CobraProject(
            project_root=tmp_path,
            entrypoint="main.co",
            cobra_toml="cobra.toml",
            cobra_lock="cobra.lock",
            assets=("assets/logo.png",),
            config={"debug": False},
            co_packages=("pkg/app.co",),
            documentation=("README.md",),
        ),
        executable_name="cobra-app",
        icon="assets/logo.png",
        target=TargetOS.MACOS,
        architecture="arm64",
        mode=BuildMode.ONEDIR,
        temp_dir="build/tmp",
        dist_dir="dist/macos",
        hashes={"main.co": "sha256:abc"},
        cobra_version="1.2.3",
        pyinstaller_version="6.0.0",
        dependencies=(DependencyInfo(name="pyinstaller", version="6.0.0", hashes={"wheel": "sha256:def"}),),
    )

    payload = manifest.to_dict()

    assert payload["project_root"] == str(tmp_path)
    assert payload["entrypoint"] == str(tmp_path / "main.co")
    assert payload["cobra_toml"] == str(tmp_path / "cobra.toml")
    assert payload["cobra_lock"] == str(tmp_path / "cobra.lock")
    assert payload["assets"] == [str(tmp_path / "assets/logo.png")]
    assert payload["config"] == {"debug": False}
    assert payload["co_packages"] == [str(tmp_path / "pkg/app.co")]
    assert payload["documentation"] == [str(tmp_path / "README.md")]
    assert payload["executable_name"] == "cobra-app"
    assert payload["icon"] == "assets/logo.png"
    assert payload["target"] == "macos"
    assert payload["architecture"] == "arm64"
    assert payload["mode"] == "onedir"
    assert payload["temp_dir"] == "build/tmp"
    assert payload["dist_dir"] == "dist/macos"
    assert payload["hashes"] == {"main.co": "sha256:abc"}
    assert payload["cobra_version"] == "1.2.3"
    assert payload["pyinstaller_version"] == "6.0.0"
    assert payload["dependencies"] == [
        {
            "name": "pyinstaller",
            "version": "6.0.0",
            "source": None,
            "path": None,
            "hashes": {"wheel": "sha256:def"},
        }
    ]


def test_create_manifest_mantiene_compatibilidad_y_agrega_campos(tmp_path: Path) -> None:
    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    options = BuildOptions(
        project_root=tmp_path,
        target=TargetOS.WINDOWS,
        architecture="x86_64",
        mode=BuildMode.ONEFILE,
        temp_dir=tmp_path / "build",
        icon="app.ico",
        assets=("assets",),
        config={"env": "prod"},
        include_dependencies=False,
    ).normalized()

    manifest_path = create_manifest(options, tmp_path / "main.co", output_dir, "demo")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["name"] == "demo"
    assert payload["executable_name"] == "demo"
    assert payload["target"] == "windows"
    assert payload["architecture"] == "x86_64"
    assert payload["mode"] == "onefile"
    assert payload["dist_dir"] == str(output_dir)
    assert payload["include_dependencies"] is False
