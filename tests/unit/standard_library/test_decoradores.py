from __future__ import annotations

import asyncio
import warnings

import pytest

from pcobra.standard_library import decoradores


EXPECTED_DECORATORS = {
    "memoizar",
    "dataclase",
    "temporizar",
    "depreciado",
    "sincronizar",
    "reintentar",
    "reintentar_async",
    "orden_total",
    "despachar_por_tipo",
}


def test_decoradores_exporta_inventario_esperado():
    assert set(decoradores.__all__) == EXPECTED_DECORATORS


def test_memoizar_reutiliza_resultado_en_llamadas_repetidas():
    llamadas = {"total": 0}

    @decoradores.memoizar(maxsize=16)
    def duplicar(valor: int) -> int:
        llamadas["total"] += 1
        return valor * 2

    assert duplicar(3) == 6
    assert duplicar(3) == 6
    assert llamadas["total"] == 1


def test_orden_total_completa_operadores_de_comparacion():
    @decoradores.orden_total
    class Prioridad:
        def __init__(self, valor: int):
            self.valor = valor

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Prioridad) and self.valor == other.valor

        def __lt__(self, other: "Prioridad") -> bool:
            return self.valor < other.valor

    assert Prioridad(1) < Prioridad(2)
    assert Prioridad(1) <= Prioridad(1)
    assert Prioridad(2) > Prioridad(1)


def test_despachar_por_tipo_registrar_y_despachar():
    @decoradores.despachar_por_tipo
    def describir(valor: object) -> str:
        return f"objeto:{valor}"

    @describir.registrar(int)
    def _describir_entero(valor: int) -> str:
        return f"entero:{valor}"

    assert describir(10) == "entero:10"
    assert describir("x") == "objeto:x"
    assert describir.despachar(int) is _describir_entero


def test_depreciado_emite_warning():
    @decoradores.depreciado(mensaje="ruta antigua", estilizar=False)
    def legacy() -> str:
        return "ok"

    with warnings.catch_warnings(record=True) as capturadas:
        warnings.simplefilter("always")
        assert legacy() == "ok"

    assert any("ruta antigua" in str(item.message) for item in capturadas)


def test_sincronizar_rechaza_corutinas():
    async def tarea() -> int:
        return 1

    with pytest.raises(TypeError, match="sincronizar solo admite funciones síncronas"):
        decoradores.sincronizar(tarea)


@pytest.mark.asyncio
async def test_reintentar_async_reintenta_hasta_exito():
    estado = {"intentos": 0}

    @decoradores.reintentar_async(intentos=3, excepciones=(ValueError,), retardo_inicial=0, estilizar=False)
    async def operacion() -> str:
        estado["intentos"] += 1
        if estado["intentos"] < 2:
            raise ValueError("fallo")
        return "ok"

    assert await operacion() == "ok"
    assert estado["intentos"] == 2


def test_reintentar_reintenta_hasta_exito(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(decoradores.time, "sleep", lambda _segundos: None)

    estado = {"intentos": 0}

    @decoradores.reintentar(intentos=3, excepciones=(RuntimeError,), retardo_inicial=0, estilizar=False)
    def operacion() -> str:
        estado["intentos"] += 1
        if estado["intentos"] < 3:
            raise RuntimeError("fallo")
        return "ok"

    assert operacion() == "ok"
    assert estado["intentos"] == 3


def test_reintentar_async_rechaza_funcion_no_async():
    def sync() -> int:
        return 1

    with pytest.raises(TypeError, match="reintentar_async requiere una corrutina"):
        decoradores.reintentar_async(sync)


def test_temporizar_funciona_tambien_en_async():
    eventos: list[str] = []

    class ConsolaFalsa:
        def print(self, mensaje: str, style: str | None = None) -> None:
            del style
            eventos.append(mensaje)

    @decoradores.temporizar(etiqueta="tarea", precision=3, consola=ConsolaFalsa())
    async def tarea() -> int:
        await asyncio.sleep(0)
        return 7

    assert asyncio.run(tarea()) == 7
    assert eventos and eventos[0].startswith("[tarea]")
