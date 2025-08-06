# -*- coding: utf-8 -*-
"""Transpilador inverso desde Fortran a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Fortran a nodos AST de Cobra
utilizando el parser tree-sitter.
"""

from typing import Any, List

from .tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoIdentificador,
    NodoModulo,
    NodoValor,
    NodoDeclaracion,
)

class ReverseFromFortran(TreeSitterReverseTranspiler):
    """Transpilador inverso de Fortran a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Fortran en nodos AST de Cobra,
    manteniendo la semántica del código original.
    """
    
    LANGUAGE = "fortran"

    def visit_program(self, node: Any) -> NodoModulo:
        """Procesa un ``program`` de Fortran."""
        # El primer hijo es ``program_statement`` con el nombre
        stmt = node.children[0] if node.children else None
        nombre = ""
        if stmt:
            for c in stmt.children:
                if c.type == "name":
                    nombre = TreeSitterNode(c).get_text()
                    break

        # El cuerpo está compuesto por los nodos intermedios
        cuerpo = [
            self.visit(c)
            for c in node.children[1:-1]
            if c.is_named
        ]

        modulo = NodoModulo()
        modulo.nombre = nombre
        modulo.cuerpo = cuerpo
        return modulo

    def visit_subroutine(self, node: Any) -> NodoFuncion:
        """Procesa una ``subroutine`` de Fortran."""
        stmt = node.children[0] if node.children else None
        nombre_n = stmt.child_by_field_name("name") if stmt else None
        params_n = stmt.child_by_field_name("parameters") if stmt else None

        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
        parametros = [
            TreeSitterNode(c).get_text()
            for c in (params_n.children if params_n else [])
            if c.is_named
        ]

        cuerpo = [
            self.visit(c)
            for c in node.children[1:-1]
            if c.is_named
        ]

        return NodoFuncion(nombre, parametros, cuerpo)

    def visit_variable_declaration(self, node: Any) -> NodoDeclaracion:
        """Procesa una declaración simple de variable."""
        tipo = TreeSitterNode(node.children[0]).get_text() if node.children else ""
        nombre = (
            TreeSitterNode(node.children[-1]).get_text() if len(node.children) > 2 else ""
        )

        decl = NodoDeclaracion()
        decl.nombre = nombre
        decl.tipo = tipo
        return decl

    # Alias para cumplir con la API solicitada
    visit_declaration = visit_variable_declaration

    # Nodos básicos ---------------------------------------------------
    def visit_assignment_statement(self, node: Any) -> NodoAsignacion:
        """Convierte una asignación ``a = b``."""
        left = self.visit(node.child_by_field_name("left"))
        right = self.visit(node.child_by_field_name("right"))
        return NodoAsignacion(left, right)

    def visit_number_literal(self, node: Any) -> NodoValor:
        """Convierte un literal numérico."""
        return self.visit_number(node)

    def visit_identifier(self, node: Any) -> NodoIdentificador:
        """Alias explícito para identificadores."""
        return super().visit_identifier(node)
