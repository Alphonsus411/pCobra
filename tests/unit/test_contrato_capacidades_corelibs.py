from __future__ import annotations

import importlib

import pytest

from pcobra.contrato_capacidades_corelibs import CAPACIDADES_POR_MODULO


MODULOS_CANONICOS = (
    "numero",
    "texto",
    "datos",
    "logica",
    "asincrono",
    "sistema",
    "archivo",
    "tiempo",
    "red",
    "holobit",
)


@pytest.mark.parametrize("modulo", MODULOS_CANONICOS)
def test_contrato_api_canonica_coincide_con_exportes(modulo: str) -> None:
    contrato = CAPACIDADES_POR_MODULO[modulo]
    modulo_stdlib = importlib.import_module(str(contrato["modulo"]))

    api_canonica = tuple(contrato["api_canonica"])
    exportes = tuple(getattr(modulo_stdlib, "__all__", ()))

    assert exportes == api_canonica


@pytest.mark.parametrize("modulo", MODULOS_CANONICOS)
def test_api_canonica_es_callable_y_solo_espanol(modulo: str) -> None:
    contrato = CAPACIDADES_POR_MODULO[modulo]
    modulo_stdlib = importlib.import_module(str(contrato["modulo"]))

    for nombre in contrato["api_canonica"]:
        assert hasattr(modulo_stdlib, nombre), f"{modulo} no implementa {nombre}"
        assert callable(getattr(modulo_stdlib, nombre)), f"{modulo}.{nombre} no es callable"
        assert nombre == nombre.lower()
        assert all(letra.isalpha() or letra == "_" for letra in nombre)


@pytest.mark.parametrize("modulo", MODULOS_CANONICOS)
def test_contrato_no_declara_aliases_ingles_en_api_canonica(modulo: str) -> None:
    contrato = CAPACIDADES_POR_MODULO[modulo]
    equivalencias = contrato.get("equivalencia_python", {})

    assert isinstance(equivalencias, dict)
    assert all(destino in contrato["api_canonica"] for destino in equivalencias.values())
