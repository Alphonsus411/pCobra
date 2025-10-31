# -*- coding: utf-8 -*-
"""Transpilador inverso desde Matlab a Cobra usando Lark."""

from __future__ import annotations

from typing import Any, List
import re

try:  # pragma: no cover - si lark está instalado se utiliza directamente
    from lark import Lark, Transformer
    _LARK_DISPONIBLE = True
except ImportError:  # pragma: no cover - ruta usada en los tests
    _LARK_DISPONIBLE = False

    class Transformer:  # type: ignore[override]
        """Sustituto mínimo del transformer de Lark."""

    class Lark:  # pylint: disable=too-few-public-methods
        """Marcador de posición para conservar la API cuando falta Lark."""

        def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - firma fija
            self.args = args
            self.kwargs = kwargs

        def parse(self, _source: str):  # pragma: no cover - no debería invocarse
            raise RuntimeError("Lark no está disponible en este entorno")

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


MATLAB_GRAMMAR = r"""
start: (function_def | statement)+

function_def: "function" NAME "=" NAME "(" NAME ")" statements "end"

statements: statement*

?statement: assignment
          | if_statement
          | for_loop

assignment: NAME "=" expr

if_statement: "if" expr statements ("else" statements)? "end"

for_loop: "for" NAME "=" expr ":" expr statements "end"

?expr: NUMBER        -> number
     | NAME          -> var

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /\d+/

%import common.WS
%ignore WS
%ignore ";"
"""


class _MatlabTransformer(Transformer):
    """Convierte el árbol de Lark en nodos AST de Cobra."""

    def start(self, items: List[Any]) -> List[Any]:  # type: ignore[override]
        return items

    def statements(self, items: List[Any]) -> List[Any]:  # type: ignore[override]
        return items

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
        _, nombre, parametro, cuerpo = items
        return NodoFuncion(str(nombre), [str(parametro)], cuerpo)


class ReverseFromMatlab(BaseReverseTranspiler):
    """Transpilador inverso de Matlab a Cobra."""

    def __init__(self) -> None:
        super().__init__()
        if _LARK_DISPONIBLE:
            self.parser = Lark(MATLAB_GRAMMAR, parser="lalr")
            self.transformer = _MatlabTransformer()
        else:
            self.parser = None
            self.transformer = None

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código Matlab."""

        if self.parser and self.transformer:
            tree = self.parser.parse(code)
            self.ast = self.transformer.transform(tree)  # type: ignore[assignment]
            return self.ast

        self.ast = self._fallback_parse(code)
        return self.ast

    def _fallback_parse(self, code: str) -> List[Any]:
        """Analizador mínimo para entornos sin la dependencia ``lark``."""

        lineas = [line.strip() for line in code.splitlines() if line.strip()]
        if not lineas:
            return []

        cabecera = lineas.pop(0)
        match = re.match(r"function\s+\w+\s*=\s*(\w+)\((\w+)\)", cabecera)
        if not match:
            raise ValueError("Formato de función de Matlab no soportado en modo de compatibilidad")

        nombre_funcion, parametro = match.groups()
        cuerpo: List[Any] = []
        pila_cuerpos: List[List[Any]] = [cuerpo]
        pila_constructores: List[str] = []

        def _destino_actual() -> List[Any]:
            return pila_cuerpos[-1]

        def _crear_expresion(valor: str) -> Any:
            valor = valor.strip()
            if valor.isdigit():
                return NodoValor(int(valor))
            return NodoIdentificador(valor)

        idx = 0
        while idx < len(lineas):
            linea = lineas[idx]
            if linea.startswith("if "):
                condicion = _crear_expresion(linea[3:])
                nodo = NodoCondicional(condicion, [], [])
                _destino_actual().append(nodo)
                pila_constructores.append("if")
                pila_cuerpos.append(nodo.bloque_si)
                idx += 1
                continue
            if linea.startswith("else") and pila_constructores and pila_constructores[-1] == "if":
                pila_cuerpos.pop()
                nodo_if = _destino_actual()[-1]
                pila_cuerpos.append(nodo_if.bloque_sino)
                idx += 1
                continue
            if linea.startswith("for "):
                bucle = linea[4:]
                match_for = re.match(r"(\w+)\s*=\s*(\d+)\s*:\s*(\d+)", bucle)
                if not match_for:
                    raise ValueError("Bucle for de Matlab no soportado en modo de compatibilidad")
                variable, inicio, fin = match_for.groups()
                iterable = NodoLlamadaFuncion("range", [NodoValor(int(inicio)), NodoValor(int(fin))])
                nodo_for = NodoPara(variable, iterable, [])
                _destino_actual().append(nodo_for)
                pila_constructores.append("for")
                pila_cuerpos.append(nodo_for.cuerpo)
                idx += 1
                continue
            if linea == "end":
                if pila_constructores:
                    pila_constructores.pop()
                    pila_cuerpos.pop()
                    idx += 1
                    continue
                break

            if "=" in linea:
                nombre, expresion = [parte.strip() for parte in linea.split("=", 1)]
                nodo_asignacion = NodoAsignacion(nombre, _crear_expresion(expresion))
                _destino_actual().append(nodo_asignacion)
                idx += 1
                continue

            idx += 1

        funcion = NodoFuncion(nombre_funcion, [parametro], cuerpo)
        return [funcion]

