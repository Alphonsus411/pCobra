from __future__ import annotations

import json
from pathlib import Path

import pcobra.cobra_installer.manifest as manifest_module

from pcobra.cobra_installer import (
    BuildManifest,
    BuildMode,
    BuildOptions,
    CobraProject,
    DependencyInfo,
    TargetOS,
)
from pcobra.cobra_installer.manifest import (
    BUILD_MANIFEST_NAME,
    create_manifest,
    write_manifest_json,
)


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
        dependencies=(
            DependencyInfo(
                name="pyinstaller", version="6.0.0", hashes={"wheel": "sha256:def"}
            ),
        ),
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


def test_build_manifest_serializa_todos_los_campos_auditables_de_forma_determinista(
    tmp_path: Path,
) -> None:
    """Valida el contrato auditable completo sin depender del reloj ni del FS."""

    project = CobraProject(
        project_root=tmp_path,
        entrypoint="src/app.cobra",
        cobra_toml="cobra.toml",
        cobra_lock="cobra.lock",
        assets=("assets/z.png", "assets/a.png"),
        config={"project": {"name": "cobra-demo", "version": "2.4.6"}},
    )
    manifest = BuildManifest(
        project=project,
        executable_name="cobra-demo-bin",
        backend="python",
        target=TargetOS.LINUX,
        architecture="x86_64",
        mode=BuildMode.ONEFILE,
        hashes={"z.bin": "sha256:zzz", "a.bin": "sha256:aaa"},
        cobra_version="9.8.7",
        pyinstaller_version="6.14.1",
        dependencies=(
            DependencyInfo(
                name="pyinstaller",
                version="6.14.1",
                source="pypi",
                path=tmp_path / "wheels" / "pyinstaller.whl",
                hashes={"wheel": "sha256:pyinstaller"},
            ),
        ),
        cobrahub_dependencies=(
            DependencyInfo(
                name="ui-kit",
                version="1.0.0",
                source="cobrahub",
                path=tmp_path / "packages" / "ui-kit.co",
                hashes={"sha256": "hub-hash"},
            ),
        ),
        generated_at="2026-07-03T10:15:30Z",
        build_duration_seconds=12.5,
        runtime_included=True,
        included_assets=("assets/runtime.dat", "assets/a.png"),
        final_size_bytes=4096,
        executable_path=tmp_path / "dist" / "cobra-demo-bin",
    )

    payload = manifest.to_dict()

    assert payload["project"] == "cobra-demo"
    assert payload["version"] == "2.4.6"
    assert payload["backend"] == "python"
    assert payload["target"] == "linux"
    assert payload["architecture"] == "x86_64"
    assert payload["build_mode"] == "onefile"
    assert payload["mode"] == "onefile"
    assert payload["cobra_version"] == "9.8.7"
    assert payload["pyinstaller_version"] == "6.14.1"
    assert payload["dependencies"] == [
        {
            "name": "pyinstaller",
            "version": "6.14.1",
            "source": "pypi",
            "path": str(tmp_path / "wheels" / "pyinstaller.whl"),
            "hashes": {"wheel": "sha256:pyinstaller"},
        }
    ]
    assert payload["cobrahub_dependencies"] == [
        {
            "name": "ui-kit",
            "version": "1.0.0",
            "source": "cobrahub",
            "path": str(tmp_path / "packages" / "ui-kit.co"),
            "hashes": {"sha256": "hub-hash"},
        }
    ]
    assert payload["hashes"] == {"a.bin": "sha256:aaa", "z.bin": "sha256:zzz"}
    assert payload["generated_at"] == "2026-07-03T10:15:30Z"
    assert payload["build_duration_seconds"] == 12.5
    assert payload["runtime_included"] is True
    assert payload["assets_included"] == ["assets/a.png", "assets/runtime.dat"]
    assert payload["final_size_bytes"] == 4096
    assert payload["executable_path"] == str(tmp_path / "dist" / "cobra-demo-bin")


def test_create_manifest_mantiene_compatibilidad_y_agrega_campos(
    tmp_path: Path,
) -> None:
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


