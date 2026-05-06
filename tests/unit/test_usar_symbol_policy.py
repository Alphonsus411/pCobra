from types import ModuleType

from pcobra.core.usar_symbol_policy import sanear_simbolo_para_usar


def test_rechaza_nombres_prohibidos_explicitos():
    for nombre in ("self", "append", "map"):
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is True


def test_rechaza_doble_guion_bajo_y_modulo_backend():
    r_privado = sanear_simbolo_para_usar("__danger__", lambda: None)
    assert r_privado.rechazado is True

    r_modulo = sanear_simbolo_para_usar("sdk", ModuleType("sdk"))
    assert r_modulo.rechazado is True
