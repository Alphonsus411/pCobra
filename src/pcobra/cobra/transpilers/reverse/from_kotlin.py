# -*- coding: utf-8 -*-
"""Transpilador inverso desde Kotlin a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Kotlin a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from pcobra.cobra.transpilers.reverse.from_kotlin import ReverseFromKotlin
    >>> transpiler = ReverseFromKotlin()
    >>> ast = transpiler.generate_ast("fun main() { return }")

Nota:
    Requiere que el parser tree-sitter para Kotlin esté instalado y configurado.
"""

from pcobra.cobra.core.ast_nodes import (
    NodoBloque,
    NodoDeclaracion,
    NodoExpresion,
    NodoFuncion
)
from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromKotlin(TreeSitterReverseTranspiler):
    """Transpilador inverso de Kotlin a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Kotlin en nodos AST de Cobra,
    manteniendo la semántica del código original.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "kotlin"