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
        # Fase explícita para alinear los side effects con el intérprete.
        self.mode = "execution" if emitir_side_effects else "analysis"

    def _log(self, mensaje: str) -> None:
        # Fuente de verdad centralizada para side effects de auditoría.
        if not self.in_execution():
            return
        logging.warning(mensaje)

    def in_execution(self) -> bool:
        """Indica si la auditoría debe emitir side effects en fase de ejecución."""
        return self.emitir_side_effects and self.mode == "execution"

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        """La advertencia visible de llamada de función vive en el intérprete.

        Aquí solo se recorre el árbol para no duplicar emisiones (validador +
        intérprete) ante el mismo evento de usuario.
        """
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