def test_create_manifest_genera_cobra_build_manifest_estable(tmp_path: Path) -> None:
    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    entrypoint = tmp_path / "main.cobra"
    entrypoint.write_text("imprimir('hola')\n", encoding="utf-8")
    asset = tmp_path / "assets" / "logo.txt"
    asset.parent.mkdir()
    asset.write_text("logo", encoding="utf-8")
    options = BuildOptions(
        project_root=tmp_path,
        target=TargetOS.LINUX,
        architecture="x86_64",
        mode=BuildMode.ONEFILE,
        assets=(asset,),
        config={
            "project": {"name": "demo", "version": "1.2.3"},
            "build": {"backend": "python"},
        },
        include_dependencies=True,
    ).normalized()

    manifest_path = create_manifest(options, entrypoint, output_dir, "demo-bin")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest_path == output_dir / BUILD_MANIFEST_NAME
    assert (output_dir / "cobra-installer-manifest.json").is_file()
    assert payload["project"] == "demo"
    assert payload["version"] == "1.2.3"
    assert payload["backend"] == "python"
    assert payload["target"] == "linux"
    assert payload["architecture"] == "x86_64"
    assert payload["build_mode"] == "onefile"
    assert payload["cobra_version"] is None or isinstance(payload["cobra_version"], str)
    assert "pyinstaller_version" in payload
    assert payload["cobrahub_dependencies"] == []
    assert str(entrypoint) in payload["hashes"]
    assert payload["generated_at"].endswith("Z")
    assert payload["build_duration_seconds"] == 0.0
    assert payload["runtime_included"] is False
    assert payload["assets_included"] == [str(asset)]
    assert payload["final_size_bytes"] is None
    assert payload["executable_path"] == str(output_dir / "demo-bin")


def test_create_manifest_calcula_hashes_runtime_y_tamano_final_deterministas(
    tmp_path: Path, monkeypatch
) -> None:
    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    build_dir = tmp_path / "build"
    (build_dir / "runtime").mkdir(parents=True)
    entrypoint = tmp_path / "main.cobra"
    entrypoint.write_text("imprimir('determinista')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text(
        "[project]\nname = 'demo-create'\nversion = '1.0.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "cobra.lock").write_text("lock-v1\n", encoding="utf-8")
    asset = tmp_path / "assets" / "logo.txt"
    asset.parent.mkdir()
    asset.write_text("asset-v1", encoding="utf-8")
    executable_path = output_dir / "demo-create" / "demo-create"
    executable_path.parent.mkdir()
    executable_path.write_bytes(b"123456789")
    mocked_versions = {"pcobra": "3.2.1", "pyinstaller": "6.1.0"}
    monkeypatch.setattr(
        manifest_module,
        "_installed_version",
        lambda name: mocked_versions[name],
    )

    manifest_path = create_manifest(
        BuildOptions(
            project_root=tmp_path,
            target=TargetOS.LINUX,
            architecture="arm64",
            mode=BuildMode.ONEDIR,
            temp_dir=build_dir,
            assets=(asset,),
            config={"project": {"name": "demo-create", "version": "1.0.0"}},
        ).normalized(),
        entrypoint,
        output_dir,
        "demo-create",
    )

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["project"] == "demo-create"
    assert payload["version"] == "1.0.0"
    assert payload["target"] == "linux"
    assert payload["architecture"] == "arm64"
    assert payload["build_mode"] == "onedir"
    assert payload["cobra_version"] == "3.2.1"
    assert payload["pyinstaller_version"] == "6.1.0"
    assert payload["runtime_included"] is True
    assert payload["assets_included"] == [str(asset)]
    assert payload["final_size_bytes"] == 9
    assert set(payload["hashes"]) == {
        str(entrypoint),
        str(tmp_path / "cobra.toml"),
        str(tmp_path / "cobra.lock"),
        str(asset),
        str(executable_path),
    }
    assert all(value.startswith("sha256:") for value in payload["hashes"].values())


def test_write_manifest_json_ordena_claves_para_comparaciones_estables(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.json"

    write_manifest_json(manifest_path, {"z": 1, "a": {"b": 2, "a": 1}})

    assert manifest_path.read_text(encoding="utf-8").splitlines()[:4] == [
        "{",
        '  "a": {',
        '    "a": 1,',
        '    "b": 2',
    ]


def test_discover_project_prefiere_main_cobra_y_recolecta_recursos(
    tmp_path: Path,
) -> None:
    from pcobra.cobra_installer import discover_project

    (tmp_path / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    (tmp_path / "cobra.toml").write_text(
        '[project]\nentrypoint = "otro.cobra"\n', encoding="utf-8"
    )
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
    (tmp_path / "cobra.toml").write_text(
        '[build]\nentrypoint = "src/app.cobra"\n', encoding="utf-8"
    )

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
            config={
                "build": {"executable_name": "bad/name", "icon": "assets/missing.bmp"}
            },
        )
    )

    codes = {error.code for error in result.errors}
    assert not result.is_valid
    assert "entrypoint_extension_invalid" in codes
    assert "cobra_toml_syntax_invalid" in codes
    assert "documentation_outside_project" in codes
    assert "documentation_not_found" in codes
    assert "executable_name_invalid" in codes
    assert "icon_not_found" in codes
    assert "icon_extension_invalid" in codes


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
            config={
                "project": {"executable_name": "demo-app", "icon": "assets/logo.png"}
            },
        )
    )

    assert result.is_valid
    assert result.errors == ()
