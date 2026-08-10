"""Regresiones de capacidades para la superficie pública ``proceso``."""

from __future__ import annotations

import inspect

import pytest

from pcobra.cobra.usar_capabilities import (
    CapacidadUsar,
    capacidades_de,
    simbolo_canonico,
)
from pcobra.cobra.usar_loader import usar_modulo
from pcobra.corelibs import proceso

EXPORTS_QUE_CREAN_PROCESOS = (
    "ejecutar",
    "capturar",
    "ejecutar_async",
    "ejecutar_stream",
)


def test_modo_seguro_conserva_exports_puros_de_proceso():
    exports = usar_modulo("proceso", safe_mode=True)
    resultado = {"codigo": 7, "salida": "out", "error": "err"}

    assert exports["codigo_salida"](resultado) == 7
    assert exports["salida"](resultado) == "out"
    assert exports["errores"](resultado) == "err"


@pytest.mark.parametrize("nombre", EXPORTS_QUE_CREAN_PROCESOS)
def test_modo_seguro_deniega_todos_los_exports_que_crean_procesos(nombre):
    simbolo = usar_modulo("proceso", safe_mode=True)[nombre]

    with pytest.raises(PermissionError, match="process.spawn"):
        simbolo("programa-inexistente")


def test_capturar_no_alcanza_subprocess_si_ejecutar_publico_esta_bloqueado(monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        proceso.subprocess, "run", lambda *a, **k: llamadas.append((a, k))
    )
    exports = usar_modulo("proceso", safe_mode=True)

    with pytest.raises(PermissionError, match="process.spawn"):
        exports["ejecutar"]("programa")
    with pytest.raises(PermissionError, match="process.spawn"):
        exports["capturar"]("programa")

    assert llamadas == []


def test_reproduce_bypass_de_bloquear_solo_el_export_ejecutar(monkeypatch):
    """Documenta por qué bloquear un nombre, en vez de su capacidad, era insuficiente."""

    llamadas = []
    monkeypatch.setattr(
        proceso.subprocess,
        "run",
        lambda *a, **k: llamadas.append((a, k))
        or type("Completado", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
    )
    superficie_ingenua = {
        "ejecutar": lambda *a, **k: (_ for _ in ()).throw(PermissionError()),
        "capturar": proceso.capturar,
    }

    with pytest.raises(PermissionError):
        superficie_ingenua["ejecutar"]("programa")
    superficie_ingenua["capturar"]("programa")

    assert len(llamadas) == 1


def test_alias_capturar_hereda_capacidades_del_simbolo_canonico():
    assert simbolo_canonico("proceso", "capturar") == ("proceso", "ejecutar")
    assert capacidades_de("proceso", "capturar") == frozenset(
        {CapacidadUsar.PROCESS_SPAWN}
    )


def test_contrato_no_depende_de_atributos_mutables_del_callable():
    proceso.capturar.capacidades = frozenset()  # type: ignore[attr-defined]
    try:
        assert capacidades_de("proceso", "capturar") == frozenset(
            {CapacidadUsar.PROCESS_SPAWN}
        )
    finally:
        del proceso.capturar.capacidades  # type: ignore[attr-defined]


def test_modo_seguro_deniega_shell_siempre():
    ejecutar = usar_modulo("proceso", safe_mode=True)["ejecutar"]
    with pytest.raises(PermissionError, match="process.shell"):
        ejecutar("echo no", shell=True, autorizar_shell=True)


def test_modo_no_seguro_exige_autorizacion_shell(monkeypatch):
    monkeypatch.setattr(
        proceso.subprocess,
        "run",
        lambda *args, **kwargs: type(
            "Completado", (), {"returncode": 0, "stdout": "ok", "stderr": ""}
        )(),
    )
    ejecutar = usar_modulo("proceso", safe_mode=False)["ejecutar"]

    with pytest.raises(PermissionError, match="autorizar_shell=True"):
        ejecutar("echo no", shell=True)
    assert ejecutar("echo si", shell=True, autorizar_shell=True)["salida"] == "ok"


@pytest.mark.parametrize("campo", ("shell", "autorizar_shell"))
def test_modo_no_seguro_exige_booleanos_validos(campo):
    opciones = {campo: 1}
    with pytest.raises(TypeError, match="deben ser booleanos"):
        proceso.ejecutar("programa", **opciones)


def test_exports_async_conservan_su_forma_publica():
    assert inspect.iscoroutinefunction(proceso.ejecutar_async)
    assert inspect.isasyncgenfunction(proceso.ejecutar_stream)
