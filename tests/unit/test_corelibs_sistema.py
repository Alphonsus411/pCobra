import subprocess
from unittest.mock import MagicMock
import pytest

import backend.corelibs as core


def test_ejecutar_exitoso(monkeypatch):
    proc = MagicMock()
    proc.stdout = 'ok'
    monkeypatch.setattr(core.sistema.subprocess, 'run', lambda *a, **k: proc)
    assert core.ejecutar('echo ok') == 'ok'


def test_ejecutar_error(monkeypatch):
    def raise_err(*a, **k):
        raise subprocess.CalledProcessError(1, a[0], stderr='fallo')

    monkeypatch.setattr(core.sistema.subprocess, 'run', raise_err)
    assert core.ejecutar('bad') == 'fallo'

    def raise_err2(*a, **k):
        raise subprocess.CalledProcessError(1, a[0])

    monkeypatch.setattr(core.sistema.subprocess, 'run', raise_err2)
    with pytest.raises(RuntimeError):
        core.ejecutar('bad')
