import pytest
from io import StringIO
from unittest.mock import patch

from cobra.core import Token, TipoToken, Lexer
from cobra.core import Parser
from core.ast_nodes import (
    NodoAsignacion,
    NodoTryCatch,
    NodoThrow,
    NodoImprimir,
    NodoIdentificador,
    NodoValor,
)
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.interpreter import ExcepcionCobra, InterpretadorCobra


def generar_tokens(*args):
    return [Token(t, v) for t, v in args]


def test_parser_try_catch_throw():
    tokens = generar_tokens(
        (TipoToken.INTENTAR, "try"),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.LANZAR, "throw"),
        (TipoToken.CADENA, "error"),
        (TipoToken.CAPTURAR, "catch"),
        (TipoToken.IDENTIFICADOR, "e"),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.IMPRIMIR, "imprimir"),
        (TipoToken.LPAREN, "("),
        (TipoToken.IDENTIFICADOR, "e"),
        (TipoToken.RPAREN, ")"),
        (TipoToken.FIN, "fin"),
        (TipoToken.EOF, None),
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoTryCatch)
    assert isinstance(nodo.bloque_try[0], NodoThrow)
    assert isinstance(nodo.bloque_catch[0], NodoImprimir)


def test_interpreter_try_catch():
    nodo = NodoTryCatch(
        [NodoThrow(NodoIdentificador("mensaje"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    interp = InterpretadorCobra()
    interp.variables["mensaje"] = "hola"
    interp.ejecutar_nodo(nodo)
    assert interp.variables["e"] == "hola"


def test_interpreter_try_finally_sin_excepcion_ejecuta_ambos_bloques():
    nodo = NodoTryCatch(
        [NodoAsignacion("try_ejecutado", NodoValor(True), declaracion=True)],
        bloque_finally=[
            NodoAsignacion("finally_ejecutado", NodoValor(True), declaracion=True)
        ],
    )
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(nodo)

    assert interp.variables["try_ejecutado"] is True
    assert interp.variables["finally_ejecutado"] is True


def test_interpreter_try_finally_repropaga_excepcion_despues_de_finally():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("fallo"))],
        bloque_finally=[
            NodoAsignacion("finally_ejecutado", NodoValor(True), declaracion=True)
        ],
    )
    interp = InterpretadorCobra()

    with pytest.raises(ExcepcionCobra) as exc_info:
        interp.ejecutar_nodo(nodo)

    assert exc_info.value.valor == "fallo"
    assert interp.variables["finally_ejecutado"] is True


def test_interpreter_try_catch_conserva_excepcion_manejada():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("fallo"))],
        "e",
        [NodoAsignacion("catch_ejecutado", NodoValor(True), declaracion=True)],
    )
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(nodo)

    assert interp.variables["e"] == "fallo"
    assert interp.variables["catch_ejecutado"] is True


def test_interpreter_try_catch_finally_maneja_y_ejecuta_finally():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("fallo"))],
        "e",
        [NodoAsignacion("catch_ejecutado", NodoValor(True), declaracion=True)],
        [NodoAsignacion("finally_ejecutado", NodoValor(True), declaracion=True)],
    )
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(nodo)

    assert interp.variables["e"] == "fallo"
    assert interp.variables["catch_ejecutado"] is True
    assert interp.variables["finally_ejecutado"] is True


def test_interpreter_try_catch_finally_sin_excepcion_omite_catch():
    nodo = NodoTryCatch(
        [NodoAsignacion("try_ejecutado", NodoValor(True), declaracion=True)],
        "e",
        [NodoAsignacion("catch_ejecutado", NodoValor(True), declaracion=True)],
        [NodoAsignacion("finally_ejecutado", NodoValor(True), declaracion=True)],
    )
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(nodo)

    assert interp.variables["try_ejecutado"] is True
    assert "catch_ejecutado" not in interp.variables
    assert interp.variables["finally_ejecutado"] is True


def test_transpiler_python_try_catch():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    tr = TranspiladorPython()
    codigo = tr.generate_code([nodo])
    esperado = "try:\n    raise Exception(1)\nexcept Exception as e:\n    print(e)\n"
    assert codigo == esperado


def test_transpiler_js_try_catch():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    tr = TranspiladorJavaScript()
    codigo = tr.generate_code([nodo])
    esperado = "try {\nthrow 1;\n}\ncatch (e) {\nconsole.log(e);\n}"
    assert codigo == esperado


def test_parser_intentar_lanzar_capturar():
    codigo = """
    intentar:
        lanzar 'err'
    capturar e:
        imprimir(e)
    fin
    """
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    nodo = ast[0]
    assert isinstance(nodo, NodoTryCatch)
    assert isinstance(nodo.bloque_try[0], NodoThrow)
    assert isinstance(nodo.bloque_catch[0], NodoImprimir)


def test_interpreter_intentar_lanzar_capturar():
    codigo = """
    intentar:
        lanzar mensaje
    capturar e:
        imprimir(e)
    fin
    """
    interp = InterpretadorCobra()
    interp.variables["mensaje"] = "hola"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()[0]

    from core.ast_nodes import (
        NodoTryCatch as STry,
        NodoThrow as SThrow,
        NodoImprimir as SImprimir,
        NodoIdentificador as SId,
        NodoValor as SVal,
    )

    nodo = STry(
        [SThrow(SId("mensaje"))],
        "e",
        [SImprimir(SId("e"))],
    )
    interp.ejecutar_nodo(nodo)
    assert interp.variables["e"] == "hola"
