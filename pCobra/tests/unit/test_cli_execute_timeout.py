import time
import cobra.cli.commands.execute_cmd as execute_cmd
import pytest


def _bucle_infinito():
    while True:
        time.sleep(0.1)


def _ejecutar_timeout(monkeypatch, os_name):
    monkeypatch.setattr(execute_cmd.os, "name", os_name)
    cmd = execute_cmd.ExecuteCommand()
    cmd.EXECUTION_TIMEOUT = 1
    with pytest.raises(TimeoutError):
        cmd._limitar_recursos(_bucle_infinito)


def test_timeout_unix(monkeypatch):
    _ejecutar_timeout(monkeypatch, "posix")


def test_timeout_windows(monkeypatch):
    _ejecutar_timeout(monkeypatch, "nt")

