from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand


@pytest.mark.integration
def test_repl_bloque_incompleto_con_fin_anidado_sigue_acumulando(monkeypatch):
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(
        [
            "si 1 == 1 :",
            "si 2 == 2 :",
            "imprimir(\"interno\")",
            "fin",
            "imprimir(\"externo\")",
            "fin",
            "salir",
        ]
    )
    prompts: list[str] = []

    def _leer_linea(prompt: str) -> str:
        prompts.append(prompt)
        return next(entradas)

    ejecutar_spy = MagicMock()
    monkeypatch.setattr(cmd, "ejecutar_codigo", ejecutar_spy)

    cmd._run_repl_loop(
        args=SimpleNamespace(),
        validador=None,
        leer_linea=_leer_linea,
        sandbox=False,
        sandbox_docker=None,
    )

    ejecutar_spy.assert_called_once_with(
        'si 1 == 1 :\nsi 2 == 2 :\nimprimir("interno")\nfin\nimprimir("externo")\nfin',
        None,
    )
    assert prompts[:6] == ["cobra> ", "... ", "... ", "... ", "... ", "... "]


@pytest.mark.integration
def test_repl_error_sintactico_por_cierre_extra_reporta_y_acepta_nuevas_entradas(monkeypatch):
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["fin", 'imprimir("ok")', "salir"])
    errores: list[str] = []

    def _leer_linea(_prompt: str) -> str:
        return next(entradas)

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.mostrar_error",
        lambda mensaje, registrar_log=False: errores.append(str(mensaje)),
    )

    ejecutar_spy = MagicMock()
    monkeypatch.setattr(cmd, "ejecutar_codigo", ejecutar_spy)

    cmd._run_repl_loop(
        args=SimpleNamespace(),
        validador=None,
        leer_linea=_leer_linea,
        sandbox=False,
        sandbox_docker=None,
    )

    assert any("'fin' sin bloque abierto" in msg for msg in errores)
    ejecutar_spy.assert_called_once_with('imprimir("ok")', None)
    assert cmd._estado_repl["buffer_lineas"] == []
    assert cmd._estado_repl["nivel_bloque"] == 0


@pytest.mark.integration
def test_repl_error_runtime_no_cierra_sesion_y_permite_recuperacion(monkeypatch):
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["romper()", 'imprimir("sigue")', "salir"])
    errores: list[str] = []

    def _leer_linea(_prompt: str) -> str:
        return next(entradas)

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.mostrar_error",
        lambda mensaje, registrar_log=False: errores.append(str(mensaje)),
    )

    def _ejecutar_codigo(codigo: str, _validador):
        if codigo == "romper()":
            raise RuntimeError("fallo de runtime controlado")

    monkeypatch.setattr(cmd, "ejecutar_codigo", _ejecutar_codigo)

    cmd._run_repl_loop(
        args=SimpleNamespace(),
        validador=None,
        leer_linea=_leer_linea,
        sandbox=False,
        sandbox_docker=None,
    )

    assert any("fallo de runtime controlado" in msg for msg in errores)
    assert cmd._estado_repl["nivel_bloque"] == 0
    assert cmd._estado_repl["buffer_lineas"] == []
