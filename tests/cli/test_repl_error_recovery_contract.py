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
            "si verdadero:",
            "si verdadero:",
            "    imprimir(\"interno\")",
            "fin",
            "    imprimir(\"externo\")",
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

    ejecutar_spy.assert_called_once()
    args, kwargs = ejecutar_spy.call_args
    assert args[:2] == (
        'si verdadero:\nsi verdadero:\nimprimir("interno")\nfin\nimprimir("externo")\nfin',
        None,
    )
    assert "ast_preparseado" in kwargs
    assert prompts[:6] == [">>> ", "... ", "... ", "... ", "... ", "... "]


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

    assert any("'fin'" in msg and "inesperado" in msg for msg in errores)
    ejecutar_spy.assert_called_once()
    args, kwargs = ejecutar_spy.call_args
    assert args[:2] == ('imprimir("ok")', None)
    assert "ast_preparseado" in kwargs
    assert cmd._estado_repl["buffer_lineas"] == []
    assert cmd._estado_repl["nivel_bloque"] == 0


@pytest.mark.integration
def test_repl_error_runtime_no_cierra_sesion_y_permite_recuperacion(monkeypatch):
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(['imprimir("boom")', 'imprimir("sigue")', "salir"])
    errores: list[str] = []

    def _leer_linea(_prompt: str) -> str:
        return next(entradas)

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.mostrar_error",
        lambda mensaje, registrar_log=False: errores.append(str(mensaje)),
    )

    def _ejecutar_codigo(codigo: str, _validador, ast_preparseado=None):
        if codigo == 'imprimir("boom")':
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


@pytest.mark.integration
@pytest.mark.parametrize(
    ("linea", "exc"),
    [
        ('usar "numpy"', ValueError("usar_error[modulo_fuera_catalogo_publico] numpy")),
        ('usar "datos"', ValueError("usar_error[export_invalido]: sanitize vacío")),
        ('usar "texto"', RuntimeError("usar_error[import_circular_controlado]: texto")),
        ('usar "numero"', ValueError("usar_error[conflicto_simbolo]: no idempotente")),
    ],
)
def test_repl_usar_errores_esperados_solo_mensaje_breve_sin_traceback(
    monkeypatch, linea, exc
):
    cmd = InteractiveCommand(MagicMock())
    entradas = iter([linea, "salir"])
    errores: list[str] = []
    logs_debug: list[str] = []

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.mostrar_error",
        lambda mensaje, registrar_log=False: errores.append(str(mensaje)),
    )
    monkeypatch.setattr(
        cmd.logger,
        "debug",
        lambda mensaje, *args, **kwargs: logs_debug.append(str(mensaje)),
    )

    def _leer_linea(_prompt: str) -> str:
        return next(entradas)

    def _ejecutar_codigo(codigo: str, _validador, ast_preparseado=None):
        if codigo == linea:
            raise exc

    monkeypatch.setattr(cmd, "ejecutar_codigo", _ejecutar_codigo)
    cmd._debug_mode = False

    cmd._run_repl_loop(
        args=SimpleNamespace(),
        validador=None,
        leer_linea=_leer_linea,
        sandbox=False,
        sandbox_docker=None,
    )

    assert errores
    assert any(msg.startswith("usar_error[") for msg in errores)
    assert not any("Traceback" in msg for msg in errores)
    assert not any("Traceback" in msg for msg in logs_debug)


@pytest.mark.integration
def test_repl_usar_error_debug_incluye_traceback(monkeypatch):
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(['usar "texto"', "salir"])
    errores: list[str] = []
    logs_debug: list[str] = []

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.interactive_cmd.mostrar_error",
        lambda mensaje, registrar_log=False: errores.append(str(mensaje)),
    )
    monkeypatch.setattr(
        cmd.logger,
        "debug",
        lambda mensaje, *args, **kwargs: logs_debug.append(str(mensaje)),
    )

    def _leer_linea(_prompt: str) -> str:
        return next(entradas)

    def _ejecutar_codigo(codigo: str, _validador, ast_preparseado=None):
        if codigo == 'usar "texto"':
            raise RuntimeError("usar_error[import_circular_controlado]: texto")

    monkeypatch.setattr(cmd, "ejecutar_codigo", _ejecutar_codigo)
    cmd._debug_mode = True

    cmd._run_repl_loop(
        args=SimpleNamespace(),
        validador=None,
        leer_linea=_leer_linea,
        sandbox=False,
        sandbox_docker=None,
    )

    assert errores and errores[0].startswith("usar_error[")
    assert any("usar_error[import_circular_controlado]" in msg for msg in logs_debug)
