import asyncio
import os
import subprocess
import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import pcobra.corelibs as core
import pcobra.corelibs.sistema as core_sistema


CASE_INSENSITIVE_OS = os.path.normcase("Aa") == os.path.normcase("aa")


def test_ejecutar_exitoso(monkeypatch):
    proc = MagicMock()
    proc.stdout = "ok"

    def fake_run(*a, **k):
        assert k["timeout"] == 1
        return proc

    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)
    monkeypatch.setattr(core_sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    permitido = core_sistema.os.path.realpath("/usr/bin/echo")
    assert core.ejecutar(["echo", "ok"], permitidos=[permitido], timeout=1) == "ok"


def test_ejecutar_error(monkeypatch, tmp_path):
    def raise_err(*a, **k):
        raise subprocess.CalledProcessError(1, a[0], stderr="fallo")

    monkeypatch.setattr(core_sistema.subprocess, "run", raise_err)
    permitido = tmp_path / "bad"
    permitido.write_text("")
    permitido.chmod(0o755)

    def fake_which(binario: str) -> str | None:
        return str(permitido) if binario == "bad" else None

    monkeypatch.setattr(core_sistema.shutil, "which", fake_which)
    permitido_real = core_sistema.os.path.realpath(str(permitido))
    assert (
        core.ejecutar(["bad"], permitidos=[permitido_real], timeout=1) == "fallo"
    )

    def raise_err2(*a, **k):
        raise subprocess.CalledProcessError(1, a[0])

    monkeypatch.setattr(core_sistema.subprocess, "run", raise_err2)
    monkeypatch.setattr(core_sistema.shutil, "which", fake_which)
    with pytest.raises(RuntimeError):
        core.ejecutar(["bad"], permitidos=[permitido_real], timeout=1)


def test_ejecutar_permitido_con_ruta(monkeypatch):
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core_sistema.subprocess, "run", lambda *a, **k: proc)
    permitido = core_sistema.os.path.realpath("/bin/echo")
    assert core.ejecutar(["/bin/echo", "ok"], permitidos=[permitido], timeout=1) == "ok"


def test_ejecutar_reemplaza_y_copia_argumentos(monkeypatch):
    permitido = core_sistema.os.path.realpath("/usr/bin/env")
    comando = ["env", "VAR=1"]
    llamado: dict[str, list[str]] = {}

    monkeypatch.setattr(core_sistema.os, "name", "posix", raising=False)
    monkeypatch.setattr(core_sistema.sys, "platform", "linux", raising=False)

    def fake_which(binario: str) -> str | None:
        return permitido if binario == "env" else None

    def fake_run(args, **kwargs):
        llamado["args"] = args
        comando[0] = "otro"
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(core_sistema.shutil, "which", fake_which)
    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)

    salida = core.ejecutar(comando, permitidos=[permitido])

    assert salida == ""
    assert llamado["args"][0].startswith("/proc/self/fd/")
    assert llamado["args"] is not comando
    assert comando[0] == "otro"


def test_ejecutar_no_usa_proc_self_en_darwin(monkeypatch, tmp_path):
    ejecutable = tmp_path / "prog"
    ejecutable.write_text("#!/bin/sh\nexit 0\n")
    ejecutable.chmod(0o755)

    permitido = core_sistema.os.path.realpath(str(ejecutable))
    llamado: dict[str, list[str]] = {}

    def fake_run(args, **kwargs):
        llamado["args"] = args
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(core_sistema.os, "name", "posix", raising=False)
    monkeypatch.setattr(core_sistema.sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)

    salida = core_sistema.ejecutar([str(ejecutable)], permitidos=[permitido])

    assert salida == ""
    assert llamado["args"][0] == permitido


