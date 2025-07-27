# -*- coding: utf-8 -*-
"""Transpilador inverso desde Matlab a Cobra (no soportado)."""

from cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromMatlab(BaseReverseTranspiler):
    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para Matlab")
