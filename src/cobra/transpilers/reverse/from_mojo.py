# -*- coding: utf-8 -*-
"""Transpilador inverso desde Mojo a Cobra (no soportado)."""

from cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromMojo(BaseReverseTranspiler):
    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para Mojo")
