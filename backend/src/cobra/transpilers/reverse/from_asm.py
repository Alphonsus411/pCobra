# -*- coding: utf-8 -*-
"""Transpilador inverso desde ensamblador a Cobra (no soportado)."""

from src.cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromASM(BaseReverseTranspiler):
    """Placeholder sin implementación por falta de gramática."""

    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para ensamblador")
