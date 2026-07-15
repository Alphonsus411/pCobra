import logging
import sys
import types

import sys

import pytest

from core import resource_limits


@pytest.mark.windows
def test_limitar_memoria_sin_resource_y_psutil_sin_rlimit(monkeypatch, caplog):
    monkeypatch.delitem(sys.modules, "resource", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", True)
    monkeypatch.setattr(resource_limits, "_WINDOWS_SKIP_LOGGED", False)
    fake_psutil = types.SimpleNamespace(
        Process=lambda: types.SimpleNamespace(),
        RLIMIT_AS=0,
    )
    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    with caplog.at_level(logging.INFO):
        resource_limits.limitar_memoria_mb(1)
    assert not any(
        "psutil.Process no soporta 'rlimit'" in r.message for r in caplog.records
    )
    assert not any(
        "No se pudo establecer el límite de memoria en Windows" in r.message
        for r in caplog.records
    )
    info_records = [
        r
        for r in caplog.records
        if (
            r.levelno == logging.INFO
            and "Los límites de recursos no son compatibles con Windows; se omiten."
            in r.message
        )
    ]
    assert len(info_records) == 1


@pytest.mark.windows
def test_limitar_cpu_sin_resource_y_psutil_sin_rlimit(monkeypatch, caplog):
    monkeypatch.delitem(sys.modules, "resource", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", True)
    monkeypatch.setattr(resource_limits, "_WINDOWS_SKIP_LOGGED", False)
    fake_psutil = types.SimpleNamespace(
        Process=lambda: types.SimpleNamespace(),
        RLIMIT_CPU=0,
    )
    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    with caplog.at_level(logging.INFO):
        resource_limits.limitar_cpu_segundos(1)
    assert not any(
        "psutil.Process no soporta 'rlimit'" in r.message for r in caplog.records
    )
    assert not any(
        "No se pudo establecer el límite de CPU en Windows" in r.message
        for r in caplog.records
    )
    info_records = [
        r
        for r in caplog.records
        if (
            r.levelno == logging.INFO
            and "Los límites de recursos no son compatibles con Windows; se omiten."
            in r.message
        )
    ]
    assert len(info_records) == 1


@pytest.mark.skipif(sys.platform != "linux", reason="resource module is Unix-specific")
def test_limitar_memoria_no_usa_resource_ni_psutil_en_linux(monkeypatch, caplog):
    import resource

    def fail_setrlimit(*args, **kwargs):
        raise AssertionError("no debe aplicarse setrlimit en el anfitrión")

    monkeypatch.setattr(resource, "setrlimit", fail_setrlimit)
    monkeypatch.delitem(sys.modules, "psutil", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", False)

    with caplog.at_level(logging.ERROR):
        resource_limits.limitar_memoria_mb(1)

    assert not caplog.records


@pytest.mark.skipif(sys.platform != "linux", reason="resource module is Unix-specific")
def test_limitar_cpu_no_usa_resource_ni_psutil_en_linux(monkeypatch, caplog):
    import resource

    def fail_setrlimit(*args, **kwargs):
        raise AssertionError("no debe aplicarse setrlimit en el anfitrión")

    monkeypatch.setattr(resource, "setrlimit", fail_setrlimit)
    monkeypatch.delitem(sys.modules, "psutil", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", False)

    with caplog.at_level(logging.ERROR):
        resource_limits.limitar_cpu_segundos(1)

    assert not caplog.records
