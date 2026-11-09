"""Regresiones de autorización de shell sin cambiar el contrato público."""

from __future__ import annotations

import subprocess

import pytest

from pcobra.corelibs import proceso


@pytest.mark.parametrize("funcion", (proceso.ejecutar, proceso.capturar))
def test_shell_no_autorizado_no_alcanza_subprocess(monkeypatch, funcion):
    llamadas = []

    def fake_run(*args, **kwargs):
        llamadas.append((args, kwargs))
        raise AssertionError("subprocess.run no debe ejecutarse")

    monkeypatch.setattr(proceso.subprocess, "run", fake_run)

    with pytest.raises(PermissionError, match="autorizar_shell=True"):
        funcion("echo seguro && echo inesperado", shell=True)

    assert llamadas == []


def test_comando_no_confiable_no_activa_shell_por_defecto(monkeypatch):
    llamadas = []

    def fake_run(*args, **kwargs):
        llamadas.append((args, kwargs))
        return subprocess.CompletedProcess(args[0], 0, "", "")

    monkeypatch.setattr(proceso.subprocess, "run", fake_run)

    comando = "echo seguro && echo inesperado"
    proceso.ejecutar(comando)

    assert len(llamadas) == 1
    args, kwargs = llamadas[0]
    assert args[0] == [comando]
    assert kwargs["shell"] is False
