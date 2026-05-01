import logging

from .base import ValidadorBase
from ..ast_nodes import (
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoHilo,
    NodoImport,
    NodoUsar,
    NodoImportDesde,
)


class ValidadorAuditoria(ValidadorBase):
    """Validador que registra las primitivas utilizadas.

    Modos de uso:
    - análisis semántico: ``emitir_side_effects=False`` (sin efectos secundarios)
    - ejecución/auditoría activa: ``emitir_side_effects=True`` (emite logs)
    """

    def __init__(self, emitir_side_effects: bool = True) -> None:
        super().__init__()
        self.emitir_side_effects = emitir_side_effects

    def _log(self, mensaje: str) -> None:
        # Fuente de verdad centralizada para side effects de auditoría.
        if not self.emitir_side_effects:
            return
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
