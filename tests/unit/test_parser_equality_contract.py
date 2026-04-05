"""Contrato de regresión para igualdad `==` en el parser clásico.

Este test cubre explícitamente:
- `ClassicParser.exp_equality`
- `ClassicParser.exp_comparison`
- `ClassicParser.declaracion_imprimir`
- `ClassicParser.declaracion_condicional`
"""

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoValor,
)
from pcobra.core.lexer import Lexer, TipoToken
from pcobra.cobra.core.parser import ClassicParser


def _parsear(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    ast = ClassicParser(tokens).parsear()
    return tokens, ast


def _assert_igualdad_cadenas(expresion, izquierda: str, derecha: str):
    """Valida el contrato AST de igualdad entre dos literales cadena."""
    assert isinstance(expresion, NodoOperacionBinaria)
    assert expresion.operador.tipo == TipoToken.IGUAL
    assert isinstance(expresion.izquierda, NodoValor)
    assert expresion.izquierda.valor == izquierda
    assert isinstance(expresion.derecha, NodoValor)
    assert expresion.derecha.valor == derecha


def _assert_igualdad_x_10(expresion):
    """Valida el contrato AST de `x == 10` generado por exp_equality/exp_comparison."""
    assert isinstance(expresion, NodoOperacionBinaria)
    assert isinstance(expresion.izquierda, NodoIdentificador)
    assert expresion.izquierda.nombre == "x"
    assert expresion.operador.tipo == TipoToken.IGUAL
    assert isinstance(expresion.derecha, NodoValor)
    assert expresion.derecha.valor == 10


def test_igualdad_en_imprimir_y_si_comparten_estructura_ast():
    # Contexto 1: declaracion_imprimir -> expresion -> exp_equality/exp_comparison
    tokens_imprimir, ast_imprimir = _parsear("imprimir(x == 10)")
    assert any(t.tipo == TipoToken.IGUAL for t in tokens_imprimir)

    nodo_imprimir = ast_imprimir[0]
    assert isinstance(nodo_imprimir, NodoImprimir)
    _assert_igualdad_x_10(nodo_imprimir.expresion)

    # Contexto 2: declaracion_condicional -> condicion -> expresion -> exp_equality/exp_comparison
    _, ast_si = _parsear("si x == 10:\n    imprimir(x)\nfin")
    nodo_si = ast_si[0]
    assert isinstance(nodo_si, NodoCondicional)
    _assert_igualdad_x_10(nodo_si.condicion)


def test_imprimir_con_agrupacion_permita_encadenar_binarias():
    _, ast = _parsear("imprimir (x + 5) + 3 + 4")
    nodo_imprimir = ast[0]
    assert isinstance(nodo_imprimir, NodoImprimir)
    assert isinstance(nodo_imprimir.expresion, NodoOperacionBinaria)
    assert nodo_imprimir.expresion.operador.tipo == TipoToken.SUMA


def test_expresion_igualdad_cadenas_parsea_sin_excepcion_y_con_ast_esperado():
    codigo = '"hola" == "hola"'
    try:
        tokens, ast = _parsear(codigo)
    except Exception as exc:  # pragma: no cover - ruta de regresión explícita
        raise AssertionError(
            f"No debía fallar el parseo de igualdad de cadenas: {codigo}"
        ) from exc

    assert any(t.tipo == TipoToken.IGUAL for t in tokens)
    assert len(ast) == 1
    _assert_igualdad_cadenas(ast[0], "hola", "hola")


def test_expresion_desigualdad_cadenas_parsea_sin_excepcion_y_con_ast_esperado():
    codigo = '"hola" == "adios"'
    try:
        tokens, ast = _parsear(codigo)
    except Exception as exc:  # pragma: no cover - ruta de regresión explícita
        raise AssertionError(
            f"No debía fallar el parseo de igualdad de cadenas: {codigo}"
        ) from exc

    assert any(t.tipo == TipoToken.IGUAL for t in tokens)
    assert len(ast) == 1
    _assert_igualdad_cadenas(ast[0], "hola", "adios")


def test_ruta_previa_identificador_sigue_entregando_ast_igualdad_esperado():
    """Garantiza que `IDENTIFICADOR` como inicio mantiene la semántica previa."""
    tokens, ast = _parsear("x == 10")
    assert tokens[0].tipo == TipoToken.IDENTIFICADOR
    assert len(ast) == 1
    _assert_igualdad_x_10(ast[0])


def test_ruta_previa_identificadores_en_igualdad_siguen_parseando_igual():
    """No regresión: `x == y` debe seguir produciendo una binaria con dos identificadores."""
    tokens, ast = _parsear("x == y")
    assert tokens[0].tipo == TipoToken.IDENTIFICADOR
    assert len(ast) == 1
    assert isinstance(ast[0], NodoOperacionBinaria)
    assert ast[0].operador.tipo == TipoToken.IGUAL
    assert isinstance(ast[0].izquierda, NodoIdentificador)
    assert ast[0].izquierda.nombre == "x"
    assert isinstance(ast[0].derecha, NodoIdentificador)
    assert ast[0].derecha.nombre == "y"


def test_ruta_previa_entero_y_flotante_siguen_entregando_ast_binario_esperado():
    """Garantiza que `ENTERO` y `FLOTANTE` como inicio siguen parseando como expresión."""
    tokens_entero, ast_entero = _parsear("10 == 10")
    assert tokens_entero[0].tipo == TipoToken.ENTERO
    assert len(ast_entero) == 1
    assert isinstance(ast_entero[0], NodoOperacionBinaria)
    assert ast_entero[0].operador.tipo == TipoToken.IGUAL
    assert isinstance(ast_entero[0].izquierda, NodoValor)
    assert ast_entero[0].izquierda.valor == 10
    assert isinstance(ast_entero[0].derecha, NodoValor)
    assert ast_entero[0].derecha.valor == 10

    tokens_flotante, ast_flotante = _parsear("1.5 == 1.5")
    assert tokens_flotante[0].tipo == TipoToken.FLOTANTE
    assert len(ast_flotante) == 1
    assert isinstance(ast_flotante[0], NodoOperacionBinaria)
    assert ast_flotante[0].operador.tipo == TipoToken.IGUAL
    assert isinstance(ast_flotante[0].izquierda, NodoValor)
    assert ast_flotante[0].izquierda.valor == 1.5
    assert isinstance(ast_flotante[0].derecha, NodoValor)
    assert ast_flotante[0].derecha.valor == 1.5


def test_ruta_previa_identificador_llamada_funcion_sigue_intacta():
    """Confirma que `foo(1)` se sigue resolviendo como llamada de función."""
    tokens, ast = _parsear("foo(1)")
    assert tokens[0].tipo == TipoToken.IDENTIFICADOR
    assert len(ast) == 1
    assert isinstance(ast[0], NodoLlamadaFuncion)
    assert ast[0].nombre == "foo"
    assert len(ast[0].argumentos) == 1
    assert isinstance(ast[0].argumentos[0], NodoValor)
    assert ast[0].argumentos[0].valor == 1


def test_ruta_previa_identificador_asignacion_sigue_intacta():
    """Confirma que `x = 1` conserva la ruta de asignación previa."""
    tokens, ast = _parsear("x = 1")
    assert tokens[0].tipo == TipoToken.IDENTIFICADOR
    assert len(ast) == 1
    assert isinstance(ast[0], NodoAsignacion)
    assert ast[0].identificador == "x"
    assert isinstance(ast[0].expresion, NodoValor)
    assert ast[0].expresion.valor == 1


def test_suma_cadenas_parsea_como_binaria_y_deja_semantica_al_evaluador():
    """Opcional útil: validar parseo/AST de suma de cadenas sin imponer semántica aquí."""
    tokens, ast = _parsear('"a" + "b"')
    assert any(t.tipo == TipoToken.SUMA for t in tokens)
    assert len(ast) == 1
    assert isinstance(ast[0], NodoOperacionBinaria)
    assert ast[0].operador.tipo == TipoToken.SUMA
    assert isinstance(ast[0].izquierda, NodoValor)
    assert ast[0].izquierda.valor == "a"
    assert isinstance(ast[0].derecha, NodoValor)
    assert ast[0].derecha.valor == "b"
