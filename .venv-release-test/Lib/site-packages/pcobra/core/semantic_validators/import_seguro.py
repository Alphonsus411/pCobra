import os
from .base import ValidadorBase
from ..ast_nodes import NodoImport
from .primitiva_peligrosa import PrimitivaPeligrosaError


class ValidadorImportSeguro(ValidadorBase):
    """Valida que las instrucciones import sean seguras."""

    def visit_import(self, nodo: NodoImport):
        from ..interpreter import _ruta_import_permitida

        if not _ruta_import_permitida(nodo.ruta):
            raise PrimitivaPeligrosaError(
                f"Importación de módulo no permitida: {nodo.ruta}"
            )
        self.generic_visit(nodo)
