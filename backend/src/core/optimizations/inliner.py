"""Optimizacion para integrar funciones pequeñas en su punto de uso."""

from __future__ import annotations

from typing import Any, List, Tuple
import copy

from ..ast_nodes import (
    NodoFuncion,
    NodoRetorno,
    NodoLlamadaFuncion,
    NodoIdentificador,
)
from ..visitor import NodeVisitor


class _FunctionInliner(NodeVisitor):
    """Recolecta funciones simples y reemplaza sus llamadas."""

    def __init__(self):
        self.funciones: dict[str, Tuple[List[str], Any]] = {}

    def visit_funcion(self, nodo: NodoFuncion):
        if len(nodo.cuerpo) == 1 and isinstance(nodo.cuerpo[0], NodoRetorno):
            expresion = self.visit(nodo.cuerpo[0].expresion)
            self.funciones[nodo.nombre] = (nodo.parametros, expresion)
            return None
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        return nodo

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.funciones:
            params, expr = self.funciones[nodo.nombre]
            if len(params) == len(nodo.argumentos):
                reemplazos = dict(zip(params, nodo.argumentos))
                return self._reemplazar(copy.deepcopy(expr), reemplazos)
        return nodo

    def generic_visit(self, nodo: Any):
        for attr, value in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(value, list):
                nuevos = []
                for v in value:
                    res = self.visit(v)
                    if res is None:
                        continue
                    elif isinstance(res, list):
                        nuevos.extend(res)
                    else:
                        nuevos.append(res)
                setattr(nodo, attr, nuevos)
            elif hasattr(value, "aceptar"):
                setattr(nodo, attr, self.visit(value))
        return nodo

    def _reemplazar(self, nodo: Any, reemplazos: dict[str, Any]):
        if isinstance(nodo, NodoIdentificador) and nodo.nombre in reemplazos:
            return reemplazos[nodo.nombre]
        for attr, value in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(value, list):
                setattr(nodo, attr, [self._reemplazar(v, reemplazos) for v in value])
            elif hasattr(value, "__dict__"):
                setattr(nodo, attr, self._reemplazar(value, reemplazos))
        return nodo


def inline_functions(ast: List[Any]):
    """Aplica inlining a funciones simples en la lista de nodos."""
    inliner = _FunctionInliner()
    resultado = []
    for nodo in ast:
        res = inliner.visit(nodo)
        if res is None:
            continue
        if isinstance(res, list):
            resultado.extend(res)
        else:
            resultado.append(res)
    return resultado
