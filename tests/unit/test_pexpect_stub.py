"""Pruebas específicas para la implementación ligera de ``pexpect``."""

from __future__ import annotations

import sys

import pytest

import pexpect


def test_spawn_split_string_command_without_shell_injection() -> None:
    """Verifica que los comandos se dividan sin ejecutar inyecciones."""

    command = f"{sys.executable} -c \"print('ok')\"; echo HACK"
    child = pexpect.spawn(command, timeout=3)

    child.expect("ok")

    with pytest.raises(EOFError):
        child.expect("HACK", timeout=1)

    child.wait()
    assert child.exitstatus == 0
