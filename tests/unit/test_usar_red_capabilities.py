"""Regresiones de capacidades para la superficie pública ``red``."""

from __future__ import annotations

import inspect

import pytest

from pcobra.cobra.usar_capabilities import (
    CapacidadUsar,
    capacidades_de,
    simbolo_canonico,
)
from pcobra.cobra.usar_loader import usar_modulo
from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS
from pcobra.corelibs import red

CASOS_RED = (
    ("obtener_url", "obtener_url", CapacidadUsar.NETWORK_GET, False, ("url",)),
    ("enviar_post", "enviar_post", CapacidadUsar.NETWORK_POST, False, ("url", {})),
    ("obtener_url_async", "obtener_url", CapacidadUsar.NETWORK_GET, True, ("url",)),
    ("enviar_post_async", "enviar_post", CapacidadUsar.NETWORK_POST, True, ("url", {})),
    (
        "descargar_archivo",
        "descargar_archivo",
        CapacidadUsar.NETWORK_DOWNLOAD,
        True,
        ("url", "salida"),
    ),
    ("obtener_url_texto", "obtener_url", CapacidadUsar.NETWORK_GET, True, ("url",)),
    ("obtener_json", "obtener_url", CapacidadUsar.NETWORK_GET, False, ("url",)),
)


@pytest.mark.parametrize("nombre,canonico,capacidad,es_async,args", CASOS_RED)
def test_metadata_canonica_y_resolucion_de_aliases_red(
    nombre, canonico, capacidad, es_async, args
):
    contrato = CANONICAL_MODULE_SURFACE_CONTRACTS["red"]

    assert simbolo_canonico("red", nombre) == ("red", canonico)
    assert capacidad in capacidades_de("red", nombre)
    assert capacidad.value in contrato.symbol_capabilities[nombre]


@pytest.mark.asyncio
@pytest.mark.parametrize("nombre,canonico,capacidad,es_async,args", CASOS_RED)
async def test_modo_seguro_deniega_por_capacidad_toda_la_superficie_red(
    nombre, canonico, capacidad, es_async, args
):
    simbolo = usar_modulo("red", safe_mode=True)[nombre]

    with pytest.raises(PermissionError, match=capacidad.value):
        resultado = simbolo(*args)
        if es_async:
            await resultado


def test_descarga_declara_red_y_escritura():
    assert capacidades_de("red", "descargar_archivo") == frozenset(
        {CapacidadUsar.NETWORK_DOWNLOAD, CapacidadUsar.FILESYSTEM_WRITE}
    )


def test_metadata_visible_no_concede_autorizacion():
    exports = usar_modulo("red", safe_mode=True)
    exports["metadata"]["obtener_url"]["symbol"] = "inofensivo"
    red.obtener_url.capacidades = frozenset()  # type: ignore[attr-defined]
    try:
        with pytest.raises(PermissionError, match="network.get"):
            exports["obtener_url"]("url")
    finally:
        del red.obtener_url.capacidades  # type: ignore[attr-defined]


@pytest.mark.asyncio
@pytest.mark.parametrize("nombre,canonico,capacidad,es_async,args", CASOS_RED)
async def test_modo_no_seguro_conserva_resultados_y_forma_publica(
    monkeypatch, nombre, canonico, capacidad, es_async, args
):
    esperado = object()
    original = getattr(red, nombre)

    if es_async:

        async def doble(*_args, **_kwargs):
            return esperado

    else:

        def doble(*_args, **_kwargs):
            return esperado

    monkeypatch.setattr(red, nombre, doble)
    simbolo = usar_modulo("red", safe_mode=False)[nombre]
    resultado = simbolo(*args)
    if es_async:
        resultado = await resultado

    assert resultado is esperado
    assert inspect.iscoroutinefunction(simbolo) is inspect.iscoroutinefunction(original)
