from types import ModuleType

import pytest

import pcobra.corelibs.datos as core_datos
from pcobra.core.usar_symbol_policy import sanear_simbolo_para_usar


def test_import_datos_corelib_expone_callables_directos():
    for simbolo in ("longitud", "elemento", "filtrar", "mapear", "agregar"):
        assert callable(getattr(core_datos, simbolo))


def test_import_datos_corelib_longitud_resuelve_lista():
    assert core_datos.longitud([1, 2, 3]) == 3


def test_rechazo_continuo_backend_real_en_saneamiento():
    resultado = sanear_simbolo_para_usar("backend_real", ModuleType("os"))

    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_import_datos_corelib_elemento_resuelve_indice():
    assert core_datos.elemento([10, 20, 30], 1) == 20


def test_import_datos_corelib_elemento_valida_indice_entero():
    with pytest.raises(TypeError, match="^índice debe ser entero$"):
        core_datos.elemento([10, 20, 30], 1.5)


def test_import_datos_corelib_elemento_rechaza_no_indexable():
    with pytest.raises(TypeError, match="^objeto no indexable$"):
        core_datos.elemento({"a": 1}, 0)


def test_import_datos_corelib_elemento_fuera_de_rango():
    with pytest.raises(IndexError, match="^índice fuera de rango$"):
        core_datos.elemento([10], 2)
