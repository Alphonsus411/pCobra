"""Optimizacion para integrar funciones pequeñas en su punto de uso."""

from __future__ import annotations

from typing import Any, List, Tuple
import copy

from ..ast_nodes import (
    NodoFuncion,
    NodoRetorno,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoAsignacion,
    NodoImprimir,
    NodoHilo,
    NodoThrow,
    NodoYield,
    NodoEsperar,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoIdentificador,
)
from ..visitor import NodeVisitor


class _FunctionInliner(NodeVisitor):
    """Recolecta funciones simples y reemplaza sus llamadas."""

    def __init__(self):
        self.funciones: dict[str, Tuple[List[str], Any]] = {}

    def _tiene_efectos_secundarios(self, nodo: Any) -> bool:
        """Determina si ``nodo`` produce efectos secundarios."""
        if isinstance(
            nodo,
            (
                NodoAsignacion,
                NodoLlamadaFuncion,
                NodoLlamadaMetodo,
                NodoImprimir,
                NodoHilo,
                NodoThrow,
                NodoYield,
                NodoEsperar,
                NodoDel,
                NodoGlobal,
                NodoNoLocal,
            ),
        ):
            return True
        for attr, value in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(value, list):
                if any(self._tiene_efectos_secundarios(v) for v in value):
                    return True
            elif hasattr(value, "__dict__"):
                if self._tiene_efectos_secundarios(value):
                    return True
        return False

    def visit_funcion(self, nodo: NodoFuncion):
        if len(nodo.cuerpo) == 1 and isinstance(nodo.cuerpo[0], NodoRetorno):
            expresion = self.visit(nodo.cuerpo[0].expresion)
            if not self._tiene_efectos_secundarios(expresion):
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

    def generic_visit(self, node: Any):
        for attr, value in list(getattr(node, "__dict__", {}).items()):
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
                setattr(node, attr, nuevos)
            elif hasattr(value, "aceptar"):
                setattr(node, attr, self.visit(value))
        return node

    def _reemplazar(self, node: Any, reemplazos: dict[str, Any]):
        if isinstance(node, NodoIdentificador) and node.nombre in reemplazos:
            return reemplazos[node.nombre]
        for attr, value in list(getattr(node, "__dict__", {}).items()):
            if isinstance(value, list):
                setattr(node, attr, [self._reemplazar(v, reemplazos) for v in value])
            elif hasattr(value, "__dict__"):
                setattr(node, attr, self._reemplazar(value, reemplazos))
        return node


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
