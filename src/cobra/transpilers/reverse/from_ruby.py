# -*- coding: utf-8 -*-
"""Transpilador inverso desde Ruby a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Ruby a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from cobra.transpilers.reverse.from_ruby import ReverseFromRuby
    >>> transpiler = ReverseFromRuby()
    >>> ast = transpiler.generate_ast("def hello; puts 'world'; end")
"""
from typing import Any, List
from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromRuby(TreeSitterReverseTranspiler):
    """Transpilador inverso de Ruby a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Ruby en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "ruby"
    
    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código Ruby.
        
        Args:
            code: Código fuente en Ruby
            
        Returns:
            List[Any]: Lista de nodos AST de Cobra
            
        Raises:
            ValueError: Si el código Ruby es inválido
        """
        try:
            return super().generate_ast(code)
        except Exception as e:
            raise ValueError(f"Error procesando código Ruby: {str(e)}") from e