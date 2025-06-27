"""Optimizacion para integrar funciones pequeñas en su punto de uso."""

from __future__ import annotations

from typing import Any, List

from ..ast_nodes import NodoFuncion, NodoRetorno, NodoLlamadaFuncion
from ..visitor import NodeVisitor


class _FunctionInliner(NodeVisitor):
    """Recolecta funciones simples y reemplaza sus llamadas."""

    def __init__(self):
        self.funciones: dict[str, Any] = {}

    def visit_funcion(self, nodo: NodoFuncion):
        # Solo se consideran funciones sin parámetros y con un único return
        if (
            len(nodo.parametros) == 0
            and len(nodo.cuerpo) == 1
            and isinstance(nodo.cuerpo[0], NodoRetorno)
        ):
            self.funciones[nodo.nombre] = self.visit(nodo.cuerpo[0].expresion)
            return None  # se elimina la definición
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        return nodo

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.funciones and not nodo.argumentos:
            return self.funciones[nodo.nombre]
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
