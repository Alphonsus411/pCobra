import pytest
from io import StringIO
from unittest.mock import patch

from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Token, TipoToken
from src.core.parser import NodoAsignacion, NodoValor, NodoLlamadaFuncion


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
