import os
from core.semantic_validators.base import ValidadorBase
from core.ast_nodes import NodoImport
from core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError


class ValidadorImportSeguro(ValidadorBase):
    """Valida que las instrucciones import sean seguras."""

    def visit_import(self, nodo: NodoImport):
        from core.interpreter import MODULES_PATH, IMPORT_WHITELIST

        ruta = os.path.abspath(nodo.ruta)
        if not ruta.startswith(MODULES_PATH) and ruta not in IMPORT_WHITELIST:
            raise PrimitivaPeligrosaError(
                f"Importación de módulo no permitida: {nodo.ruta}"
            )
        self.generic_visit(nodo)
