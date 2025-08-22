import logging
import sys
import types

import pytest

from core import resource_limits


@pytest.mark.windows
def test_limitar_memoria_sin_resource_y_psutil_sin_rlimit(monkeypatch, caplog):
    monkeypatch.delitem(sys.modules, "resource", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", True)
    fake_psutil = types.SimpleNamespace(
        Process=lambda: types.SimpleNamespace(),
        RLIMIT_AS=0,
    )
    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    with caplog.at_level(logging.WARNING):
        resource_limits.limitar_memoria_mb(1)
    warn_record = next(
        (
            r
            for r in caplog.records
            if "psutil.Process no soporta 'rlimit'" in r.message
        ),
        None,
    )
    assert warn_record and warn_record.levelno == logging.WARNING
    err_record = next(
        (
            r
            for r in caplog.records
            if "No se pudo establecer el límite de memoria en Windows" in r.message
        ),
        None,
    )
    assert err_record and err_record.levelno == logging.ERROR


@pytest.mark.windows
def test_limitar_cpu_sin_resource_y_psutil_sin_rlimit(monkeypatch, caplog):
    monkeypatch.delitem(sys.modules, "resource", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", True)
    fake_psutil = types.SimpleNamespace(
        Process=lambda: types.SimpleNamespace(),
        RLIMIT_CPU=0,
    )
    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    with caplog.at_level(logging.WARNING):
        resource_limits.limitar_cpu_segundos(1)
    warn_record = next(
        (
            r
            for r in caplog.records
            if "psutil.Process no soporta 'rlimit'" in r.message
        ),
        None,
    )
    assert warn_record and warn_record.levelno == logging.WARNING
    err_record = next(
        (
            r
            for r in caplog.records
            if "No se pudo establecer el límite de CPU en Windows" in r.message
        ),
        None,
    )
    assert err_record and err_record.levelno == logging.ERROR


def test_limitar_memoria_sin_psutil_en_linux(monkeypatch, caplog):
    import resource

    def fail_setrlimit(*args, **kwargs):
        raise OSError("fail")

    monkeypatch.setattr(resource, "setrlimit", fail_setrlimit)
    monkeypatch.delitem(sys.modules, "psutil", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", False)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            resource_limits.limitar_memoria_mb(1)

    err_record = next(
        (
            r
            for r in caplog.records
            if (
                "El módulo 'psutil' no está disponible para limitar la "
                "memoria." in r.message
            )
        ),
        None,
    )
    assert err_record and err_record.levelno == logging.ERROR


def test_limitar_cpu_sin_psutil_en_linux(monkeypatch, caplog):
    import resource

    def fail_setrlimit(*args, **kwargs):
        raise OSError("fail")

    monkeypatch.setattr(resource, "setrlimit", fail_setrlimit)
    monkeypatch.delitem(sys.modules, "psutil", raising=False)
    monkeypatch.setattr(resource_limits, "IS_WINDOWS", False)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            resource_limits.limitar_cpu_segundos(1)

    err_record = next(
        (
            r
            for r in caplog.records
            if (
                "El módulo 'psutil' no está disponible para limitar la "
                "CPU." in r.message
            )
        ),
        None,
    )
    assert err_record and err_record.levelno == logging.ERROR
