# -*- coding: utf-8 -*-
"""Transpilador inverso desde Julia a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Julia a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from cobra.transpilers.reverse.from_julia import ReverseFromJulia
    >>> transpiler = ReverseFromJulia()
    >>> ast = transpiler.generate_ast("function suma(x, y) return x + y end")

Nota:
    Requiere que el parser tree-sitter para Julia esté instalado y configurado.
"""

from cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler

class ReverseFromJulia(TreeSitterReverseTranspiler):
    """Transpilador inverso de Julia a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Julia en nodos AST de Cobra,
    manteniendo la semántica del código original.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "julia"