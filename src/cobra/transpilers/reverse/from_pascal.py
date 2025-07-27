# -*- coding: utf-8 -*-
"""Transpilador inverso desde Pascal a Cobra (no soportado)."""

from cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromPascal(BaseReverseTranspiler):
    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para Pascal")
