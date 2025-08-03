# -*- coding: utf-8 -*-
"""Transpilador inverso desde Java a Cobra usando tree-sitter."""
from typing import Any, List

from core.ast_nodes import (
    NodoClase,
    NodoFuncion,
    NodoIdentificador,
    NodoMetodo
)
from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromJava(TreeSitterReverseTranspiler):
    """Transpilador inverso de Java a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Java en nodos AST de Cobra,
    manteniendo la semántica del código original.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE: str = "java"