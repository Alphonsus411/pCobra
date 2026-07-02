from pathlib import Path

import pytest

from pcobra.cobra.cli.commands_v2.build_cmd import BuildCommandV2
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


def test_build_installer_alias_equivale_a_installer_build(
    monkeypatch, tmp_path, capsys
):
    import pcobra.cobra_installer as cobra_installer

    calls = []

    def fake_build_project(project_path, options):
        calls.append((project_path, options))
        return BuildResult(success=True, artifact_path=tmp_path / "dist" / "demo")

    monkeypatch.setattr(cobra_installer, "build_project", fake_build_project)
    installer_command = InstallerCommandV2()
    build_command = BuildCommandV2()
    installer_parser = _registered_parser(installer_command)
    build_parser = _registered_parser(build_command)

    installer_args = installer_parser.parse_args(["installer", "build", str(tmp_path)])
    alias_args = build_parser.parse_args(["build", "--installer", str(tmp_path)])

    installer_status = installer_command.run(installer_args)
    installer_output = capsys.readouterr().out
    alias_status = build_command.run(alias_args)
    alias_output = capsys.readouterr().out

    assert installer_status == alias_status == 0
    assert installer_output == alias_output
    assert calls[0][0] == calls[1][0] == str(tmp_path)
    assert calls[0][1].normalized() == calls[1][1].normalized()


def test_build_installer_alias_equivale_en_error(monkeypatch, tmp_path, capsys):
    import pcobra.cobra_installer as cobra_installer

    def fake_build_project(project_path, options):
        raise CobraInstallerError("La ruta del proyecto no existe: demo")

    monkeypatch.setattr(cobra_installer, "build_project", fake_build_project)
    installer_command = InstallerCommandV2()
    build_command = BuildCommandV2()
    installer_parser = _registered_parser(installer_command)
    build_parser = _registered_parser(build_command)

    installer_args = installer_parser.parse_args(["installer", "build", str(tmp_path)])
    alias_args = build_parser.parse_args(["build", "--installer", str(tmp_path)])

    installer_status = installer_command.run(installer_args)
    installer_output = capsys.readouterr().out
    alias_status = build_command.run(alias_args)
    alias_output = capsys.readouterr().out

    assert installer_status == alias_status == 1
    assert installer_output == alias_output


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (
            "La estructura del proyecto no es válida: falta main.cobra",
            "Proyecto inválido",
        ),
        ("La ruta del proyecto no existe: demo", "Dependencia o ruta inexistente"),
        ("sha256 esperado no coincide", "Hash incorrecto"),
        ("Conflicto de versiones para dep", "Conflicto de versiones"),
        ("PyInstaller no está instalado", "PyInstaller no disponible"),
        (
            "PyInstaller no soporta cross-compilation de forma nativa",
            "Cross-compilation solicitada",
        ),
    ],
)
def test_installer_build_mensajes_claros(
    monkeypatch, tmp_path, capsys, message, expected
):
    import pcobra.cobra_installer as cobra_installer

    def fake_build_project(project_path, options):
        raise CobraInstallerError(message)

    monkeypatch.setattr(cobra_installer, "build_project", fake_build_project)
    command = InstallerCommandV2()
    parser = _registered_parser(command)
    args = parser.parse_args(
        ["installer", "build", str(tmp_path), "--target", "linux"]
    )

    assert command.run(args) == 1
    assert expected in capsys.readouterr().out


def _registered_parser(command):
    import argparse

    root = argparse.ArgumentParser()
    subparsers = root.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return root


def test_installer_build_muestra_conflicto_transitivo_con_cadena(
    monkeypatch, tmp_path, capsys
):
    import pcobra.cobra_installer as cobra_installer

    def fake_build_project(project_path, options):
        raise CobraInstallerError(
            "Conflicto de versiones para compartida: se requieren versiones "
            "incompatibles 1.0.0 y 2.0.0. Cadena existente: proyecto -> "
            "dep-a==1.0.0 -> compartida==1.0.0. Cadena nueva: proyecto -> "
            "dep-b==1.0.0 -> compartida==2.0.0."
        )

    monkeypatch.setattr(cobra_installer, "build_project", fake_build_project)
    command = InstallerCommandV2()
    parser = _registered_parser(command)
    args = parser.parse_args(
        ["installer", "build", str(tmp_path), "--target", "linux"]
    )

    assert command.run(args) == 1
    output = capsys.readouterr().out
    assert "Conflicto de versiones" in output
    assert "compartida" in output
    assert "Cadena existente" in output
    assert "Cadena nueva" in output
