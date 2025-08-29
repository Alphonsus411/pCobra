"""Eliminacion simple de codigo muerto para Cobra."""

from __future__ import annotations

from typing import Any, List

from core.ast_nodes import (
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoMetodo,
    NodoRetorno,
    NodoThrow,
    NodoRomper,
    NodoContinuar,
    NodoValor,
)
from core.visitor import NodeVisitor


class _DeadCodeRemover(NodeVisitor):
    def visit_condicional(self, nodo: NodoCondicional):
        nodo.condicion = self.visit(nodo.condicion)
        nodo.bloque_si = self._limpiar_bloque([self.visit(n) for n in nodo.bloque_si])
        nodo.bloque_sino = self._limpiar_bloque(
            [self.visit(n) for n in nodo.bloque_sino]
        )
        if isinstance(nodo.condicion, NodoValor):
            return nodo.bloque_si if nodo.condicion.valor else nodo.bloque_sino
        return nodo

    def visit_bucle_mientras(self, nodo: NodoBucleMientras):
        nodo.condicion = self.visit(nodo.condicion)
        nodo.cuerpo = self._limpiar_bloque([self.visit(n) for n in nodo.cuerpo])
        if isinstance(nodo.condicion, NodoValor):
            if nodo.condicion.valor is False:
                return []
            if (
                nodo.condicion.valor is True
                and nodo.cuerpo
                and self._es_salida(nodo.cuerpo[-1])
            ):
                cuerpo = nodo.cuerpo
                if isinstance(cuerpo[-1], (NodoRomper, NodoContinuar)):
                    cuerpo = cuerpo[:-1]
                return cuerpo
        return nodo

    def visit_funcion(self, nodo: NodoFuncion):
        nodo.cuerpo = self._limpiar_bloque([self.visit(n) for n in nodo.cuerpo])
        return nodo

    def visit_metodo(self, nodo: NodoMetodo):
        nodo.cuerpo = self._limpiar_bloque([self.visit(n) for n in nodo.cuerpo])
        return nodo

    def generic_visit(self, node: Any):
        for attr, value in list(getattr(node, "__dict__", {}).items()):
            if isinstance(value, list):
                setattr(node, attr, [self.visit(v) for v in value])
            elif hasattr(value, "aceptar"):
                setattr(node, attr, self.visit(value))
        return node

    # Helpers --------------------------------------------------------------
    def _es_salida(self, nodo: Any) -> bool:
        if isinstance(nodo, (NodoRetorno, NodoThrow, NodoRomper, NodoContinuar)):
            return True
        if isinstance(nodo, NodoCondicional):
            if nodo.bloque_si and nodo.bloque_sino:
                return self._es_salida(nodo.bloque_si[-1]) and self._es_salida(
                    nodo.bloque_sino[-1]
                )
        return False

    def _limpiar_bloque(self, nodos: List[Any]):
        limpios = []
        for n in nodos:
            limpios.append(n)
            if self._es_salida(n):
                break
        return limpios


def remove_dead_code(ast: List[Any]):
    """Elimina codigo que nunca se ejecutara del AST."""
    remover = _DeadCodeRemover()
    resultado = []
    for nodo in ast:
        res = remover.visit(nodo)
        if isinstance(res, list):
            resultado.extend(res)
        else:
            resultado.append(res)
    return resultado
