import pytest
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.semantic_validator import ValidadorSemantico, PrimitivaPeligrosaError


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    return parser.parsear()


def test_primitiva_peligrosa_detectada():
    codigo = "leer_archivo('x.txt')"
    ast = generar_ast(codigo)
    validador = ValidadorSemantico()

    with pytest.raises(PrimitivaPeligrosaError):
        for nodo in ast:
            nodo.aceptar(validador)


def test_codigo_seguro_no_lanza_error():
    codigo = "imprimir('hola')"
    ast = generar_ast(codigo)
    validador = ValidadorSemantico()

    # No debe lanzar excepciones
    for nodo in ast:
        nodo.aceptar(validador)
