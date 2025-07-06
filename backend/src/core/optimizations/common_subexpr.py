"""Eliminación de subexpresiones comunes para Cobra."""

from __future__ import annotations

from typing import Any, List

from ..visitor import NodeVisitor
from ..ast_nodes import (
    NodoAsignacion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoValor,
    NodoFuncion,
    NodoMetodo,
)


def _expr_key(expr: Any):
    if isinstance(expr, NodoOperacionBinaria):
        return (
            "bin",
            expr.operador.tipo,
            _expr_key(expr.izquierda),
            _expr_key(expr.derecha),
        )
    if isinstance(expr, NodoOperacionUnaria):
        return ("un", expr.operador.tipo, _expr_key(expr.operando))
    if isinstance(expr, NodoIdentificador):
        return ("id", expr.nombre)
    if isinstance(expr, NodoValor):
        return ("val", expr.valor)
    return expr.__class__.__name__


class _ExprCounter(NodeVisitor):
    def __init__(self) -> None:
        self.counts: dict[Any, int] = {}

    def visit_operacion_binaria(self, nodo: NodoOperacionBinaria):
        key = _expr_key(nodo)
        self.counts[key] = self.counts.get(key, 0) + 1
        self.visit(nodo.izquierda)
        self.visit(nodo.derecha)

    def visit_operacion_unaria(self, nodo: NodoOperacionUnaria):
        key = _expr_key(nodo)
        self.counts[key] = self.counts.get(key, 0) + 1
        self.visit(nodo.operando)

    def generic_visit(self, nodo: Any):
        for attr, value in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(value, list):
                for v in value:
                    if hasattr(v, "aceptar"):
                        self.visit(v)
            elif hasattr(value, "aceptar"):
                self.visit(value)


class _CommonSubexprEliminator(NodeVisitor):
    def __init__(self, counts: dict[Any, int]):
        self.counts = counts
        self.maps: list[dict[Any, str]] = [{}]
        self.assigns: list[list[Any]] = [[]]

    # Helpers --------------------------------------------------------------
    def _current_map(self) -> dict[Any, str]:
        return self.maps[-1]

    def _current_assigns(self) -> list[Any]:
        return self.assigns[-1]

    def _replace(self, key: Any, expr: Any):
        cur = self._current_map()
        if key not in cur:
            nombre = f"_cse{len(cur)}"
            cur[key] = nombre
            self._current_assigns().append(NodoAsignacion(nombre, expr))
        return NodoIdentificador(cur[key])

    # Visit methods --------------------------------------------------------
    def visit_operacion_binaria(self, nodo: NodoOperacionBinaria):
        nodo.izquierda = self.visit(nodo.izquierda)
        nodo.derecha = self.visit(nodo.derecha)
        key = _expr_key(nodo)
        if self.counts.get(key, 0) > 1:
            return self._replace(key, NodoOperacionBinaria(nodo.izquierda, nodo.operador, nodo.derecha))
        return nodo

    def visit_operacion_unaria(self, nodo: NodoOperacionUnaria):
        nodo.operando = self.visit(nodo.operando)
        key = _expr_key(nodo)
        if self.counts.get(key, 0) > 1:
            return self._replace(key, NodoOperacionUnaria(nodo.operador, nodo.operando))
        return nodo

    def visit_funcion(self, nodo: NodoFuncion):
        self.maps.append({})
        self.assigns.append([])
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        assigns = self.assigns.pop()
        self.maps.pop()
        if assigns:
            nodo.cuerpo = assigns + nodo.cuerpo
        return nodo

    def visit_metodo(self, nodo: NodoMetodo):
        self.maps.append({})
        self.assigns.append([])
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        assigns = self.assigns.pop()
        self.maps.pop()
        if assigns:
            nodo.cuerpo = assigns + nodo.cuerpo
        return nodo

    def generic_visit(self, nodo: Any):
        for attr, value in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(value, list):
                setattr(nodo, attr, [self.visit(v) if hasattr(v, "aceptar") else v for v in value])
            elif hasattr(value, "aceptar"):
                setattr(nodo, attr, self.visit(value))
        return nodo


def eliminate_common_subexpressions(ast: List[Any]):
    """Reemplaza subexpresiones repetidas por variables temporales."""
    counter = _ExprCounter()
    for nodo in ast:
        counter.visit(nodo)
    eliminator = _CommonSubexprEliminator(counter.counts)
    resultado = []
    for nodo in ast:
        res = eliminator.visit(nodo)
        if isinstance(res, list):
            resultado.extend(res)
        else:
            resultado.append(res)
    asignaciones = eliminator.assigns.pop()
    if asignaciones:
        resultado = asignaciones + resultado
    return resultado
