# -*- coding: utf-8 -*-
"""Transpilador inverso desde JavaScript a Cobra usando tree-sitter.

Este módulo implementa la conversión de código JavaScript a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from pcobra.cobra.transpilers.reverse.from_js import ReverseFromJS
    >>> transpiler = ReverseFromJS()
    >>> ast = transpiler.generate_ast("function main() { return 0; }")
"""
from typing import Any, List

from tree_sitter import Node

from pcobra.cobra.core import Token, TipoToken
from pcobra.cobra.core.ast_nodes import (
    NodoClase,
    NodoFuncion,
    NodoMetodo,
    NodoBucleMientras,
    NodoOperacionBinaria,
    NodoIdentificador,
    NodoRetorno,
    NodoValor,
    NodoLista,
    NodoDiccionario,
    NodoListaTipo,
    NodoDiccionarioTipo,
    NodoAsignacion,
    NodoSwitch,
    NodoCase,
    NodoPattern,
    NodoOption,
)

from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode


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

    def visit_switch_statement(self, node: Node) -> NodoSwitch:
        """Convierte un switch de JavaScript."""
        expr_n = node.child_by_field_name("value")
        body_n = node.child_by_field_name("body")
        expr = self.visit(expr_n) if expr_n else NodoValor(None)
        casos: List[NodoCase] = []
        por_defecto: List[Any] = []
        if body_n:
            for child in body_n.children:
                if child.type == "switch_case":
                    val_n = child.child_by_field_name("value")
                    val = self.visit(val_n) if val_n else NodoValor(None)
                    if not isinstance(val, NodoPattern):
                        val = NodoPattern(val)
                    cuerpo = [
                        self.visit(c)
                        for c in child.children
                        if c.is_named and c is not val_n
                    ]
                    casos.append(NodoCase(val, cuerpo))
                elif child.type == "switch_default":
                    por_defecto = [self.visit(c) for c in child.children if c.is_named]
        return NodoSwitch(expr, casos, por_defecto)

    # ------------------------------------------------------------------
    # Expresiones
    def visit_array(self, node: Node) -> NodoLista:
        elementos = [self.visit(c) for c in node.children if c.is_named]
        return NodoLista(elementos)

    def visit_object(self, node: Node) -> NodoDiccionario:
        pares = []
        for child in node.children:
            if child.type == "pair":
                key = self.visit(child.child_by_field_name("key"))
                value = self.visit(child.child_by_field_name("value"))
                pares.append((key, value))
        return NodoDiccionario(pares)

    def visit_variable_declaration(self, node: Node) -> NodoAsignacion:
        declarator = next((c for c in node.children if c.type == "variable_declarator"), None)
        if declarator is None:
            return self.generic_visit(node)
        name_n = declarator.child_by_field_name("name")
        value_n = declarator.child_by_field_name("value")
        nombre = TreeSitterNode(name_n).get_text() if name_n else ""
        valor = self.visit(value_n) if value_n else NodoValor(None)
        if isinstance(valor, NodoLista):
            return NodoListaTipo(nombre, "Any", valor.elementos)
        if isinstance(valor, NodoDiccionario):
            return NodoDiccionarioTipo(nombre, "Any", "Any", valor.elementos)
        return NodoAsignacion(nombre, valor)

    def visit_assignment_expression(self, node: Node) -> NodoAsignacion:
        left_n = node.child_by_field_name("left")
        right_n = node.child_by_field_name("right")
        left = self.visit(left_n)
        right = self.visit(right_n) if right_n else NodoValor(None)
        if isinstance(left, NodoIdentificador):
            nombre = left.nombre
            if isinstance(right, NodoLista):
                return NodoListaTipo(nombre, "Any", right.elementos)
            if isinstance(right, NodoDiccionario):
                return NodoDiccionarioTipo(nombre, "Any", "Any", right.elementos)
            return NodoAsignacion(nombre, right)
        return NodoAsignacion(left, right)
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
        text = TreeSitterNode(node).get_text()
        if text == "undefined":
            return NodoOption(None)
        return super().visit_identifier(node)

    def visit_number(self, node: Node) -> NodoValor:  # type: ignore[override]
        return super().visit_number(node)

    def visit_null(self, node: Node) -> NodoOption:  # type: ignore[override]
        return NodoOption(None)

    def visit_string(self, node: Node) -> NodoValor:  # type: ignore[override]
        return super().visit_string(node)
