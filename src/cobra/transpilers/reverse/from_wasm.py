# -*- coding: utf-8 -*-
"""Transpilador inverso desde VisualBasic a Cobra (no soportado)."""
from typing import List, Any
from cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromVisualBasic(BaseReverseTranspiler):
    """Transpilador inverso de VisualBasic a Cobra.

    Esta clase actualmente no está implementada ya que no hay un parser
    disponible para código VisualBasic.
    """

    def __init__(self) -> None:
        """Inicializa el transpilador."""
        super().__init__()

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código VisualBasic.

        Args:
            code: Código fuente en VisualBasic

        Returns:
            List[Any]: Lista de nodos AST de Cobra

        Raises:
            NotImplementedError: Esta funcionalidad no está implementada actualmente
        """
        raise NotImplementedError(
            "La transpilación desde VisualBasic no está implementada. "
            "Se requiere un parser compatible para procesar código VisualBasic."
        )
