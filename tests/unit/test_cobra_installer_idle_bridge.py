from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from pcobra.cobra_installer import idle_bridge
from pcobra.cobra_installer.project import BuildOptions, BuildResult, CobraInstallerError


def test_package_current_project_convierte_opciones_idle_e_invoca_builder(monkeypatch, tmp_path: Path) -> None:
    calls = []
    progress = []
    dist_dir = tmp_path / "dist"
    executable = dist_dir / "demo"
    executable.parent.mkdir()
    executable.write_text("bin", encoding="utf-8")

    def fake_build_project(project_path, options):
        calls.append((project_path, options))
        options.log_callback("progreso del builder")
        return BuildResult(
            success=True,
            executable_name="demo",
            output_dir=dist_dir,
            dist_dir=dist_dir,
        )

    monkeypatch.setattr(idle_bridge, "build_project", fake_build_project)

    result = idle_bridge.package_current_project(
        tmp_path,
        {
            "nombre": "demo",
            "directorio_salida": "dist",
            "objetivo": "linux",
            "arquitectura": "x86_64",
            "modo": "onefile",
            "limpiar": True,
            "incluir_dependencias": False,
            "extra_args": "--noconfirm --clean",
        },
        progress.append,
    )

    assert result == idle_bridge.IdlePackageResult(executable, dist_dir)
    assert len(calls) == 1
    assert calls[0][0] == tmp_path
    options = calls[0][1]
    assert isinstance(options, BuildOptions)
    assert options.project_root == tmp_path
    assert options.name == "demo"
    assert options.output_dir == "dist"
    assert options.target == "linux"
    assert options.architecture == "x86_64"
    assert options.mode == "onefile"
    assert options.clean is True
    assert options.include_dependencies is False
    assert options.extra_args == ("--noconfirm", "--clean")
    assert progress == [
        "Iniciando empaquetado del proyecto Cobra...",
        "progreso del builder",
        f"Empaquetado completado en {dist_dir}.",
    ]


def test_package_current_project_acepta_objeto_simple_de_opciones(monkeypatch, tmp_path: Path) -> None:
    captured = []

    def fake_build_project(_project_path, options):
        captured.append(options)
        return BuildResult(success=True, executable_name="app", dist_dir=tmp_path / "dist")

    monkeypatch.setattr(idle_bridge, "build_project", fake_build_project)

    result = idle_bridge.package_current_project(
        tmp_path,
        SimpleNamespace(nombre="app", objetivo="windows", instalar_pyinstaller=True),
    )

    assert result.executable_path == tmp_path / "dist" / "app"
    assert result.dist_dir == tmp_path / "dist"
    assert captured[0].name == "app"
    assert captured[0].target == "windows"
    assert captured[0].install_pyinstaller is True


def test_package_current_project_traduce_error_controlado(monkeypatch, tmp_path: Path) -> None:
    errors = []

    def fake_build_project(_project_path, _options):
        raise CobraInstallerError("no existe main.cobra")

    monkeypatch.setattr(idle_bridge, "build_project", fake_build_project)

    with pytest.raises(RuntimeError, match="No se pudo empaquetar"):
        idle_bridge.package_current_project(
            tmp_path, {}, error_callback=errors.append
        )

    assert errors == [
        "No se pudo empaquetar el proyecto Cobra: no existe main.cobra"
    ]


def test_package_from_idle_es_alias_compatible_con_kwargs(monkeypatch, tmp_path: Path) -> None:
    captured = []

    def fake_package_current_project(project_root, ui_options, progress_callback, error_callback):
        captured.append((project_root, ui_options, progress_callback, error_callback))
        return idle_bridge.IdlePackageResult(tmp_path / "dist" / "demo", tmp_path / "dist")

    monkeypatch.setattr(idle_bridge, "package_current_project", fake_package_current_project)

    result = idle_bridge.package_from_idle(tmp_path, {"nombre": "demo"}, objetivo="linux")

    assert result.dist_dir == tmp_path / "dist"
    assert captured == [
        (tmp_path, {"nombre": "demo", "objetivo": "linux"}, None, None)
    ]


def test_package_current_project_muestra_conflicto_transitivo_comprensible(
    monkeypatch, tmp_path: Path
) -> None:
    errors = []

    def fake_build_project(_project_path, _options):
        raise CobraInstallerError(
            "Conflicto de versiones para compartida: se requieren versiones "
            "incompatibles 1.0.0 y 2.0.0. Cadena existente: proyecto -> "
            "dep-a==1.0.0 -> compartida==1.0.0. Cadena nueva: proyecto -> "
            "dep-b==1.0.0 -> compartida==2.0.0."
        )

    monkeypatch.setattr(idle_bridge, "build_project", fake_build_project)

    with pytest.raises(RuntimeError) as exc_info:
        idle_bridge.package_current_project(
            tmp_path, {}, error_callback=errors.append
        )

    message = str(exc_info.value)
    assert "No se pudo empaquetar el proyecto Cobra" in message
    assert "Conflicto de versiones para compartida" in message
    assert "Cadena existente" in message
    assert errors == [message]
