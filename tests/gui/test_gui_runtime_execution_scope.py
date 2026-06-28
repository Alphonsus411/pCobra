import pytest

from pcobra.gui import runtime


def test_ejecutar_codigo_permite_asignacion_numerica_en_mismo_fragmento():
    salida = runtime.ejecutar_codigo("x = 123\nimprimir(x)")

    assert "123" in salida


def test_ejecutar_codigo_permite_asignacion_texto_en_mismo_fragmento():
    salida = runtime.ejecutar_codigo('x = "hola"\nimprimir(x)')

    assert "hola" in salida


def test_ejecutar_codigo_permite_asignacion_lista_en_mismo_fragmento():
    salida = runtime.ejecutar_codigo("numeros = [1, 2, 3, 4]\nimprimir(numeros)")

    assert "[1, 2, 3, 4]" in salida


def test_ejecutar_codigo_variable_inexistente_sigue_fallando():
    with pytest.raises(NameError, match="Variable no declarada"):
        runtime.ejecutar_codigo("imprimir(no_existe)")
