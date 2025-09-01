# -*- coding: utf-8 -*-
"""Transpilador inverso desde R a Cobra usando tree-sitter.

Este módulo implementa la conversión de código R a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from cobra.transpilers.reverse.from_r import ReverseFromR
    >>> transpiler = ReverseFromR()
    >>> ast = transpiler.generate_ast("x <- 5")
"""
from cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler

class ReverseFromR(TreeSitterReverseTranspiler):
    """Transpilador inverso de R a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente R en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "r"