import platform
import warnings

import pytest

from pcobra.cobra_installer.targets import (
    Builder,
    BuilderConfig,
    TargetOS,
    detect_host_os,
    expected_artifact_for,
    normalize_target,
    validate_target,
)


def test_detect_host_os_normaliza_platforms(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    assert detect_host_os() is TargetOS.WINDOWS
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    assert detect_host_os() is TargetOS.LINUX
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    assert detect_host_os() is TargetOS.MACOS


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("windows", TargetOS.WINDOWS),
        ("win32", TargetOS.WINDOWS),
        ("linux", TargetOS.LINUX),
        ("gnu_linux", TargetOS.LINUX),
        ("macos", TargetOS.MACOS),
        ("darwin", TargetOS.MACOS),
        ("osx", TargetOS.MACOS),
    ],
)
def test_normalize_target_acepta_aliases(raw, expected):
    assert normalize_target(raw) is expected


def test_expected_artifact_for_declara_formatos_finales():
    assert expected_artifact_for("windows").extension == ".exe"
    assert expected_artifact_for("linux").description == "binario ELF"
    assert expected_artifact_for("macos").bundle_extension == ".app"


def test_validate_target_advierte_en_cross_compilation(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    with pytest.warns(RuntimeWarning) as captured:
        assert validate_target("windows") is TargetOS.WINDOWS
    message = str(captured[0].message)
    assert "PyInstaller no soporta cross-compilation de forma nativa" in message
    assert "Docker" in message
    assert "Máquina Virtual" in message
    assert "runner CI/CD" in message
    assert "builder remoto" in message


def test_validate_target_no_advierte_en_host_actual(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        assert validate_target("linux") is TargetOS.LINUX
    assert captured == []


def test_builder_config_prepara_opciones_futuras():
    assert Builder.from_value("docker") is Builder.DOCKER
    assert Builder.from_value("vm") is Builder.VM
    assert Builder.from_value("ci") is Builder.CI
    assert Builder.from_value("remote") is Builder.REMOTE
    assert BuilderConfig.from_value("remote") == BuilderConfig(builder=Builder.REMOTE)
