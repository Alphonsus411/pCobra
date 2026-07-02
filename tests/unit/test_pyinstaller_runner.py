from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from pcobra.cobra_installer.project import CobraInstallerError
from pcobra.cobra_installer.pyinstaller_runner import (
    detect_pyinstaller,
    install_pyinstaller_if_allowed,
    run_pyinstaller,
)


class Logger:
    def __init__(self) -> None:
        self.infos: list[str] = []
        self.errors: list[str] = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


class FakeProcess:
    def __init__(self, returncode: int = 0) -> None:
        self.stdout = iter(["paso 1\n", "paso 2\n"])
        self.stderr = iter(["aviso\n"])
        self._returncode = returncode

    def wait(self) -> int:
        return self._returncode


def completed(args: list[str], returncode: int = 0, stdout: str = "6.14.0\n", stderr: str = ""):
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def test_detect_pyinstaller_usa_python_module_y_devuelve_version() -> None:
    calls: list[list[str]] = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return completed(args, stdout="6.14.0\n")

    info = detect_pyinstaller(run_factory=fake_run, which=lambda name: None)

    assert info.available is True
    assert info.version == "6.14.0"
    assert calls == [[info.command[0], "-m", "PyInstaller", "--version"]]


def test_install_pyinstaller_rechaza_instalacion_no_habilitada() -> None:
    def fake_run(args, **kwargs):
        return completed(args, returncode=1, stdout="", stderr="No module named PyInstaller")

    with pytest.raises(CobraInstallerError, match="Habilita la instalación automática"):
        install_pyinstaller_if_allowed(SimpleNamespace(), run_factory=fake_run)


def test_install_pyinstaller_si_opcion_lo_permite() -> None:
    calls: list[list[str]] = []
    installed = False

    def fake_run(args, **kwargs):
        nonlocal installed
        calls.append(args)
        if args[1:3] == ["-m", "PyInstaller"] and not installed:
            return completed(args, returncode=1, stdout="", stderr="No module named PyInstaller")
        if args[1:4] == ["-m", "pip", "install"]:
            installed = True
            return completed(args, stdout="installed\n")
        return completed(args, stdout="6.14.0\n")

    info = install_pyinstaller_if_allowed(
        SimpleNamespace(install_pyinstaller=True), run_factory=fake_run
    )

    assert info.available is True
    assert info.version == "6.14.0"
    assert any(call[1:4] == ["-m", "pip", "install"] for call in calls)


def test_run_pyinstaller_streaming_y_resultado(tmp_path: Path) -> None:
    spec = tmp_path / "app.spec"
    spec.write_text("# spec", encoding="utf-8")
    logger = Logger()

    def fake_run(args, **kwargs):
        return completed(args, stdout="6.14.0\n")

    popen_calls: list[list[str]] = []

    def fake_popen(args, **kwargs):
        popen_calls.append(args)
        assert kwargs["stdout"] == subprocess.PIPE
        assert kwargs["stderr"] == subprocess.PIPE
        return FakeProcess()

    result = run_pyinstaller(
        spec,
        SimpleNamespace(extra_args=("--clean",)),
        logger,
        run_factory=fake_run,
        popen_factory=fake_popen,
    )

    assert result.success is True
    assert result.version == "6.14.0"
    assert result.stdout == "paso 1\npaso 2\n"
    assert result.stderr == "aviso\n"
    assert popen_calls[0][-2:] == [str(spec.resolve()), "--clean"]
    assert "paso 1" in logger.infos
    assert "aviso" in logger.errors


def test_run_pyinstaller_traduce_errores_comunes(tmp_path: Path) -> None:
    spec = tmp_path / "app.spec"
    spec.write_text("# spec", encoding="utf-8")

    def fake_run(args, **kwargs):
        return completed(args, stdout="6.14.0\n")

    class FailingProcess(FakeProcess):
        def __init__(self) -> None:
            super().__init__(returncode=1)
            self.stdout = iter([])
            self.stderr = iter(["Permission denied: dist/app\n"])

    with pytest.raises(CobraInstallerError, match="Permiso denegado"):
        run_pyinstaller(
            spec,
            SimpleNamespace(),
            Logger(),
            run_factory=fake_run,
            popen_factory=lambda args, **kwargs: FailingProcess(),
        )
