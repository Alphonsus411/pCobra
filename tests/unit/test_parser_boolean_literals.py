from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from pcobra.core.ast_nodes import NodoCondicional, NodoOperacionBinaria, NodoValor
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.lexer import Lexer, TipoToken
from pcobra.cobra.core.parser import ClassicParser, ParserError


def _parsear_sin_error_booleano_en_termino(codigo: str):
    try:
        tokens = Lexer(codigo).analizar_token()
        ast = ClassicParser(tokens).parsear()
    except ParserError as exc:  # pragma: no cover - contrato anti-regresión explícito
        mensaje = str(exc)
        assert "Token inesperado en término: TipoToken.BOOLEANO" not in mensaje
        raise
    return tokens, ast


def _lineas_utiles(salida: str) -> list[str]:
    return [
        linea.strip()
        for linea in salida.splitlines()
        if linea.strip() and not linea.lstrip().startswith("[")
    ]


def test_si_verdadero_condicion_booleana_ast_valido_y_retorna_ok() -> None:
    _, ast = _parsear_sin_error_booleano_en_termino('si verdadero: "ok" fin')

    assert len(ast) == 1
    nodo_si = ast[0]
    assert isinstance(nodo_si, NodoCondicional)
    assert isinstance(nodo_si.condicion, NodoValor)
    assert nodo_si.condicion.valor is True

    inter = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO) as out:
        resultado = inter.ejecutar_nodo(nodo_si)

    assert resultado == "ok"
    assert _lineas_utiles(out.getvalue()) == []


def test_si_falso_condicion_booleana_ast_valido_y_sin_salida() -> None:
    _, ast = _parsear_sin_error_booleano_en_termino('si falso: "no" fin')

    assert len(ast) == 1
    nodo_si = ast[0]
    assert isinstance(nodo_si, NodoCondicional)
    assert isinstance(nodo_si.condicion, NodoValor)
    assert nodo_si.condicion.valor is False

    inter = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO) as out:
        resultado = inter.ejecutar_nodo(nodo_si)

    assert resultado is None
    assert _lineas_utiles(out.getvalue()) == []


def test_verdadero_igual_verdadero_parsea_como_binaria_con_nodovalor_booleanos() -> None:
    tokens, ast = _parsear_sin_error_booleano_en_termino("verdadero == verdadero")

    assert any(t.tipo == TipoToken.IGUAL for t in tokens)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoOperacionBinaria)
    assert nodo.operador.tipo == TipoToken.IGUAL
    assert isinstance(nodo.izquierda, NodoValor)
    assert nodo.izquierda.valor is True
    assert isinstance(nodo.derecha, NodoValor)
    assert nodo.derecha.valor is True


def test_verdadero_igual_falso_parsea_como_binaria_con_nodovalor_booleanos() -> None:
    tokens, ast = _parsear_sin_error_booleano_en_termino("verdadero == falso")

    assert any(t.tipo == TipoToken.IGUAL for t in tokens)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoOperacionBinaria)
    assert nodo.operador.tipo == TipoToken.IGUAL
    assert isinstance(nodo.izquierda, NodoValor)
    assert nodo.izquierda.valor is True
    assert isinstance(nodo.derecha, NodoValor)
    assert nodo.derecha.valor is False
