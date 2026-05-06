from __future__ import annotations

from importlib import import_module

import pytest

from pcobra.contrato_capacidades_corelibs import CAPACIDADES_POR_MODULO


@pytest.mark.parametrize("nombre_modulo", sorted(CAPACIDADES_POR_MODULO.keys()))
def test_all_coincide_con_api_canonica(nombre_modulo: str) -> None:
    contrato = CAPACIDADES_POR_MODULO[nombre_modulo]
    modulo = import_module(str(contrato["modulo"]))
    esperado = tuple(contrato["api_canonica"])
    assert tuple(modulo.__all__) == esperado


@pytest.mark.parametrize("nombre_modulo", sorted(CAPACIDADES_POR_MODULO.keys()))
def test_all_no_expone_internals(nombre_modulo: str) -> None:
    contrato = CAPACIDADES_POR_MODULO[nombre_modulo]
    modulo = import_module(str(contrato["modulo"]))
    assert all(not simbolo.startswith("_") for simbolo in modulo.__all__)
