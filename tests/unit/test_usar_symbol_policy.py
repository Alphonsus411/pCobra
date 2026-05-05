import importlib
import math
from types import ModuleType

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


def test_rechaza_aliases_publicos_reservados():
    for nombre in ("append", "map", "filter", "unwrap", "expect", "self", "keys", "values", "len"):
        resultado = sanear_simbolo_para_usar(nombre, _callable_dummy)
        assert resultado.rechazado is True
        assert resultado.codigo == "explicit_forbidden_name"


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
