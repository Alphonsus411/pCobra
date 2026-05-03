import math

from pcobra.core.usar_symbol_policy import sanear_simbolo_para_usar


def test_rechaza_nombres_prohibidos_backend():
    resultado = sanear_simbolo_para_usar("sys", lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_internal_name"


def test_rechaza_dunders():
    resultado = sanear_simbolo_para_usar("__algo__", lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo == "private_prefix"


def test_rechaza_objetos_modulo():
    resultado = sanear_simbolo_para_usar("modulo", math)
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_permite_constante_publica_explicita_como_warning():
    resultado = sanear_simbolo_para_usar("PI", 3.14)
    assert resultado.rechazado is False
    assert resultado.warning is True
    assert resultado.codigo == "public_constant"
