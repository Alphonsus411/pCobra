from .base import ValidadorBase
from src.core.ast_nodes import NodoLlamadaFuncion, NodoLlamadaMetodo
from .primitiva_peligrosa import PrimitivaPeligrosaError


class ValidadorSistemaArchivos(ValidadorBase):
    """Proh\u00edbe funciones que acceden al sistema de archivos."""

    PROHIBIDAS = {
        "cargar_biblioteca",
        "obtener_funcion",
        "cargar_funcion",
        "compilar_extension",
        "cargar_extension",
        "compilar_y_cargar",
        "compilar_crate",
        "cargar_crate",
        "compilar_y_cargar_crate",
    }

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.PROHIBIDAS:
            raise PrimitivaPeligrosaError(
                f"Acceso al sistema de archivos no permitido: {nodo.nombre}"
            )
        self.generic_visit(nodo)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        if nodo.nombre_metodo in self.PROHIBIDAS:
            raise PrimitivaPeligrosaError(
                f"Acceso al sistema de archivos no permitido: {nodo.nombre_metodo}"
            )
        self.generic_visit(nodo)
