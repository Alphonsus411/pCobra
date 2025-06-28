"""Optimizacion de plegado de constantes para Cobra."""

from __future__ import annotations

from typing import Any, List

from ..visitor import NodeVisitor
from ..ast_nodes import (
    NodoAsignacion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoValor,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoMetodo,
    NodoRetorno,
)
from backend.src.cobra.lexico.lexer import TipoToken, Token


class _ConstantFolder(NodeVisitor):
    def visit_asignacion(self, nodo: NodoAsignacion):
        """Visita una asignación y actualiza su expresión.

        Las pruebas antiguas usan nodos de asignación simplificados que
        almacenan la expresión en el atributo ``valor`` en lugar de
        ``expresion``.  Para mantener compatibilidad comprobamos ambos
        nombres de atributo.
        """

        attr = 'expresion' if hasattr(nodo, 'expresion') else 'valor'
        setattr(nodo, attr, self.visit(getattr(nodo, attr)))
        return nodo

    def visit_operacion_binaria(self, nodo: NodoOperacionBinaria):
        nodo.izquierda = self.visit(nodo.izquierda)
        nodo.derecha = self.visit(nodo.derecha)
        if isinstance(nodo.izquierda, NodoValor) and isinstance(nodo.derecha, NodoValor):
            try:
                resultado = self._evaluar(nodo.izquierda.valor, nodo.operador, nodo.derecha.valor)
                return NodoValor(resultado)
            except Exception:
                return nodo
        return nodo

    def visit_operacion_unaria(self, nodo: NodoOperacionUnaria):
        nodo.operando = self.visit(nodo.operando)
        if isinstance(nodo.operando, NodoValor):
            try:
                resultado = self._evaluar_unaria(nodo.operador, nodo.operando.valor)
                return NodoValor(resultado)
            except Exception:
                return nodo
        return nodo

    def visit_condicional(self, nodo: NodoCondicional):
        nodo.condicion = self.visit(nodo.condicion)
        nodo.bloque_si = [self.visit(n) for n in nodo.bloque_si]
        nodo.bloque_sino = [self.visit(n) for n in nodo.bloque_sino]
        return nodo

    def visit_bucle_mientras(self, nodo: NodoBucleMientras):
        nodo.condicion = self.visit(nodo.condicion)
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        return nodo

    def visit_funcion(self, nodo: NodoFuncion):
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        return nodo

    def visit_metodo(self, nodo: NodoMetodo):
        nodo.cuerpo = [self.visit(n) for n in nodo.cuerpo]
        return nodo

    def generic_visit(self, nodo: Any):
        for attr, value in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(value, list):
                setattr(nodo, attr, [self.visit(v) for v in value])
            elif hasattr(value, "aceptar"):
                setattr(nodo, attr, self.visit(value))
        return nodo

    # Helpers --------------------------------------------------------------
    def _evaluar(self, izq: Any, token: Token, der: Any):
        if token.tipo == TipoToken.SUMA:
            return izq + der
        if token.tipo == TipoToken.RESTA:
            return izq - der
        if token.tipo == TipoToken.MULT:
            return izq * der
        if token.tipo == TipoToken.DIV:
            return izq / der
        if token.tipo == TipoToken.MOD:
            return izq % der
        if token.tipo == TipoToken.MAYORQUE:
            return izq > der
        if token.tipo == TipoToken.MAYORIGUAL:
            return izq >= der
        if token.tipo == TipoToken.MENORIGUAL:
            return izq <= der
        if token.tipo == TipoToken.IGUAL:
            return izq == der
        if token.tipo == TipoToken.DIFERENTE:
            return izq != der
        if token.tipo == TipoToken.AND:
            return bool(izq) and bool(der)
        if token.tipo == TipoToken.OR:
            return bool(izq) or bool(der)
        raise ValueError("Operador no soportado")

    def _evaluar_unaria(self, token: Token, valor: Any):
        if token.tipo == TipoToken.NOT:
            return not bool(valor)
        raise ValueError("Operador unario no soportado")


def optimize_constants(ast: List[Any]):
    """Aplica plegado de constantes a la lista de nodos."""
    folder = _ConstantFolder()
    return [folder.visit(n) for n in ast]
