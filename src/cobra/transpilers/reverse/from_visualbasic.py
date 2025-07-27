# -*- coding: utf-8 -*-
"""Transpilador inverso desde VisualBasic a Cobra (no soportado)."""

from cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromVisualBasic(BaseReverseTranspiler):
    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para VisualBasic")
