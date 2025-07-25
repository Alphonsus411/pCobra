import logging

from .base import ValidadorBase
from core.ast_nodes import (
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoHilo,
    NodoImport,
    NodoUsar,
    NodoImportDesde,
)


class ValidadorAuditoria(ValidadorBase):
    """Validador que registra las primitivas utilizadas."""

    def _log(self, mensaje: str) -> None:
        logging.warning(mensaje)

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        self._log(f"Llamada a funcion: {nodo.nombre}")
        self.generic_visit(nodo)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        self._log(f"Llamada a metodo: {nodo.nombre_metodo}")
        self.generic_visit(nodo)

    def visit_hilo(self, nodo: NodoHilo):
        self._log(f"Ejecucion de hilo: {nodo.llamada.nombre}")
        nodo.llamada.aceptar(self)
        self.delegar(nodo)

    def visit_import(self, nodo: NodoImport):
        self._log(f"Import de modulo: {nodo.ruta}")
        self.generic_visit(nodo)

    def visit_usar(self, nodo: NodoUsar):
        self._log(f"Usar modulo: {nodo.modulo}")
        self.generic_visit(nodo)

    def visit_import_desde(self, nodo: NodoImportDesde):
        self._log(f"Importar desde: {nodo.modulo}")
        self.generic_visit(nodo)
