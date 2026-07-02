from pathlib import Path

import pytest

from pcobra.cobra.cli.commands_v2.installer_cmd import InstallerCommandV2
from pcobra.cobra_installer import BuildMode, Builder, CobraInstallerError, TargetOS
from pcobra.cobra_installer.project import BuildResult


def test_installer_build_invoca_build_project(monkeypatch, tmp_path, capsys):
    import pcobra.cobra_installer as cobra_installer

    captured = {}

    def fake_build_project(project_path, options):
        captured["project_path"] = project_path
        captured["options"] = options
        return BuildResult(success=True, artifact_path=tmp_path / "dist")

    monkeypatch.setattr(cobra_installer, "build_project", fake_build_project)
    command = InstallerCommandV2()
    parser = _registered_parser(command)
    args = parser.parse_args(
        [
            "installer",
            "build",
            str(tmp_path),
            "--target",
            "linux",
            "--mode",
            "onefile",
            "--name",
            "demo",
            "--icon",
            "icon.png",
            "--builder",
            "local",
            "--install-pyinstaller",
            "--no-open-dist",
        ]
    )

    assert command.run(args) == 0

    options = captured["options"].normalized()
    assert captured["project_path"] == str(tmp_path)
    assert options.target is TargetOS.LINUX
    assert options.mode is BuildMode.ONEFILE
    assert options.name == "demo"
    assert options.icon == tmp_path / "icon.png"
    assert options.builder is Builder.LOCAL
    assert options.install_pyinstaller is True
    assert "Build completado correctamente" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("La estructura del proyecto no es válida: falta main.cobra", "Proyecto inválido"),
        ("La ruta del proyecto no existe: demo", "Dependencia o ruta inexistente"),
        ("sha256 esperado no coincide", "Hash incorrecto"),
        ("Conflicto de versiones para dep", "Conflicto de versiones"),
        ("PyInstaller no está instalado", "PyInstaller no disponible"),
        ("PyInstaller no soporta cross-compilation de forma nativa", "Cross-compilation solicitada"),
    ],
)
def test_installer_build_mensajes_claros(monkeypatch, tmp_path, capsys, message, expected):
    import pcobra.cobra_installer as cobra_installer

    def fake_build_project(project_path, options):
        raise CobraInstallerError(message)

    monkeypatch.setattr(cobra_installer, "build_project", fake_build_project)
    command = InstallerCommandV2()
    parser = _registered_parser(command)
    args = parser.parse_args(["installer", "build", str(tmp_path), "--target", "linux"])

    assert command.run(args) == 1
    assert expected in capsys.readouterr().out


def _registered_parser(command):
    import argparse

    root = argparse.ArgumentParser()
    subparsers = root.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return root
