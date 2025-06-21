# coding: utf-8
"""Validador semántico para prevenir el uso de primitivas peligrosas."""

from src.core.visitor import NodeVisitor
from src.core.ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo


class PrimitivaPeligrosaError(Exception):
    """Se lanza cuando se intenta utilizar una primitiva peligrosa."""
    pass


class ValidadorSemantico(NodeVisitor):
    """Recorre el AST y valida que no se usen primitivas peligrosas."""

    PRIMITIVAS_PELIGROSAS = {"leer_archivo", "escribir_archivo", "obtener_url", "hilo"}

    def generic_visit(self, node):
        for atributo in getattr(node, "__dict__", {}).values():
            if isinstance(atributo, list):
                for elem in atributo:
                    if hasattr(elem, "aceptar"):
                        elem.aceptar(self)
            elif hasattr(atributo, "aceptar"):
                atributo.aceptar(self)

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(f"Uso de primitiva peligrosa: '{nodo.nombre}'")
        self.generic_visit(nodo)

    def visit_hilo(self, nodo: NodoHilo):
        if nodo.llamada.nombre in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(f"Uso de primitiva peligrosa: '{nodo.llamada.nombre}'")
        nodo.llamada.aceptar(self)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        if nodo.nombre_metodo in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre_metodo}'"
            )
        self.generic_visit(nodo)


__all__ = ["PrimitivaPeligrosaError", "ValidadorSemantico"]
