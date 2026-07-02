from __future__ import annotations

import json
import py_compile
from pathlib import Path

import pytest

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
    assert result.artifact_path == project_root / "dist" / "main" / "main"
    assert result.dist_dir == project_root / "dist"
    assert result.pyinstaller_version == "6.test"
    assert (project_root / "cobra.lock").is_file()
    assert calls and calls[0].name == "main.spec"
    assert any("1/12 Descubriendo" in item for item in progress)
    assert "pyinstaller simulado" in progress
    assert (project_root / "dist" / "cobra_build_manifest.json").is_file()


def test_build_cancela_antes_de_transpilar_y_pyinstaller_si_dependencia_no_existe(
    tmp_path: Path, monkeypatch
) -> None:
    import pcobra.cobra_installer.runtime_builder as runtime_builder
    from pcobra.cobra_installer import build_project
    from pcobra.cobra_installer.dependency_resolver import CobraDependencyError
    from pcobra.cobra_installer.project import CobraInstallerError

    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text(
        "usar dep-fantasma.modulo\nimprimir('no transpilar')\n", encoding="utf-8"
    )
    (project_root / "cobra.toml").write_text(
        '[project]\nname = "demo"\n\n[dependencies]\ndep-fantasma = "9.9.9"\n',
        encoding="utf-8",
    )

    calls = {"resolve": 0, "transpile": 0, "pyinstaller": 0}

    def fake_resolve_project_dependencies(root):
        calls["resolve"] += 1
        assert Path(root) == project_root
        raise CobraDependencyError(
            "No se pudo descargar dep-fantasma==9.9.9 desde CobraHub: no existe"
        )

    def fail_transpile_project(*_args, **_kwargs):
        calls["transpile"] += 1
        raise AssertionError("no debe transpilar si falla CobraHub")

    def fail_run_pyinstaller(*_args, **_kwargs):
        calls["pyinstaller"] += 1
        raise AssertionError("no debe ejecutar PyInstaller si falla CobraHub")

    monkeypatch.setattr(
        runtime_builder,
        "resolve_project_dependencies",
        fake_resolve_project_dependencies,
    )
    monkeypatch.setattr(runtime_builder, "transpile_project", fail_transpile_project)
    monkeypatch.setattr(runtime_builder, "run_pyinstaller", fail_run_pyinstaller)

    with pytest.raises(CobraInstallerError) as exc_info:
        build_project(
            project_root,
            BuildOptions(project_root=project_root, entrypoint=entrypoint),
        )

    message = str(exc_info.value)
    assert "dep-fantasma" in message
    assert "9.9.9" in message
    assert calls == {"resolve": 1, "transpile": 0, "pyinstaller": 0}


