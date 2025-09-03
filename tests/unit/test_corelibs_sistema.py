import subprocess
import importlib
from unittest.mock import MagicMock

import pytest

import pcobra.corelibs as core


def test_ejecutar_exitoso(monkeypatch):
    proc = MagicMock()
    proc.stdout = "ok"

    def fake_run(*a, **k):
        assert k["timeout"] == 1
        return proc

    monkeypatch.setattr(core.sistema.subprocess, "run", fake_run)
    monkeypatch.setattr(core.sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    permitido = core.sistema.os.path.realpath("/usr/bin/echo")
    assert core.ejecutar(["echo", "ok"], permitidos=[permitido], timeout=1) == "ok"


def test_ejecutar_error(monkeypatch):
    def raise_err(*a, **k):
        raise subprocess.CalledProcessError(1, a[0], stderr="fallo")

    monkeypatch.setattr(core.sistema.subprocess, "run", raise_err)
    monkeypatch.setattr(core.sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    permitido = core.sistema.os.path.realpath("/usr/bin/bad")
    assert core.ejecutar(["bad"], permitidos=[permitido], timeout=1) == "fallo"

    def raise_err2(*a, **k):
        raise subprocess.CalledProcessError(1, a[0])

    monkeypatch.setattr(core.sistema.subprocess, "run", raise_err2)
    monkeypatch.setattr(core.sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    permitido = core.sistema.os.path.realpath("/usr/bin/bad")
    with pytest.raises(RuntimeError):
        core.ejecutar(["bad"], permitidos=[permitido], timeout=1)


def test_ejecutar_permitido_con_ruta(monkeypatch):
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core.sistema.subprocess, "run", lambda *a, **k: proc)
    permitido = core.sistema.os.path.realpath("/bin/echo")
    assert core.ejecutar(["/bin/echo", "ok"], permitidos=[permitido], timeout=1) == "ok"


def test_ejecutar_sin_lista_blanca(monkeypatch):
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core.sistema.subprocess, "run", lambda *a, **k: proc)
    monkeypatch.setattr(core.sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    monkeypatch.delenv(core.sistema.WHITELIST_ENV, raising=False)
    with pytest.raises(ValueError):
        core.ejecutar(["echo", "ok"], timeout=1)


def test_ejecutar_env_ignora_cambios(monkeypatch):
    permitido = "/usr/bin/echo"
    monkeypatch.setenv(core.sistema.WHITELIST_ENV, permitido)
    importlib.reload(core.sistema)

    monkeypatch.setenv(core.sistema.WHITELIST_ENV, "/usr/bin/false")
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core.sistema.subprocess, "run", lambda *a, **k: proc)
    monkeypatch.setattr(core.sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    assert core.sistema.ejecutar(["echo", "ok"], timeout=1) == "ok"
    with pytest.raises(ValueError):
        core.sistema.ejecutar(["false"], timeout=1)


def test_ejecutar_comando_vacio():
    with pytest.raises(ValueError, match="Comando vacío"):
        core.ejecutar([], permitidos=[], timeout=1)


def test_ejecutar_timeout_expira(monkeypatch):
    def raise_timeout(*a, **k):
        raise subprocess.TimeoutExpired(a[0], k.get("timeout"))

    monkeypatch.setattr(core.sistema.subprocess, "run", raise_timeout)
    monkeypatch.setattr(core.sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    permitido = core.sistema.os.path.realpath("/usr/bin/echo")
    with pytest.raises(RuntimeError, match="Tiempo de espera agotado"):
        core.ejecutar(["echo", "ok"], permitidos=[permitido], timeout=1)
