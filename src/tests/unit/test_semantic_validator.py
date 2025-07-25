import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.semantic_validators import (
    construir_cadena,
    PrimitivaPeligrosaError,
)


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    return parser.parsear()


def test_primitiva_peligrosa_detectada():
    codigo = "leer_archivo('x.txt')"
    ast = generar_ast(codigo)
    validador = construir_cadena()

    with pytest.raises(PrimitivaPeligrosaError):
        for nodo in ast:
            nodo.aceptar(validador)


def test_codigo_seguro_no_lanza_error():
    codigo = "imprimir('hola')"
    ast = generar_ast(codigo)
    validador = construir_cadena()

    for nodo in ast:
        nodo.aceptar(validador)


def test_import_no_permitido():
    codigo = "import 'malicioso.co'"
    ast = generar_ast(codigo)
    validador = construir_cadena()

    with pytest.raises(PrimitivaPeligrosaError):
        for nodo in ast:
            nodo.aceptar(validador)
