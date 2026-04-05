import pytest
from core.ast_nodes import (
    NodoAST,
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
from cobra.core import Token, TipoToken
from core.optimizations import (
    optimize_constants,
    remove_dead_code,
    inline_functions,
    eliminate_common_subexpressions,
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


def test_remove_condicional_constante_true_colapsa_a_bloque_then():
    ast = [
        NodoCondicional(NodoValor(True), [NodoAsignacion("x", NodoValor(1))], [NodoAsignacion("x", NodoValor(2))])
    ]
    optimizado = remove_dead_code(ast)
    assert len(optimizado) == 1
    assert isinstance(optimizado[0], NodoAsignacion)
    assert optimizado[0].valor.valor == 1


@pytest.mark.parametrize("valor_no_booleano", [5, "hola"])
def test_remove_condicional_literal_no_booleano_no_colapsa(valor_no_booleano):
    ast = [
        NodoCondicional(
            NodoValor(valor_no_booleano),
            [NodoAsignacion("x", NodoValor(1))],
            [NodoAsignacion("x", NodoValor(2))],
        )
    ]
    optimizado = remove_dead_code(ast)
    assert len(optimizado) == 1
    assert isinstance(optimizado[0], NodoCondicional)


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


def test_inline_functions_no_side_effects():
    ast = [
        NodoFuncion(
            "impure",
            [],
            [NodoAsignacion("x", NodoValor(1)), NodoRetorno(NodoValor(1))],
        ),
        NodoFuncion("f", [], [NodoRetorno(NodoLlamadaFuncion("impure", []))]),
        NodoAsignacion("y", NodoLlamadaFuncion("f", [])),
    ]
    optimizado = inline_functions(ast)
    assert len(optimizado) == 3
    assert isinstance(optimizado[0], NodoFuncion)
    assert isinstance(optimizado[1], NodoFuncion)


def test_inline_functions_nested_pure():
    ast = [
        NodoFuncion("inner", [], [NodoRetorno(NodoValor(5))]),
        NodoFuncion("outer", [], [NodoRetorno(NodoLlamadaFuncion("inner", []))]),
        NodoAsignacion("x", NodoLlamadaFuncion("outer", [])),
    ]
    optimizado = inline_functions(ast)
    assert len(optimizado) == 1
    asign = optimizado[0]
    assert isinstance(asign.expresion, NodoValor)
    assert asign.expresion.valor == 5


def test_inline_functions_remove_definition():
    ast = [
        NodoFuncion("uno", [], [NodoRetorno(NodoValor(1))]),
        NodoAsignacion("a", NodoLlamadaFuncion("uno", [])),
        NodoAsignacion("b", NodoLlamadaFuncion("uno", [])),
    ]
    optimizado = inline_functions(ast)
    assert len(optimizado) == 2
    assert all(not isinstance(n, NodoFuncion) for n in optimizado)


def test_eliminate_common_subexpressions_global():
    suma = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("b"),
    )
    ast = [
        NodoAsignacion("x", suma),
        NodoAsignacion("y", NodoOperacionBinaria(NodoIdentificador("a"), Token(TipoToken.SUMA, "+"), NodoIdentificador("b"))),
    ]
    optimizado = eliminate_common_subexpressions(ast)
    assert len(optimizado) == 3
    temp = optimizado[0]
    assert temp.identificador == "_cse0"
    assert isinstance(optimizado[1].expresion, NodoIdentificador)
    assert optimizado[1].expresion.nombre == "_cse0"
    assert isinstance(optimizado[2].expresion, NodoIdentificador)
    assert optimizado[2].expresion.nombre == "_cse0"


def test_eliminate_common_subexpressions_in_function():
    suma = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("b"),
    )
    func = NodoFuncion(
        "f",
        [],
        [
            NodoAsignacion("x", suma),
            NodoAsignacion("y", NodoOperacionBinaria(NodoIdentificador("a"), Token(TipoToken.SUMA, "+"), NodoIdentificador("b"))),
            NodoRetorno(NodoValor(0)),
        ],
    )
    optimizado = eliminate_common_subexpressions([func])
    cuerpo = optimizado[0].cuerpo
    assert cuerpo[0].identificador == "_cse0"
    assert isinstance(cuerpo[1].expresion, NodoIdentificador)
    assert cuerpo[1].expresion.nombre == "_cse0"
    assert isinstance(cuerpo[2].expresion, NodoIdentificador)
    assert cuerpo[2].expresion.nombre == "_cse0"


def _assert_ast_sin_ciclos(nodos):
    activos = set()
    visitados = set()

    def _visitar(valor, ruta="raiz"):
        if isinstance(valor, list):
            for idx, item in enumerate(valor):
                _visitar(item, f"{ruta}[{idx}]")
            return

        if not isinstance(valor, NodoAST):
            return

        nid = id(valor)
        if nid in activos:
            pytest.fail(f"Se detectó ciclo AST en {ruta}")
        if nid in visitados:
            return

        activos.add(nid)
        try:
            for attr, child in vars(valor).items():
                _visitar(child, f"{ruta}.{attr}")
        finally:
            activos.remove(nid)
            visitados.add(nid)

    _visitar(nodos)


def test_inline_no_comparte_subarbol_entre_ramas_y_ast_sin_ciclos():
    token_suma = Token(TipoToken.SUMA, "+")
    argumento_compartido = NodoOperacionBinaria(
        NodoValor(1),
        token_suma,
        NodoValor(2),
    )

    ast = [
        NodoFuncion(
            "dup",
            ["a"],
            [
                NodoRetorno(
                    NodoOperacionBinaria(
                        NodoIdentificador("a"),
                        token_suma,
                        NodoIdentificador("a"),
                    )
                )
            ],
        ),
        NodoAsignacion("x", NodoLlamadaFuncion("dup", [argumento_compartido])),
    ]

    optimizado = inline_functions(ast)
    asignacion = optimizado[0]
    assert isinstance(asignacion.expresion, NodoOperacionBinaria)
    assert asignacion.expresion.izquierda is not asignacion.expresion.derecha

    _assert_ast_sin_ciclos(optimizado)


def test_cse_no_reutiliza_instancia_mutable_y_ast_sin_ciclos():
    token_suma = Token(TipoToken.SUMA, "+")
    compartida = NodoOperacionBinaria(
        NodoIdentificador("a"),
        token_suma,
        NodoIdentificador("b"),
    )
    ast = [
        NodoAsignacion("x", compartida),
        NodoAsignacion("y", compartida),
    ]

    optimizado = eliminate_common_subexpressions(ast)

    assert len(optimizado) == 3
    temporal = optimizado[0]
    assert isinstance(temporal.expresion, NodoOperacionBinaria)
    assert temporal.expresion is not compartida

    _assert_ast_sin_ciclos(optimizado)
