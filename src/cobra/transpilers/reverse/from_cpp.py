# -*- coding: utf-8 -*-
"""Transpilador inverso desde C++ a Cobra usando tree-sitter."""

from typing import Any, List

import core.ast_nodes
from .tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode


class ReverseFromCPP(TreeSitterReverseTranspiler):
    """Transpilador inverso de C++ a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente C++ en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "cpp"
    # ------------------------------------------------------------------
    # Clases y namespaces
    def visit_class_definition(self, node: Any) -> core.ast_nodes.NodoClase:
        """Procesa una definición de clase C++."""
        nombre_n = node.child_by_field_name("name")
        body_n = node.child_by_field_name("body")
        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""

        miembros: List[Any] = []
        if body_n:
            for child in body_n.children:
                if child.is_named:
                    miembros.append(self.visit(child))

        return core.ast_nodes.NodoClase(nombre, miembros)

    # Alias para el nodo de tree-sitter `class_specifier`
    def visit_class_specifier(self, node: Any) -> core.ast_nodes.NodoClase:
        return self.visit_class_definition(node)

    def visit_field_declaration(self, node: Any) -> core.ast_nodes.NodoAsignacion:
        """Convierte una declaración de campo en una asignación simple."""
        declarator = node.child_by_field_name("declarator")
        nombre = TreeSitterNode(declarator).get_text() if declarator else ""
        return core.ast_nodes.NodoAsignacion(
            nombre, core.ast_nodes.NodoValor(None)
        )

    def visit_function_definition(self, node: Any) -> core.ast_nodes.NodoMetodo:
        """Procesa una definición de método dentro de una clase."""
        if node.parent and node.parent.type == "field_declaration_list":
            nombre_n = node.child_by_field_name("name")
            params_n = node.child_by_field_name("parameters")
            body_n = node.child_by_field_name("body")

            nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
            params = [
                TreeSitterNode(c).get_text()
                for c in params_n.children
                if c.type == "identifier"
            ] if params_n else []

            cuerpo = [
                self.visit(c)
                for c in body_n.children
                if c.is_named
            ] if body_n else []

            return core.ast_nodes.NodoMetodo(nombre, params, cuerpo)

        return super().visit_function_definition(node)

    def visit_namespace_definition(self, node: Any) -> core.ast_nodes.NodoBloque:
        """Procesa una definición de namespace."""
        body_n = node.child_by_field_name("body")
        sentencias: List[Any] = []
        if body_n:
            for child in body_n.children:
                if child.is_named:
                    sentencias.append(self.visit(child))

        bloque = core.ast_nodes.NodoBloque()
        bloque.sentencias = sentencias
        return bloque

    def visit_simple_declaration(self, node: Any) -> core.ast_nodes.NodoAsignacion:
        declarator = node.child_by_field_name("declarator")
        valor_n = node.child_by_field_name("value")
        nombre_n = declarator
        if declarator and declarator.type == "init_declarator":
            nombre_n = declarator.child_by_field_name("declarator")
            valor_n = declarator.child_by_field_name("value")
        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
        valor = self.visit(valor_n) if valor_n else core.ast_nodes.NodoValor(None)
        return core.ast_nodes.NodoAsignacion(nombre, valor)

    def visit_switch_statement(self, node: Any) -> core.ast_nodes.NodoSwitch:
        cond_n = node.child_by_field_name("condition")
        body_n = node.child_by_field_name("body")
        expr = self.visit(cond_n) if cond_n else core.ast_nodes.NodoValor(None)
        casos: List[core.ast_nodes.NodoCase] = []
        por_defecto: List[Any] = []
        if body_n:
            for child in body_n.children:
                if child.type == "case_statement":
                    val_n = child.child_by_field_name("value")
                    val = self.visit(val_n) if val_n else core.ast_nodes.NodoValor(None)
                    if not isinstance(val, core.ast_nodes.NodoPattern):
                        val = core.ast_nodes.NodoPattern(val)
                    cuerpo = [
                        self.visit(c)
                        for c in child.children
                        if c.is_named and c is not val_n
                    ]
                    casos.append(core.ast_nodes.NodoCase(val, cuerpo))
                elif child.type == "default_statement":
                    por_defecto = [self.visit(c) for c in child.children if c.is_named]
        return core.ast_nodes.NodoSwitch(expr, casos, por_defecto)

    def visit_identifier(self, node: Any) -> Any:  # type: ignore[override]
        text = TreeSitterNode(node).get_text()
        if text in {"nullptr", "NULL", "std::nullopt"}:
            return core.ast_nodes.NodoOption(None)
        return super().visit_identifier(node)
