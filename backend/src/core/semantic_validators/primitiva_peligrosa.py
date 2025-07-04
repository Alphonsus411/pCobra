from .base import ValidadorBase
from src.core.ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo


class PrimitivaPeligrosaError(Exception):
    """Se lanza cuando se utiliza una primitiva peligrosa."""
    pass


class ValidadorPrimitivaPeligrosa(ValidadorBase):
    """Validador que detecta llamadas a primitivas peligrosas."""

    PRIMITIVAS_PELIGROSAS = {
        "leer_archivo",
        "escribir_archivo",
        "obtener_url",
        "hilo",
        "leer",
        "escribir",
        "existe",
        "eliminar",
        "enviar_post",
        "ejecutar",
        "listar_dir",
    }

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
