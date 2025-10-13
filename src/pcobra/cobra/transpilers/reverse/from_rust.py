# -*- coding: utf-8 -*-
"""Transpilador inverso desde Rust a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Rust a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from pcobra.cobra.transpilers.reverse.from_rust import ReverseFromRust
    >>> transpiler = ReverseFromRust()
    >>> ast = transpiler.generate_ast("fn main() { println!(\"Hello\"); }")
"""
from typing import Any, List

from pcobra.cobra.core.ast_nodes import (
    NodoBloque,
    NodoFuncion,
    NodoIdentificador,
)
from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromRust(TreeSitterReverseTranspiler):
    """Transpilador inverso de Rust a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Rust en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "rust"

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código Rust.
        
        Args:
            code: Código fuente en Rust
            
        Returns:
            List[Any]: Lista de nodos AST de Cobra
            
        Raises:
            ValueError: Si el código Rust es inválido
            NotImplementedError: Si se encuentra una construcción no soportada
        """
        try:
            return super().generate_ast(code)
        except Exception as e:
            raise ValueError(f"Error procesando código Rust: {str(e)}") from e