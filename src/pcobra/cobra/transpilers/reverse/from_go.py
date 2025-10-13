# -*- coding: utf-8 -*-
"""Transpilador inverso desde Go a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Go a nodos AST de Cobra
utilizando el parser tree-sitter. 

Soporta las principales construcciones del lenguaje Go incluyendo:
- Declaraciones de funciones y métodos
- Estructuras y tipos
- Goroutines y canales
- Interfaces
- Manejo de paquetes

Ejemplos:
    >>> from pcobra.cobra.transpilers.reverse.from_go import ReverseFromGo
    >>> transpiler = ReverseFromGo()
    >>> ast = transpiler.generate_ast("func main() { return }")

Nota:
    Requiere que el parser tree-sitter para Go esté instalado y configurado.
"""

from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromGo(TreeSitterReverseTranspiler):
    """Transpilador inverso de Go a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Go en nodos AST de Cobra,
    manteniendo la semántica del código original.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "go"