@pytest.mark.asyncio
async def test_ejecutar_async_reemplaza_y_copia_argumentos(monkeypatch):
    permitido = core_sistema.os.path.realpath("/usr/bin/env")
    comando = ["env"]
    llamado: dict[str, list[str]] = {}

    monkeypatch.setattr(core_sistema.os, "name", "posix", raising=False)
    monkeypatch.setattr(core_sistema.sys, "platform", "linux", raising=False)

    def fake_which(binario: str) -> str | None:
        return permitido if binario == "env" else None

    class FakeProc:
        returncode = 0
        stdout = None
        stderr = None

        async def communicate(self):
            return b"", b""

    async def fake_create_subprocess_exec(*args, **kwargs):
        llamado["args"] = list(args)
        comando[0] = "otro"
        return FakeProc()

    monkeypatch.setattr(core_sistema.shutil, "which", fake_which)
    monkeypatch.setattr(
        core_sistema.asyncio, "create_subprocess_exec", fake_create_subprocess_exec
    )

    salida = await core_sistema.ejecutar_async(comando, permitidos=[permitido])

    assert salida == ""
    assert llamado["args"][0].startswith("/proc/self/fd/")
    assert comando[0] == "otro"


@pytest.mark.asyncio
async def test_ejecutar_async_no_usa_proc_self_en_darwin(monkeypatch):
    permitido = core_sistema.os.path.realpath("/usr/bin/env")
    comando = ["env"]
    llamado: dict[str, list[str]] = {}

    class FakeProc:
        returncode = 0
        stdout = None
        stderr = None

        async def communicate(self):
            return b"", b""

    async def fake_create_subprocess_exec(*args, **kwargs):
        llamado["args"] = list(args)
        return FakeProc()

    monkeypatch.setattr(core_sistema.os, "name", "posix", raising=False)
    monkeypatch.setattr(core_sistema.sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(
        core_sistema.asyncio, "create_subprocess_exec", fake_create_subprocess_exec
    )

    salida = await core_sistema.ejecutar_async(comando, permitidos=[permitido])

    assert salida == ""
    assert llamado["args"][0] == permitido


@pytest.mark.asyncio
async def test_ejecutar_stream_no_usa_proc_self_en_darwin(monkeypatch):
    permitido = core_sistema.os.path.realpath("/usr/bin/env")
    comando = ["env"]
    llamado: dict[str, list[str]] = {}

    class FakeStdout:
        def __init__(self) -> None:
            self._chunks = [b"linea\n", b""]

        async def readline(self) -> bytes:
            return self._chunks.pop(0)

    class FakeStderr:
        async def read(self) -> bytes:
            return b""

    class FakeProc:
        returncode = 0

        def __init__(self) -> None:
            self.stdout = FakeStdout()
            self.stderr = FakeStderr()

        async def wait(self) -> int:
            return 0

    async def fake_create_subprocess_exec(*args, **kwargs):
        llamado["args"] = list(args)
        return FakeProc()

    monkeypatch.setattr(core_sistema.os, "name", "posix", raising=False)
    monkeypatch.setattr(core_sistema.sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(
        core_sistema.asyncio, "create_subprocess_exec", fake_create_subprocess_exec
    )

    resultado = [
        linea
        async for linea in core_sistema.ejecutar_stream(
            comando, permitidos=[permitido]
        )
    ]

    assert resultado == ["linea\n"]
    assert llamado["args"][0] == permitido


def test_ejecutar_detecta_reemplazo(monkeypatch, tmp_path):
    original = tmp_path / "programa"
    original.write_text("echo")
    original.chmod(0o755)
    permitido = core_sistema.os.path.realpath(str(original))

    ejecutado = False

    def fake_run(*args, **kwargs):
        nonlocal ejecutado
        ejecutado = True
        return SimpleNamespace(stdout="", stderr="")

    real_resolver = core_sistema._resolver_ejecutable

    def fake_resolver(cmd, permitidos):
        resultado = real_resolver(cmd, permitidos)
        reemplazo = tmp_path / "programa_nuevo"
        reemplazo.write_text("otro")
        reemplazo.chmod(0o755)
        os.replace(reemplazo, original)
        return resultado

    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)
    monkeypatch.setattr(core_sistema, "_resolver_ejecutable", fake_resolver)

    with pytest.raises(RuntimeError, match="cambió"):
        core_sistema.ejecutar([str(original)], permitidos=[permitido])

    assert not ejecutado


def test_ejecutar_detecta_reemplazo_en_windows(monkeypatch, tmp_path):
    original = tmp_path / "programa.exe"
    original.write_text("echo")
    original.chmod(0o755)
    permitido = core_sistema.os.path.realpath(str(original))

    ejecutado = False

    def fake_run(*args, **kwargs):
        nonlocal ejecutado
        ejecutado = True
        return SimpleNamespace(stdout="", stderr="")

    real_resolver = core_sistema._resolver_ejecutable

    def fake_resolver(cmd, permitidos):
        resultado = real_resolver(cmd, permitidos)
        reemplazo = tmp_path / "programa_nuevo.exe"
        reemplazo.write_text("otro")
        reemplazo.chmod(0o755)
        os.replace(reemplazo, original)
        return resultado

    monkeypatch.setattr(core_sistema.os, "name", "nt")
    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)
    monkeypatch.setattr(core_sistema, "_resolver_ejecutable", fake_resolver)

    with pytest.raises(RuntimeError, match="cambió"):
        core_sistema.ejecutar([str(original)], permitidos=[permitido])

    assert not ejecutado


