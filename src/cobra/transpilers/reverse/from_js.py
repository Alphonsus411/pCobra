# -*- coding: utf-8 -*-
"""Transpilador inverso desde JavaScript a Cobra usando tree-sitter.

Este módulo implementa la conversión de código JavaScript a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from cobra.transpilers.reverse.from_js import ReverseFromJS
    >>> transpiler = ReverseFromJS()
    >>> ast = transpiler.generate_ast("function main() { return 0; }")
"""
from typing import List

from tree_sitter import Node

from cobra.lexico.lexer import Token, TipoToken
from core.ast_nodes import (
    NodoClase,
    NodoFuncion,
    NodoMetodo,
    NodoBucleMientras,
    NodoOperacionBinaria,
    NodoIdentificador,
    NodoRetorno,
    NodoValor,
)

from .tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode


class ReverseFromJS(TreeSitterReverseTranspiler):
    """Transpilador inverso de JavaScript a Cobra usando tree-sitter."""

    LANGUAGE = "javascript"

    OPERADORES = {
        "+": Token(TipoToken.SUMA, "+"),
        "-": Token(TipoToken.RESTA, "-"),
        "*": Token(TipoToken.MULT, "*"),
        "/": Token(TipoToken.DIV, "/"),
        "==": Token(TipoToken.IGUAL, "=="),
        "!=": Token(TipoToken.DIFERENTE, "!="),
        "<": Token(TipoToken.MENORQUE, "<"),
        ">": Token(TipoToken.MAYORQUE, ">"),
        "<=": Token(TipoToken.MENORIGUAL, "<="),
        ">=": Token(TipoToken.MAYORIGUAL, ">="),
    }

    # ------------------------------------------------------------------
    # Definiciones
    def visit_function_declaration(self, node: Node) -> NodoFuncion:
        """Convierte una declaración de función."""
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

        return NodoFuncion(nombre, params, cuerpo)

    def visit_class_declaration(self, node: Node) -> NodoClase:
        """Convierte una declaración de clase."""
        nombre_n = node.child_by_field_name("name")
        body_n = node.child_by_field_name("body")

        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
        metodos = [
            self.visit(c)
            for c in body_n.children
            if c.is_named
        ] if body_n else []

        return NodoClase(nombre, metodos)

    def visit_method_definition(self, node: Node) -> NodoMetodo:
        """Convierte una definición de método."""
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

        return NodoMetodo(nombre, params, cuerpo)

    # ------------------------------------------------------------------
    # Bucles
    def visit_while_statement(self, node: Node) -> NodoBucleMientras:
        """Convierte un bucle while."""
        cond = self.visit(node.child_by_field_name("condition"))
        body_n = node.child_by_field_name("body")
        cuerpo = [
            self.visit(c)
            for c in body_n.children
            if c.is_named
        ] if body_n else []
        return NodoBucleMientras(cond, cuerpo)

    def visit_for_statement(self, node: Node) -> NodoBucleMientras:
        """Convierte un bucle for en un mientras simplificado."""
        cond = self.visit(node.child_by_field_name("condition"))
        body_n = node.child_by_field_name("body")
        cuerpo = [
            self.visit(c)
            for c in body_n.children
            if c.is_named
        ] if body_n else []
        return NodoBucleMientras(cond, cuerpo)

    # ------------------------------------------------------------------
    # Expresiones
    def visit_binary_expression(self, node: Node) -> NodoOperacionBinaria:
        """Convierte una expresión binaria."""
        izquierda = self.visit(node.children[0])
        derecha = self.visit(node.children[2])
        operador_txt = TreeSitterNode(node.children[1]).get_text()
        token = self.OPERADORES.get(operador_txt, Token(TipoToken.DIFERENTE, operador_txt))
        return NodoOperacionBinaria(izquierda, token, derecha)

    def visit_parenthesized_expression(self, node: Node) -> NodoValor:
        """Elimina paréntesis de una expresión."""
        expr = next((c for c in node.children if c.is_named), None)
        return self.visit(expr) if expr else NodoValor(None)

    def visit_return_statement(self, node: Node) -> NodoRetorno:  # type: ignore[override]
        """Convierte un return de JavaScript."""
        expr = next((c for c in node.children if c.is_named), None)
        return NodoRetorno(self.visit(expr) if expr else NodoValor(None))

    def visit_identifier(self, node: Node) -> NodoIdentificador:  # type: ignore[override]
        return super().visit_identifier(node)

    def visit_number(self, node: Node) -> NodoValor:  # type: ignore[override]
        return super().visit_number(node)

    def visit_string(self, node: Node) -> NodoValor:  # type: ignore[override]
        return super().visit_string(node)
