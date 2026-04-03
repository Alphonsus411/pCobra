import pytest

from cobra.core import Lexer, Parser
from cobra.semantico import AnalizadorSemantico
from core.ast_nodes import (
    NodoIdentificador,
    NodoAsignacion,
    NodoValor,
    NodoFuncion,
    NodoClase,
)


def test_variable_no_declarada():
    ast = [NodoIdentificador("x")]
    analizador = AnalizadorSemantico()
    with pytest.raises(NameError):
        analizador.analizar(ast)


def test_condicional_variable_no_declarada_lanza_nameerror_exacto():
    codigo = """
si x == 10:
    pasar
fin
"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    analizador = AnalizadorSemantico()

    with pytest.raises(NameError) as exc_info:
        analizador.analizar(ast)

    assert str(exc_info.value) == "Variable no declarada: x"


def test_condicional_variable_no_declarada_con_dos_puntos_espaciado():
    codigo = """
si x == 10 :
    pasar
fin
"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    analizador = AnalizadorSemantico()

    with pytest.raises(NameError, match=r"^Variable no declarada: x$"):
        analizador.analizar(ast)


def test_conflicto_duplicado_funcion():
    ast = [
        NodoFuncion("f", [], []),
        NodoFuncion("f", [], []),
    ]
    analizador = AnalizadorSemantico()
    with pytest.raises(ValueError):
        analizador.analizar(ast)


def test_clase_base_no_declarada():
    ast = [NodoClase("Derivada", [], bases=["Base"])]
    analizador = AnalizadorSemantico()
    with pytest.raises(ValueError, match="Clase base no encontrada: Base"):
        analizador.analizar(ast)


def test_herencia_circular():
    ast = [NodoClase("A", [], bases=["A"])]
    analizador = AnalizadorSemantico()
    with pytest.raises(ValueError, match="Herencia circular"):
        analizador.analizar(ast)
