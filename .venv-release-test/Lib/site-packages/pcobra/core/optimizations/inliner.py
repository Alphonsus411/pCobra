"""Optimizacion para integrar funciones pequeñas en su punto de uso."""

from __future__ import annotations

from typing import Any, List, Tuple
import copy

from ..ast_nodes import (
    NodoAST,
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
    NodoBloque,
)
from ..visitor import NodeVisitor


class _FunctionInliner(NodeVisitor):
    """Recolecta funciones simples y reemplaza sus llamadas."""

    def __init__(self):
        self.funciones: dict[str, Tuple[List[str], Any]] = {}

    def _error_estructura(self, ruta: str, valor: Any):
        raise RuntimeError(
            f"Estructura AST inválida en optimización (inliner) en '{ruta}': "
            f"{type(valor).__name__}"
        )

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
        for attr, value in vars(nodo).items():
            if isinstance(value, list):
                if any(self._tiene_efectos_secundarios(v) for v in value):
                    return True
            elif isinstance(value, NodoBloque):
                if any(
                    self._tiene_efectos_secundarios(v) for v in value.instrucciones
                ):
                    return True
            elif isinstance(value, NodoAST):
                if self._tiene_efectos_secundarios(value):
                    return True
        return False

    def visit_funcion(self, nodo: NodoFuncion):
        if len(nodo.cuerpo.instrucciones) == 1 and isinstance(
            nodo.cuerpo.instrucciones[0], NodoRetorno
        ):
            expresion = self.visit(nodo.cuerpo.instrucciones[0].expresion)
            if not self._tiene_efectos_secundarios(expresion):
                self.funciones[nodo.nombre] = (nodo.parametros, expresion)
                return None
        nodo.cuerpo = NodoBloque([self.visit(n) for n in nodo.cuerpo.instrucciones])
        return nodo

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.funciones:
            params, expr = self.funciones[nodo.nombre]
            if len(params) == len(nodo.argumentos):
                reemplazos = dict(zip(params, nodo.argumentos))
                return self._reemplazar(copy.deepcopy(expr), reemplazos)
        return nodo

    def generic_visit(self, node: Any):
        if not isinstance(node, NodoAST):
            self._error_estructura(type(node).__name__, node)
        for attr, value in vars(node).items():
            ruta = f"{node.__class__.__name__}.{attr}"
            if isinstance(value, NodoBloque):
                value.instrucciones = [
                    self.visit(v) for v in value.instrucciones if v is not None
                ]
                continue
            if isinstance(value, list):
                nuevos = []
                for idx, v in enumerate(value):
                    if isinstance(v, NodoAST):
                        res = self.visit(v)
                        if res is None:
                            continue
                        if isinstance(res, list):
                            nuevos.extend(res)
                        else:
                            nuevos.append(res)
                    elif isinstance(v, list):
                        self._error_estructura(f"{ruta}[{idx}]", v)
                    else:
                        nuevos.append(v)
                setattr(node, attr, nuevos)
            elif isinstance(value, NodoAST):
                setattr(node, attr, self.visit(value))
        return node

    def _reemplazar(self, node: Any, reemplazos: dict[str, Any]):
        if isinstance(node, NodoIdentificador) and node.nombre in reemplazos:
            return copy.deepcopy(reemplazos[node.nombre])
        for attr, value in vars(node).items():
            if isinstance(value, list):
                setattr(node, attr, [self._reemplazar(v, reemplazos) for v in value])
            elif isinstance(value, NodoBloque):
                value.instrucciones = [
                    self._reemplazar(v, reemplazos) for v in value.instrucciones
                ]
            elif isinstance(value, NodoAST):
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
