from src.cobra.lexico.lexer import Token, TipoToken
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
)
from src.cobra.transpilers.transpiler.to_matlab import TranspiladorMatlab
from src.cobra.transpilers.transpiler.to_rust import TranspiladorRust


def test_operacion_binaria_matlab():
    expr = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("b"),
    )
    codigo = TranspiladorMatlab().generate_code([NodoAsignacion("x", expr)])
    assert codigo == "x = a + b;"


def test_operacion_unaria_rust():
    expr = NodoOperacionUnaria(Token(TipoToken.NOT, "!"), NodoIdentificador("cond"))
    codigo = TranspiladorRust().generate_code([NodoAsignacion("y", expr)])
    assert codigo == "let y = !cond;"
