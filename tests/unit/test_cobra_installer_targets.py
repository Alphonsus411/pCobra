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


@pytest.mark.parametrize(
    ("target", "expected", "attribute", "value"),
    [
        ("windows", TargetOS.WINDOWS, "extension", ".exe"),
        ("linux", TargetOS.LINUX, "description", "binario ELF"),
        ("macos", TargetOS.MACOS, "bundle_extension", ".app"),
    ],
)
def test_targets_principales_declaran_artefacto_esperado(
    target, expected, attribute, value
):
    assert normalize_target(target) is expected
    artifact = expected_artifact_for(target)
    assert getattr(artifact, attribute) == value


@pytest.mark.parametrize(
    ("host_system", "target", "expected"),
    [
        ("Windows", "windows", TargetOS.WINDOWS),
        ("Linux", "linux", TargetOS.LINUX),
        ("Darwin", "macos", TargetOS.MACOS),
    ],
)
def test_validate_target_no_advierte_si_target_es_igual_al_host(
    monkeypatch, host_system, target, expected
):
    monkeypatch.setattr(platform, "system", lambda: host_system)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        assert validate_target(target) is expected
    assert captured == []


@pytest.mark.parametrize(
    ("host_system", "target", "expected"),
    [
        ("Linux", "windows", TargetOS.WINDOWS),
        ("Windows", "linux", TargetOS.LINUX),
        ("Linux", "macos", TargetOS.MACOS),
    ],
)
def test_validate_target_advierte_si_target_es_diferente_al_host(
    monkeypatch, host_system, target, expected
):
    monkeypatch.setattr(platform, "system", lambda: host_system)

    with pytest.warns(RuntimeWarning) as captured:
        assert validate_target(target) is expected

    message = str(captured[0].message)
    assert "PyInstaller no soporta cross-compilation de forma nativa" in message
    assert "Docker" in message
    assert "Máquina Virtual" in message
    assert "runner CI/CD" in message
    assert "builder remoto" in message


@pytest.mark.parametrize("invalid_target", ["freebsd", "", "windows-arm64"])
def test_normalize_target_rechaza_target_invalido(invalid_target):
    with pytest.raises(ValueError) as excinfo:
        normalize_target(invalid_target)

    message = str(excinfo.value)
    assert f"Target no soportado: {invalid_target!r}" in message
    assert "windows, linux, macos, current" in message


def test_builder_config_prepara_opciones_futuras():
    assert Builder.from_value("docker") is Builder.DOCKER
    assert Builder.from_value("vm") is Builder.VM
    assert Builder.from_value("ci") is Builder.CI
    assert Builder.from_value("remote") is Builder.REMOTE
    assert BuilderConfig.from_value("remote") == BuilderConfig(builder=Builder.REMOTE)
