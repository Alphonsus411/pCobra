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
    assert any(
        "psutil.Process no soporta 'rlimit'" in record.message for record in caplog.records
    )
    assert any(
        "No se pudo establecer el límite de memoria en Windows" in record.message
        for record in caplog.records
    )


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
    assert any(
        "psutil.Process no soporta 'rlimit'" in record.message for record in caplog.records
    )
    assert any(
        "No se pudo establecer el límite de CPU en Windows" in record.message
        for record in caplog.records
    )
