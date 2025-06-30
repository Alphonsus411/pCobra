import pytest

from src.cobra.semantico import AnalizadorSemantico
from src.core.ast_nodes import (
    NodoIdentificador,
    NodoAsignacion,
    NodoValor,
    NodoFuncion,
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
