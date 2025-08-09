# -*- coding: utf-8 -*-
"""Transpilador inverso desde Java a Cobra usando tree-sitter."""
from typing import List

from tree_sitter import Node

from cobra.core import Token, TipoToken
from core.ast_nodes import (
    NodoClase,
    NodoMetodo,
    NodoBucleMientras,
    NodoOperacionBinaria,
    NodoIdentificador,
    NodoRetorno,
    NodoValor,
    NodoCondicional,
)

from .tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode


class ReverseFromJava(TreeSitterReverseTranspiler):
    """Transpilador inverso de Java a Cobra usando tree-sitter."""

    LANGUAGE: str = "java"

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

    def visit_method_declaration(self, node: Node) -> NodoMetodo:
        """Convierte una declaración de método."""
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
        izquierda = self.visit(node.child_by_field_name("left"))
        derecha = self.visit(node.child_by_field_name("right"))
        operador_txt = TreeSitterNode(node.children[1]).get_text()
        token = self.OPERADORES.get(operador_txt, Token(TipoToken.DIFERENTE, operador_txt))
        return NodoOperacionBinaria(izquierda, token, derecha)

    def visit_condition(self, node: Node):
        """Procesa un nodo condición envolviendo una expresión."""
        expr = next((c for c in node.children if c.is_named), None)
        return self.visit(expr) if expr else None

    def visit_parenthesized_expression(self, node: Node):
        """Elimina paréntesis de la expresión contenida."""
        expr = next((c for c in node.children if c.is_named), None)
        return self.visit(expr) if expr else None

    def visit_identifier(self, node: Node) -> NodoIdentificador:  # type: ignore[override]
        return super().visit_identifier(node)

    def visit_number(self, node: Node) -> NodoValor:  # type: ignore[override]
        return super().visit_number(node)

    def visit_string(self, node: Node) -> NodoValor:  # type: ignore[override]
        return super().visit_string(node)

    def visit_return_statement(self, node: Node) -> NodoRetorno:  # type: ignore[override]
        return super().visit_return_statement(node)

    def visit_if_statement(self, node: Node) -> NodoCondicional:  # type: ignore[override]
        return super().visit_if_statement(node)
