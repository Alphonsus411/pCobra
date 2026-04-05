"""Eliminacion simple de codigo muerto para Cobra."""

from __future__ import annotations

from typing import Any, List

from ..ast_nodes import (
    NodoAST,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoMetodo,
    NodoRetorno,
    NodoThrow,
    NodoRomper,
    NodoContinuar,
    NodoValor,
    NodoBloque,
)
from ..visitor import NodeVisitor


class _DeadCodeRemover(NodeVisitor):
    def _error_estructura(self, ruta: str, valor: Any):
        raise RuntimeError(
            f"Estructura AST inválida en optimización (dead_code) en '{ruta}': "
            f"{type(valor).__name__}"
        )

    def visit_condicional(self, nodo: NodoCondicional):
        nodo.condicion = self.visit(nodo.condicion)
        nodo.bloque_si = self._limpiar_bloque(
            NodoBloque([self.visit(n) for n in nodo.bloque_si.instrucciones])
        )
        nodo.bloque_sino = self._limpiar_bloque(
            NodoBloque([self.visit(n) for n in nodo.bloque_sino.instrucciones])
        )
        if isinstance(nodo.condicion, NodoValor) and isinstance(nodo.condicion.valor, bool):
            if nodo.condicion.valor is True:
                return nodo.bloque_si.instrucciones
            if nodo.condicion.valor is False:
                return nodo.bloque_sino.instrucciones
        return nodo

    def visit_bucle_mientras(self, nodo: NodoBucleMientras):
        nodo.condicion = self.visit(nodo.condicion)
        nodo.cuerpo = self._limpiar_bloque(
            NodoBloque([self.visit(n) for n in nodo.cuerpo.instrucciones])
        )
        if isinstance(nodo.condicion, NodoValor):
            if nodo.condicion.valor is False:
                return []
            if (
                nodo.condicion.valor is True
                and nodo.cuerpo.instrucciones
                and self._es_salida(nodo.cuerpo.instrucciones[-1])
            ):
                cuerpo = nodo.cuerpo.instrucciones
                if isinstance(cuerpo[-1], (NodoRomper, NodoContinuar)):
                    cuerpo = cuerpo[:-1]
                return cuerpo
        return nodo

    def visit_funcion(self, nodo: NodoFuncion):
        nodo.cuerpo = self._limpiar_bloque(
            NodoBloque([self.visit(n) for n in nodo.cuerpo.instrucciones])
        )
        return nodo

    def visit_metodo(self, nodo: NodoMetodo):
        nodo.cuerpo = self._limpiar_bloque(
            NodoBloque([self.visit(n) for n in nodo.cuerpo.instrucciones])
        )
        return nodo

    def generic_visit(self, node: Any):
        if not isinstance(node, NodoAST):
            self._error_estructura(type(node).__name__, node)
        for attr, value in vars(node).items():
            ruta = f"{node.__class__.__name__}.{attr}"
            if isinstance(value, NodoBloque):
                value.instrucciones = [self.visit(v) for v in value.instrucciones]
                continue
            if isinstance(value, list):
                nuevos = []
                for idx, v in enumerate(value):
                    if isinstance(v, NodoAST):
                        nuevos.append(self.visit(v))
                    elif isinstance(v, list):
                        self._error_estructura(f"{ruta}[{idx}]", v)
                    else:
                        nuevos.append(v)
                setattr(node, attr, nuevos)
            elif isinstance(value, NodoAST):
                setattr(node, attr, self.visit(value))
        return node

    # Helpers --------------------------------------------------------------
    def _es_salida(self, nodo: Any) -> bool:
        if isinstance(nodo, (NodoRetorno, NodoThrow, NodoRomper, NodoContinuar)):
            return True
        if isinstance(nodo, NodoCondicional):
            if nodo.bloque_si.instrucciones and nodo.bloque_sino.instrucciones:
                return self._es_salida(nodo.bloque_si.instrucciones[-1]) and self._es_salida(
                    nodo.bloque_sino.instrucciones[-1]
                )
        return False

    def _limpiar_bloque(self, bloque: NodoBloque):
        limpios: List[Any] = []
        for n in bloque.instrucciones:
            limpios.append(n)
            if self._es_salida(n):
                break
        return NodoBloque(limpios)


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
