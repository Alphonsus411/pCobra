from __future__ import annotations

import pytest

from cobra.core import Lexer, Parser
from core.ast_nodes import (
    NodoBloque,
    NodoBucleMientras,
    NodoCondicional,
    NodoPara,
    NodoValor,
)
from core.interpreter import InterpretadorCobra
from core.utils import ErrorEstructuraAST, validar_ast_estructural


def test_ast_falla_si_hay_lista_donde_se_espera_nodo_bloque() -> None:
    nodo = NodoCondicional(NodoValor(True), [NodoValor(1)], [NodoValor(0)])
    nodo.bloque_si = [NodoValor(1)]  # inyección inválida deliberada

    with pytest.raises(ErrorEstructuraAST, match="Se encontró lista donde se esperaba NodoBloque"):
        validar_ast_estructural([nodo])


@pytest.mark.parametrize(
    ("codigo", "atributo_bloque"),
    [
        ("si 1 == 1:\n    pasar\nfin", "bloque_si"),
        ("mientras 1 == 1:\n    pasar\nfin", "cuerpo"),
        ("para i in [1]:\n    pasar\nfin", "cuerpo"),
    ],
)
def test_parser_genera_nodos_bloque_en_estructuras_de_control(
    codigo: str, atributo_bloque: str
) -> None:
    ast = Parser(Lexer(codigo).tokenizar()).parsear()
    assert ast
    nodo = ast[0]
    assert isinstance(getattr(nodo, atributo_bloque), NodoBloque)


def test_validacion_falla_si_nodo_mientras_recibe_lista_cruda() -> None:
    nodo = NodoBucleMientras(NodoValor(True), [NodoValor(1)])
    nodo.cuerpo = [NodoValor(1)]  # inyección inválida deliberada

    with pytest.raises(ErrorEstructuraAST, match="Se encontró lista donde se esperaba NodoBloque"):
        validar_ast_estructural([nodo])


def test_validacion_falla_si_nodo_para_recibe_lista_cruda() -> None:
    nodo = NodoPara("i", NodoValor([1]), [NodoValor(1)])
    nodo.cuerpo = [NodoValor(1)]  # inyección inválida deliberada

    with pytest.raises(ErrorEstructuraAST, match="Se encontró lista donde se esperaba NodoBloque"):
        validar_ast_estructural([nodo])


def test_regresion_ejecutar_ast_no_revive_error_de_dict_en_listas() -> None:
    inter = InterpretadorCobra()
    nodo = NodoCondicional(NodoValor(True), NodoBloque([NodoValor(1)]), NodoBloque())
    nodo.bloque_si = [NodoValor(1)]  # inyección inválida deliberada

    with pytest.raises(RuntimeError, match=r"^Estructura AST inválida en fase 'parseo':"):
        inter.ejecutar_ast([nodo])


def test_nodo_bloque_preserva_orden_e_iteracion() -> None:
    primero = NodoValor(1)
    segundo = NodoValor(2)
    bloque = NodoBloque([primero, segundo])

    assert list(bloque) == [primero, segundo]
    assert bloque.instrucciones == [primero, segundo]