def test_build_cancela_antes_de_transpilar_y_pyinstaller_si_hash_de_lock_no_coincide(
    tmp_path: Path, monkeypatch
) -> None:
    import pcobra.cobra_installer.runtime_builder as runtime_builder
    from pcobra.cobra_installer import build_project
    from pcobra.cobra_installer.dependency_resolver import CobraDependencyError
    from pcobra.cobra_installer.project import CobraInstallerError

    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text(
        "usar dep-integridad.modulo\nimprimir('no transpilar')\n",
        encoding="utf-8",
    )
    (project_root / "cobra.toml").write_text(
        '[project]\nname = "demo"\n\n[dependencies]\ndep-integridad = "1.2.3"\n',
        encoding="utf-8",
    )
    expected_hash = "a" * 64
    resolved_hash = "b" * 64
    (project_root / "cobra.lock").write_text(
        json.dumps(
            {
                "version": 1,
                "packages": [
                    {
                        "name": "dep-integridad",
                        "version": "1.2.3",
                        "sha256": expected_hash,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    calls = {"resolve": 0, "transpile": 0, "pyinstaller": 0}

    def fake_resolve_project_dependencies(root):
        calls["resolve"] += 1
        assert Path(root) == project_root
        lock = json.loads((project_root / "cobra.lock").read_text(encoding="utf-8"))
        assert lock["packages"][0]["sha256"] == expected_hash
        raise CobraDependencyError(
            "Hash inválido para dep-integridad==1.2.3: "
            f"se esperaba {expected_hash}, se obtuvo {resolved_hash}."
        )

    def fail_transpile_project(*_args, **_kwargs):
        calls["transpile"] += 1
        raise AssertionError("no debe transpilar si falla la integridad del lock")

    def fail_run_pyinstaller(*_args, **_kwargs):
        calls["pyinstaller"] += 1
        raise AssertionError(
            "no debe ejecutar PyInstaller si falla la integridad del lock"
        )

    monkeypatch.setattr(
        runtime_builder,
        "resolve_project_dependencies",
        fake_resolve_project_dependencies,
    )
    monkeypatch.setattr(runtime_builder, "transpile_project", fail_transpile_project)
    monkeypatch.setattr(runtime_builder, "run_pyinstaller", fail_run_pyinstaller)

    with pytest.raises(CobraInstallerError) as exc_info:
        build_project(
            project_root,
            BuildOptions(project_root=project_root, entrypoint=entrypoint),
        )

    message = str(exc_info.value)
    assert "dep-integridad" in message
    assert expected_hash in message
    assert resolved_hash in message
    assert calls == {"resolve": 1, "transpile": 0, "pyinstaller": 0}


def test_build_cancela_antes_de_transpilar_si_conflicto_transitivo_incompatible(
    tmp_path: Path, monkeypatch
) -> None:
    import pcobra.cobra_installer.runtime_builder as runtime_builder
    from pcobra.cobra_installer import build_project
    from pcobra.cobra_installer.dependency_resolver import CobraDependencyError
    from pcobra.cobra_installer.project import CobraInstallerError

    project_root = tmp_path / "app"
    project_root.mkdir()
    entrypoint = project_root / "main.cobra"
    entrypoint.write_text("usar dep-a.api\nusar dep-b.api\n", encoding="utf-8")
    (project_root / "cobra.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[dependencies]\ndep-a = "1.0.0"\ndep-b = "1.0.0"\n',
        encoding="utf-8",
    )
    calls = {"resolve": 0, "transpile": 0, "pyinstaller": 0}

    def fake_resolve_project_dependencies(root):
        calls["resolve"] += 1
        assert Path(root) == project_root
        raise CobraDependencyError(
            "Conflicto de versiones para compartida: se requieren versiones "
            "incompatibles 1.0.0 y 2.0.0. Cadena existente: proyecto -> "
            "dep-a==1.0.0 -> compartida==1.0.0. Cadena nueva: proyecto -> "
            "dep-b==1.0.0 -> compartida==2.0.0."
        )

    def fail_transpile_project(*_args, **_kwargs):
        calls["transpile"] += 1
        raise AssertionError("no debe transpilar si hay conflicto de dependencias")

    def fail_run_pyinstaller(*_args, **_kwargs):
        calls["pyinstaller"] += 1
        raise AssertionError("no debe ejecutar PyInstaller si hay conflicto")

    monkeypatch.setattr(
        runtime_builder,
        "resolve_project_dependencies",
        fake_resolve_project_dependencies,
    )
    monkeypatch.setattr(runtime_builder, "transpile_project", fail_transpile_project)
    monkeypatch.setattr(runtime_builder, "run_pyinstaller", fail_run_pyinstaller)

    with pytest.raises(CobraInstallerError) as exc_info:
        build_project(
            project_root,
            BuildOptions(project_root=project_root, entrypoint=entrypoint),
        )

    message = str(exc_info.value)
    assert "Conflicto de versiones para compartida" in message
    assert "Cadena existente" in message
    assert "Cadena nueva" in message
    assert calls == {"resolve": 1, "transpile": 0, "pyinstaller": 0}
