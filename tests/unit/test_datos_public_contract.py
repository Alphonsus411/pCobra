from types import ModuleType

import pytest

import pcobra.corelibs.datos as core_datos
from pcobra.core.usar_symbol_policy import sanear_simbolo_para_usar


def test_import_datos_corelib_expone_callables_directos():
    for simbolo in ("longitud", "filtrar", "mapear", "agregar"):
        assert callable(getattr(core_datos, simbolo))


def test_import_datos_corelib_longitud_resuelve_lista():
    assert core_datos.longitud([1, 2, 3]) == 3


def test_rechazo_continuo_backend_real_en_saneamiento():
    resultado = sanear_simbolo_para_usar("backend_real", ModuleType("os"))

    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"
