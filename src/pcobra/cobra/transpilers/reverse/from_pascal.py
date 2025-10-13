# -*- coding: utf-8 -*-
"""Transpilador inverso desde Pascal a Cobra usando Lark."""

from __future__ import annotations

from typing import Any, List

from lark import Lark, Transformer

from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler
from pcobra.cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoPara,
    NodoValor,
    NodoIdentificador,
)


PASCAL_GRAMMAR = r"""
start: function_def

function_def: "function" NAME "(" NAME ":" NAME ")" ":" NAME ";" block ";"

block: "begin" statements "end"

statements: (statement ";")*

?statement: assignment
          | if_statement
          | for_loop

assignment: NAME ":=" expr

if_statement: "if" expr "then" block ("else" block)?

for_loop: "for" NAME ":=" expr "to" expr "do" block

?expr: NUMBER        -> number
     | NAME          -> var

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /\d+/

%import common.WS
%ignore WS
"""


class _PascalTransformer(Transformer):
    """Convierte el árbol de Lark en nodos AST de Cobra."""

    def start(self, items: List[Any]) -> List[Any]:  # type: ignore[override]
        return items

    def statements(self, items: List[Any]) -> List[Any]:  # type: ignore[override]
        return items

    def block(self, items: List[Any]) -> List[Any]:  # type: ignore[override]
        return items[0] if items else []

    def number(self, items: List[Any]) -> NodoValor:  # type: ignore[override]
        return NodoValor(int(items[0]))

    def var(self, items: List[Any]) -> NodoIdentificador:  # type: ignore[override]
        return NodoIdentificador(str(items[0]))

    def assignment(self, items: List[Any]) -> NodoAsignacion:  # type: ignore[override]
        nombre = str(items[0])
        expresion = items[1]
        return NodoAsignacion(nombre, expresion)

    def if_statement(self, items: List[Any]) -> NodoCondicional:  # type: ignore[override]
        condicion = items[0]
        bloque_si = items[1]
        bloque_sino = items[2] if len(items) > 2 else []
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def for_loop(self, items: List[Any]) -> NodoPara:  # type: ignore[override]
        variable = str(items[0])
        inicio = items[1]
        fin = items[2]
        cuerpo = items[3]
        iterable = NodoLlamadaFuncion("range", [inicio, fin])
        return NodoPara(variable, iterable, cuerpo)

    def function_def(self, items: List[Any]) -> NodoFuncion:  # type: ignore[override]
        nombre = str(items[0])
        parametro = str(items[1])
        cuerpo = items[-1]
        return NodoFuncion(nombre, [parametro], cuerpo)


class ReverseFromPascal(BaseReverseTranspiler):
    """Transpilador inverso de Pascal a Cobra."""

    def __init__(self) -> None:
        super().__init__()
        self.parser = Lark(PASCAL_GRAMMAR, parser="lalr")
        self.transformer = _PascalTransformer()

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código Pascal."""

        tree = self.parser.parse(code)
        self.ast = self.transformer.transform(tree)  # type: ignore[assignment]
        return self.ast

