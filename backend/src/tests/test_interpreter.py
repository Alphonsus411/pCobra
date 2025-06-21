import pytest
from io import StringIO
from unittest.mock import patch

from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Token, TipoToken
from src.core.parser import (
    NodoAsignacion,
    NodoValor,
    NodoLlamadaFuncion,
    NodoFuncion,
)


def test_interpretador_asignacion_y_llamada_funcion():
    # Crea una instancia del intérprete
    interpretador = InterpretadorCobra()

    # Prueba de asignación
    nodo_asignacion = NodoAsignacion("x", NodoValor(45))
    interpretador.ejecutar_nodo(nodo_asignacion)

    # Verifica que la variable x se haya almacenado correctamente
    assert interpretador.variables["x"] == 45

    # Prueba de llamada a la función imprimir
    nodo_llamada = NodoLlamadaFuncion("imprimir", [NodoValor("Hola, Cobra!")])

    # Usamos un patch para capturar la salida de imprimir
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        interpretador.ejecutar_llamada_funcion(nodo_llamada)

    # Captura la salida
    output = mock_stdout.getvalue().strip()

    # Verifica que la salida sea la esperada
    assert output == "Hola, Cobra!"


def test_interpretador_variable_no_definida():
    interpretador = InterpretadorCobra()

    # Intenta imprimir una variable no definida
    nodo_llamada = NodoLlamadaFuncion("imprimir", [Token(TipoToken.IDENTIFICADOR, "y")])

    # Usamos un patch para capturar la salida de imprimir
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        interpretador.ejecutar_llamada_funcion(nodo_llamada)

    output = mock_stdout.getvalue().strip()

    # Verifica que la salida sea la esperada para variable no definida
    assert output == "Variable 'y' no definida"


def test_aislamiento_de_contexto_en_funciones():
    """Verifica que las variables locales no contaminen el contexto global."""
    inter = InterpretadorCobra()

    funcion = NodoFuncion(
        "crear_local",
        [],
        [NodoAsignacion("z", NodoValor(100))],
    )

    inter.ejecutar_funcion(funcion)
    inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("crear_local", []))

    assert "z" not in inter.variables


def test_preservacion_de_variables_globales():
    """Verifica que las variables globales no se modifiquen dentro de una función."""
    inter = InterpretadorCobra()

    inter.ejecutar_asignacion(NodoAsignacion("a", NodoValor(5)))

    funcion = NodoFuncion(
        "modificar",
        [],
        [NodoAsignacion("a", NodoValor(1))],
    )

    inter.ejecutar_funcion(funcion)
    inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("modificar", []))

    assert inter.variables["a"] == 5
