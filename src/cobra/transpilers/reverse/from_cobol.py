# -*- coding: utf-8 -*-
"""Transpilador inverso desde COBOL a Cobra (no soportado)."""
from typing import List, Any
from cobra.transpilers.reverse.base import BaseReverseTranspiler

class ReverseFromCOBOL(BaseReverseTranspiler):
    """Transpilador inverso de COBOL a Cobra.
    
    Esta implementación actualmente no está soportada.
    """
    
    def __init__(self) -> None:
        super().__init__()
        
    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra equivalente al código fuente COBOL.
        
        Args:
            code: Código fuente en COBOL
            
        Returns:
            Lista de nodos AST de Cobra
            
        Raises:
            NotImplementedError: La funcionalidad no está implementada actualmente
        """
        raise NotImplementedError(
            "La conversión desde COBOL no está soportada en esta versión"
        )