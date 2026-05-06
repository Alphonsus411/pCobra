import importlib
import math
from types import ModuleType

import pytest

from pcobra.core.ast_nodes import NodoUsar
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.usar_symbol_policy import sanear_simbolo_para_usar


def _callable_dummy():
    return None


def test_rechaza_nombres_prohibidos_backend():
    for nombre in ("sys", "os", "importlib", "pcobra", "cobra", "core"):
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is True
        assert resultado.codigo == "backend_internal_name"


def test_rechaza_privado():
    resultado = sanear_simbolo_para_usar("_privado", _callable_dummy)
    assert resultado.rechazado is True
    assert resultado.codigo == "private_prefix"


def test_rechaza_dunders():
    resultado = sanear_simbolo_para_usar("__algo__", lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo in {"dunder_pattern", "private_prefix"}


def test_rechaza_dunders_python_conocidos():
    resultado = sanear_simbolo_para_usar("__name__", lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo == "private_prefix"


def test_rechaza_aliases_publicos_reservados_con_nombre_recomendado():
    esperados = {
        "append": "agregar",
        "map": "mapear",
        "filter": "filtrar",
        "unwrap": "obtener_o_error",
        "expect": "obtener_o_error",
        "self": "instancia",
        "keys": "claves",
        "values": "valores",
        "len": "longitud",
    }
    for nombre, recomendado in esperados.items():
        resultado = sanear_simbolo_para_usar(nombre, _callable_dummy)
        assert resultado.rechazado is True
        assert resultado.codigo == "explicit_forbidden_name"
        assert recomendado in (resultado.mensaje or "")


def test_rechaza_objetos_modulo():
    resultado = sanear_simbolo_para_usar("modulo", math)
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_rechaza_tipo_modulo_backend():
    resultado = sanear_simbolo_para_usar("TipoModulo", ModuleType)
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_rechaza_wrapper_indirecto_de_backend():
    class WrapperSDK:
        __wrapped__ = math

    resultado = sanear_simbolo_para_usar("wrapper", WrapperSDK())
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_rechaza_objeto_importado_indirectamente_desde_backend():
    resultado = sanear_simbolo_para_usar("machinery", importlib.machinery)
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_permite_constante_publica_explicita_como_warning():
    resultado = sanear_simbolo_para_usar("PI", 3.14)
    assert resultado.rechazado is False
    assert resultado.warning is True
    assert resultado.codigo == "public_constant"


def test_rechaza_constante_no_mayuscula():
    resultado = sanear_simbolo_para_usar("pi", 3.14)
    assert resultado.rechazado is True
    assert resultado.codigo == "non_callable_not_canonical_public_constant"


def test_rechaza_constante_mayuscula_no_canonica():
    resultado = sanear_simbolo_para_usar("MAX_SIZE", 128)
    assert resultado.rechazado is True
    assert resultado.codigo == "non_callable_not_canonical_public_constant"


def test_usar_modulo_mixto_importa_solo_simbolos_validos(monkeypatch):
    modulo = ModuleType("fake_numero")
    modulo.__all__ = ["es_finito", "_interno", "MAX_SIZE", "PI"]
    modulo.es_finito = _callable_dummy
    modulo._interno = _callable_dummy
    modulo.MAX_SIZE = 128
    modulo.PI = 3.14
    modulo.__file__ = __file__

    monkeypatch.setattr(
        "pcobra.core.usar_loader.obtener_modulo_cobra_oficial",
        lambda _canonico: modulo,
    )

    interp = InterpretadorCobra(safe_mode=False)
    interp.ejecutar_usar(NodoUsar("numero"))

    assert interp.variables["es_finito"] is _callable_dummy
    assert interp.variables["PI"] == 3.14
    assert "_interno" not in interp.variables
    assert "MAX_SIZE" not in interp.variables


def test_usar_modulo_totalmente_invalido_falla(monkeypatch):
    modulo = ModuleType("fake_numero_invalido")
    modulo.__all__ = ["_interno", "MAX_SIZE"]
    modulo._interno = _callable_dummy
    modulo.MAX_SIZE = 128
    modulo.__file__ = __file__

    monkeypatch.setattr(
        "pcobra.core.usar_loader.obtener_modulo_cobra_oficial",
        lambda _canonico: modulo,
    )

    interp = InterpretadorCobra(safe_mode=False)
    with pytest.raises(ImportError, match="no quedaron símbolos exportables"):
        interp.ejecutar_usar(NodoUsar("numero"))


def test_rechaza_nombres_con_dunder_en_cualquier_posicion():
    for nombre in ("mi__simbolo", "__x", "x__", "normal__otro"):
        resultado = sanear_simbolo_para_usar(nombre, _callable_dummy)
        assert resultado.rechazado is True
        assert resultado.codigo in {"dunder_pattern", "private_prefix"}
