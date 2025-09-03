import pytest

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
