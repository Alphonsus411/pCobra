from __future__ import annotations

import pytest

from pcobra.corelibs import pruebas


def test_aserciones_exitosas_devuelven_true():
    assert pruebas.igual({"a": 1}, {"a": 1}) is True
    assert pruebas.verdadero([1]) is True
    assert pruebas.falso([]) is True
    assert pruebas.contiene("cobra", "ob") is True


def test_aserciones_fallidas_usan_mensajes_deterministas():
    with pytest.raises(AssertionError, match="Se esperaba 2, pero se obtuvo 1"):
        pruebas.igual(1, 2)

    with pytest.raises(AssertionError, match="Se esperaba un valor verdadero, pero se obtuvo 0"):
        pruebas.verdadero(0)

    with pytest.raises(AssertionError, match="Se esperaba un valor falso, pero se obtuvo 'texto'"):
        pruebas.falso("texto")

    with pytest.raises(AssertionError, match=r"Se esperaba que 4 estuviera en \[1, 2, 3\]"):
        pruebas.contiene([1, 2, 3], 4)


def test_mensaje_personalizado_sustituye_el_predeterminado():
    with pytest.raises(AssertionError, match="mensaje propio"):
        pruebas.igual("a", "b", "mensaje propio")


def test_contiene_reporta_contenedor_no_iterable_como_assertion_error():
    with pytest.raises(AssertionError, match="No se pudo comprobar pertenencia"):
        pruebas.contiene(10, 1)


def test_lanza_error_devuelve_error_capturado():
    def falla(valor: str) -> None:
        raise ValueError(f"valor inválido: {valor}")

    error = pruebas.lanza_error(falla, ValueError, "x")

    assert isinstance(error, ValueError)
    assert str(error) == "valor inválido: x"


def test_lanza_error_falla_si_no_hay_error_o_tipo_distinto():
    with pytest.raises(AssertionError, match="Se esperaba error ValueError, pero no se lanzó ninguno"):
        pruebas.lanza_error(lambda: None, ValueError)

    with pytest.raises(AssertionError, match="Se esperaba error ValueError, pero se lanzó TypeError"):
        pruebas.lanza_error(lambda: (_ for _ in ()).throw(TypeError("boom")), ValueError)


def test_lanza_error_valida_callable_y_tipo_error():
    with pytest.raises(TypeError, match="funcion debe ser callable"):
        pruebas.lanza_error("no callable")

    with pytest.raises(TypeError, match="tipo_error debe ser una clase de excepción"):
        pruebas.lanza_error(lambda: None, object)


def test_all_expone_solo_api_publica():
    assert pruebas.__all__ == ["igual", "verdadero", "falso", "contiene", "lanza_error"]
    for nombre in pruebas.__all__:
        assert hasattr(pruebas, nombre)
