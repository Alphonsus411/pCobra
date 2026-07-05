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
        config_dirs=("config",),
        auxiliary_resources=("assets/logo.png",),
        config={"profile": "release"},
    ).normalized()

    assert project.entrypoint == tmp_path / "src/main.co"
    assert project.cobra_toml == tmp_path / "cobra.toml"
    assert project.cobra_lock == tmp_path / "cobra.lock"
    assert project.assets == (tmp_path / "assets/logo.png",)
    assert project.co_packages == (tmp_path / "paquetes/ui.co",)
    assert project.documentation == (tmp_path / "docs/manual.md",)
    assert project.config_dirs == (tmp_path / "config",)
    assert project.auxiliary_resources == (tmp_path / "assets/logo.png",)
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
            config_dirs=("config",),
            auxiliary_resources=("assets/logo.png",),
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
    assert payload["config_dirs"] == [str(tmp_path / "config")]
    assert payload["auxiliary_resources"] == [str(tmp_path / "assets" / "logo.png")]
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


def test_discover_project_prefiere_main_cobra_y_recolecta_recursos(tmp_path: Path) -> None:
    from pcobra.cobra_installer import discover_project

    (tmp_path / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text('[project]\nentrypoint = "otro.cobra"\n', encoding="utf-8")
    (tmp_path / "cobra.lock").write_text("# lock\n", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "logo.png").write_bytes(b"png")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "app.yaml").write_text("debug: false\n", encoding="utf-8")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "ui.co").write_text("paquete ui\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    project = discover_project(tmp_path)

    assert project.project_root == tmp_path.resolve()
    assert project.entrypoint == tmp_path / "main.cobra"
    assert project.cobra_toml == tmp_path / "cobra.toml"
    assert project.cobra_lock == tmp_path / "cobra.lock"
    assert project.assets == (tmp_path / "assets",)
    assert project.config_dirs == (tmp_path / "config",)
    assert project.co_packages == (tmp_path / "pkg" / "ui.co",)
    assert project.documentation == (tmp_path / "README.md",)
    assert tmp_path / "assets" / "logo.png" in project.auxiliary_resources
    assert tmp_path / "config" / "app.yaml" in project.auxiliary_resources


def test_find_entrypoint_usa_cobra_toml_si_no_hay_main(tmp_path: Path) -> None:
    from pcobra.cobra_installer import find_entrypoint

    src = tmp_path / "src"
    src.mkdir()
    entrypoint = src / "app.cobra"
    entrypoint.write_text("imprimir('app')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text('[build]\nentrypoint = "src/app.cobra"\n', encoding="utf-8")

    assert find_entrypoint(tmp_path) == entrypoint


def test_find_entrypoint_error_claro_si_hay_ambiguedad(tmp_path: Path) -> None:
    import pytest

    from pcobra.cobra_installer import CobraInstallerError, find_entrypoint

    (tmp_path / "uno.cobra").write_text("", encoding="utf-8")
    (tmp_path / "dos.cobra").write_text("", encoding="utf-8")

    with pytest.raises(CobraInstallerError, match="varios archivos .cobra"):
        find_entrypoint(tmp_path)


def test_collect_project_resources_ignora_build_y_dist(tmp_path: Path) -> None:
    from pcobra.cobra_installer import collect_project_resources

    (tmp_path / "assets").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "omitido.co").write_text("", encoding="utf-8")
    (tmp_path / "mod.co").write_text("", encoding="utf-8")
    (tmp_path / "manual.rst").write_text("Manual\n", encoding="utf-8")

    resources = collect_project_resources(tmp_path)

    assert resources.assets == (tmp_path / "assets",)
    assert resources.co_packages == (tmp_path / "mod.co",)
    assert resources.documentation == (tmp_path / "manual.rst",)


def test_validate_project_acumula_errores_para_idle(tmp_path: Path) -> None:
    from pcobra.cobra_installer import CobraProject, validate_project

    source = tmp_path / "main.co"
    source.write_text("imprimir('hola')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text("[sin_cierre\n", encoding="utf-8")
    outside_doc = tmp_path.parent / "manual.md"

    result = validate_project(
        CobraProject(
            project_root=tmp_path,
            entrypoint=source,
            documentation=(outside_doc,),
            config={"build": {"executable_name": "bad/name", "icon": "assets/missing.bmp"}},
        )
    )

    codes = {error.code for error in result.errors}
    assert not result.is_valid
    assert "entrypoint_extension_invalid" not in codes
    assert "cobra_toml_syntax_invalid" in codes
    assert "documentation_outside_project" in codes
    assert "documentation_not_found" in codes
    assert "executable_name_invalid" in codes
    assert "icon_not_found" in codes
    assert "icon_extension_invalid" in codes


def test_validate_project_acepta_entrypoint_co_fuente_texto(tmp_path: Path) -> None:
    from pcobra.cobra_installer import CobraProject, validate_project

    entrypoint = tmp_path / "main.co"
    entrypoint.write_text("imprimir('hola')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")

    result = validate_project(CobraProject(project_root=tmp_path, entrypoint=entrypoint))

    assert result.is_valid
    assert result.errors == ()


def test_validate_build_options_acepta_entrypoint_co_fuente_texto_descubierto(tmp_path: Path) -> None:
    from pcobra.cobra_installer import BuildOptions
    from pcobra.cobra_installer.validator import validate_build_options

    entrypoint = tmp_path / "main.co"
    entrypoint.write_text("imprimir('hola')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")

    options = validate_build_options(BuildOptions(project_root=tmp_path))

    assert options.project_root == tmp_path


def test_validate_project_acepta_proyecto_cobra_minimo(tmp_path: Path) -> None:
    from pcobra.cobra_installer import CobraProject, validate_project

    entrypoint = tmp_path / "main.cobra"
    entrypoint.write_text("imprimir('hola')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
    (tmp_path / "cobra.lock").write_text('version = "1"\n', encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    icon = assets / "logo.png"
    icon.write_bytes(b"png")

    result = validate_project(
        CobraProject(
            project_root=tmp_path,
            entrypoint=entrypoint,
            assets=(assets,),
            config={"project": {"executable_name": "demo-app", "icon": "assets/logo.png"}},
        )
    )

    assert result.is_valid
    assert result.errors == ()
