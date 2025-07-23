# -*- coding: utf-8 -*-
"""Transpilador inverso desde LaTeX a Cobra (no soportado)."""

from src.cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromLatex(BaseReverseTranspiler):
    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para LaTeX")
