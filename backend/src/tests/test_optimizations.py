import pytest
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoValor,
    NodoFuncion,
    NodoRetorno,
    NodoCondicional,
    NodoLlamadaFuncion,
    NodoIdentificador,
    NodoBucleMientras,
    NodoRomper,
)
from src.cobra.lexico.lexer import Token, TipoToken
from src.core.optimizations import (
    optimize_constants,
    remove_dead_code,
    inline_functions,
)


def test_optimize_constants_binaria():
    ast = [
        NodoAsignacion(
            "x",
            NodoOperacionBinaria(NodoValor(2), Token(TipoToken.SUMA, "+"), NodoValor(3)),
        )
    ]
    optimizado = optimize_constants(ast)
    assert isinstance(optimizado[0].expresion, NodoValor)
    assert optimizado[0].expresion.valor == 5


def test_remove_dead_code_en_funcion():
    ast = [
        NodoFuncion(
            "f",
            [],
            [NodoRetorno(NodoValor(1)), NodoAsignacion("x", NodoValor(2))],
        )
    ]
    optimizado = remove_dead_code(ast)
    cuerpo = optimizado[0].cuerpo
    assert len(cuerpo) == 1
    assert isinstance(cuerpo[0], NodoRetorno)


def test_remove_condicional_constante():
    ast = [
        NodoCondicional(NodoValor(False), [NodoAsignacion("x", NodoValor(1))], [NodoAsignacion("x", NodoValor(2))])
    ]
    optimizado = remove_dead_code(ast)
    assert len(optimizado) == 1
    assert isinstance(optimizado[0], NodoAsignacion)
    assert optimizado[0].valor.valor == 2


def test_inline_functions_simple():
    ast = [
        NodoFuncion("uno", [], [NodoRetorno(NodoValor(1))]),
        NodoAsignacion("x", NodoLlamadaFuncion("uno", [])),
    ]
    optimizado = inline_functions(ast)
    assert len(optimizado) == 1
    asign = optimizado[0]
    assert isinstance(asign.expresion, NodoValor)
    assert asign.expresion.valor == 1


def test_remove_dead_code_condicional_completo():
    ast = [
        NodoFuncion(
            "f",
            [],
            [
                NodoCondicional(
                    NodoIdentificador("cond"),
                    [NodoRetorno(NodoValor(1))],
                    [NodoRetorno(NodoValor(2))],
                ),
                NodoAsignacion("x", NodoValor(3)),
            ],
        )
    ]
    optimizado = remove_dead_code(ast)
    cuerpo = optimizado[0].cuerpo
    assert len(cuerpo) == 1
    assert isinstance(cuerpo[0], NodoCondicional)


def test_remove_dead_code_en_bucle():
    ast = [
        NodoBucleMientras(
            NodoValor(True),
            [NodoRomper(), NodoAsignacion("x", NodoValor(1))],
        )
    ]
    optimizado = remove_dead_code(ast)
    assert optimizado == []


def test_remove_dead_code_bucle_true_break_final():
    ast = [
        NodoBucleMientras(
            NodoValor(True),
            [NodoAsignacion("x", NodoValor(1)), NodoRomper()],
        )
    ]
    optimizado = remove_dead_code(ast)
    assert len(optimizado) == 1
    assert isinstance(optimizado[0], NodoAsignacion)


def test_inline_functions_con_parametro():
    ast = [
        NodoFuncion("dup", ["a"], [NodoRetorno(NodoIdentificador("a"))]),
        NodoAsignacion("x", NodoLlamadaFuncion("dup", [NodoValor(3)])),
    ]
    optimizado = inline_functions(ast)
    assert len(optimizado) == 1
    asign = optimizado[0]
    assert isinstance(asign.expresion, NodoValor)
    assert asign.expresion.valor == 3
