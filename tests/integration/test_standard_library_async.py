import asyncio
import time

import pytest

import standard_library as stlib


@pytest.mark.asyncio
async def test_proteger_tarea_desacopla_cancelaciones():
    finalizado = asyncio.Event()
    cancelaciones: list[str] = []

    async def trabajo():
        try:
            await asyncio.sleep(0.01)
            return "listo"
        except asyncio.CancelledError:
            cancelaciones.append("cancelada")
            raise
        finally:
            finalizado.set()

    original = asyncio.create_task(trabajo())
    protegido = stlib.proteger_tarea(original)

    protegido.cancel()
    await asyncio.sleep(0)

    assert not original.cancelled()

    resultado = await original
    await finalizado.wait()

    assert resultado == "listo"
    assert not cancelaciones


def _trabajo_bloqueante(marcas: list[str], demora: float) -> str:
    marcas.append("inicio")
    time.sleep(demora)
    marcas.append("fin")
    return "hecho"


@pytest.mark.asyncio
async def test_ejecutar_en_hilo_permite_proteger_resultados():
    marcas: list[str] = []
    tarea = asyncio.create_task(stlib.ejecutar_en_hilo(_trabajo_bloqueante, marcas, 0.02))
    envoltura = stlib.proteger_tarea(tarea)

    envoltura.cancel()
    await asyncio.sleep(0)

    assert not tarea.cancelled()

    resultado = await tarea

    assert resultado == "hecho"
    assert marcas == ["inicio", "fin"]


@pytest.mark.asyncio
async def test_ejecutar_en_hilo_sigue_trabajando_si_se_cancela():
    marcas: list[str] = []
    tarea = asyncio.create_task(stlib.ejecutar_en_hilo(_trabajo_bloqueante, marcas, 0.02))

    await asyncio.sleep(0)
    tarea.cancel()

    with pytest.raises(asyncio.CancelledError):
        await tarea

    for _ in range(20):
        if marcas == ["inicio", "fin"]:
            break
        await asyncio.sleep(0.01)

    assert marcas == ["inicio", "fin"]
