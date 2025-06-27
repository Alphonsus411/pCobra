from .base import ValidadorBase
from src.core.ast_nodes import NodoLlamadaFuncion, NodoLlamadaMetodo, NodoAtributo
from .primitiva_peligrosa import PrimitivaPeligrosaError


class ValidadorProhibirReflexion(ValidadorBase):
    """Impide el uso de mecanismos de reflexi\u00f3n e introspecci\u00f3n."""

    FUNCIONES_PROHIBIDAS = {
        "eval",
        "exec",
        "getattr",
        "setattr",
        "hasattr",
        "globals",
        "locals",
        "vars",
    }

    ATRIBUTOS_PROHIBIDOS = {"__dict__", "__class__", "__bases__", "__mro__"}

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.FUNCIONES_PROHIBIDAS:
            raise PrimitivaPeligrosaError(
                f"Uso de reflexi\u00f3n no permitido: {nodo.nombre}"
            )
        self.generic_visit(nodo)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        if nodo.nombre_metodo in self.FUNCIONES_PROHIBIDAS:
            raise PrimitivaPeligrosaError(
                f"Uso de reflexi\u00f3n no permitido: {nodo.nombre_metodo}"
            )
        self.generic_visit(nodo)

    def visit_atributo(self, nodo: NodoAtributo):
        if nodo.nombre in self.ATRIBUTOS_PROHIBIDOS or nodo.nombre.startswith("__"):
            raise PrimitivaPeligrosaError(
                f"Acceso reflexivo no permitido: {nodo.nombre}"
            )
        self.generic_visit(nodo)
