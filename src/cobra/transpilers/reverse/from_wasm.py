# -*- coding: utf-8 -*-
"""Transpilador inverso desde WebAssembly a Cobra (no soportado)."""

from cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromWasm(BaseReverseTranspiler):
    def generate_ast(self, code: str):
        raise NotImplementedError("No hay parser para WebAssembly")
