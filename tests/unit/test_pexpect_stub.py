"""Pruebas específicas para la implementación ligera de ``pexpect``."""

from __future__ import annotations

import sys

import pytest

from pcobra._stubs import pexpect


def test_spawn_split_string_command_without_shell_injection() -> None:
    """Verifica que los comandos se dividan sin ejecutar inyecciones."""

    command = f"{sys.executable} -c \"print('ok')\"; echo HACK"
    child = pexpect.spawn(command, timeout=3)

    child.expect("ok")

    with pytest.raises(EOFError):
        child.expect("HACK", timeout=1)

    child.wait()
    assert child.exitstatus == 0


def test_spawn_accepts_executable_and_args_like_real_pexpect() -> None:
    """Admite separar el ejecutable de sus argumentos como ``pexpect`` real."""

    child = pexpect.spawn(
        sys.executable,
        args=["-c", "print('firma compatible')"],
        timeout=3,
    )

    child.expect("firma compatible")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0