def test_ejecutar_sin_lista_blanca(monkeypatch):
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core_sistema.subprocess, "run", lambda *a, **k: proc)
    monkeypatch.setattr(core_sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    monkeypatch.delenv(core_sistema.WHITELIST_ENV, raising=False)
    with pytest.raises(ValueError):
        core.ejecutar(["echo", "ok"], timeout=1)


def test_ejecutar_env_ignora_cambios(monkeypatch):
    permitido = "/usr/bin/echo"
    monkeypatch.setenv(core_sistema.WHITELIST_ENV, permitido)
    importlib.reload(core_sistema)

    monkeypatch.setenv(core_sistema.WHITELIST_ENV, "/usr/bin/false")
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core_sistema.subprocess, "run", lambda *a, **k: proc)
    monkeypatch.setattr(core_sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    assert core_sistema.ejecutar(["echo", "ok"], timeout=1) == "ok"
    with pytest.raises(ValueError):
        core_sistema.ejecutar(["false"], timeout=1)


def test_ejecutar_comando_vacio():
    with pytest.raises(ValueError, match="Comando vacío"):
        core.ejecutar([], permitidos=[], timeout=1)


def test_ejecutar_timeout_expira(monkeypatch):
    def raise_timeout(*a, **k):
        raise subprocess.TimeoutExpired(a[0], k.get("timeout"))

    monkeypatch.setattr(core_sistema.subprocess, "run", raise_timeout)
    monkeypatch.setattr(core_sistema.shutil, "which", lambda x: f"/usr/bin/{x}")
    permitido = core_sistema.os.path.realpath("/usr/bin/echo")
    with pytest.raises(RuntimeError, match="Tiempo de espera agotado"):
        core.ejecutar(["echo", "ok"], permitidos=[permitido], timeout=1)


@pytest.mark.skipif(
    not CASE_INSENSITIVE_OS,
    reason="Requiere sistema de archivos insensible a mayúsculas",
)
def test_ejecutar_compara_rutas_normalizadas_en_os_insensible(monkeypatch, tmp_path):
    proc = MagicMock()
    proc.stdout = "ok"
    monkeypatch.setattr(core_sistema.subprocess, "run", lambda *a, **k: proc)

    carpeta = tmp_path / "Binario"
    carpeta.mkdir()
    ejecutable = carpeta / "MiEjecutable"
    ejecutable.write_text("echo")

    permitido = core_sistema.os.path.normcase(
        core_sistema.os.path.normpath(str(ejecutable))
    )
    comando = [str(ejecutable).upper()]

    assert core.ejecutar(comando, permitidos=[permitido], timeout=1) == "ok"
