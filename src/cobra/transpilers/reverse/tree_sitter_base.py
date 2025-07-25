# -*- coding: utf-8 -*-
"""Transpiladores inversos basados en tree-sitter."""

from __future__ import annotations

from tree_sitter_languages import get_parser

from src.cobra.transpilers.reverse.base import BaseReverseTranspiler
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoRetorno,
    NodoIdentificador,
    NodoValor,
)


class TreeSitterReverseTranspiler(BaseReverseTranspiler):
    """Convierte código de varios lenguajes a nodos Cobra usando tree-sitter."""

    LANGUAGE: str = ""

    def __init__(self):
        super().__init__()
        if not self.LANGUAGE:
            raise ValueError("LANGUAGE debe definirse en la subclase")
        try:
            self.parser = get_parser(self.LANGUAGE)
        except Exception as exc:  # pylint: disable=broad-except
            raise NotImplementedError(
                f"No hay gramática tree-sitter para {self.LANGUAGE}"
            ) from exc

    def generate_ast(self, code: str):
        tree = self.parser.parse(code.encode("utf-8"))
        self.ast = [self.visit(child) for child in tree.root_node.children if child.is_named]
        return self.ast

    # Visitas genéricas -------------------------------------------------
    def visit(self, node):  # type: ignore[override]
        method = getattr(self, f"visit_{node.type}", None)
        if method is None:
            return self.generic_visit(node)
        return method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Nodo no soportado: {node.type}")

    # Nodos simples -----------------------------------------------------
    def visit_identifier(self, node):
        return NodoIdentificador(node.text.decode())

    def visit_number(self, node):
        texto = node.text.decode()
        try:
            valor = int(texto)
        except ValueError:
            try:
                valor = float(texto)
            except ValueError:
                valor = texto
        return NodoValor(valor)

    def visit_string(self, node):
        texto = node.text.decode().strip('"\'')
        return NodoValor(texto)

    # Expresiones -------------------------------------------------------
    def visit_call_expression(self, node):
        nombre = node.child_by_field_name("function")
        args = node.child_by_field_name("arguments")
        nombre_txt = nombre.text.decode() if nombre else ""
        argumentos = []
        if args:
            for child in args.children:
                if child.is_named:
                    argumentos.append(self.visit(child))
        return NodoLlamadaFuncion(nombre_txt, argumentos)

    # Sentencias -------------------------------------------------------
    def visit_assignment_expression(self, node):
        izquierdo = self.visit(node.child_by_field_name("left"))
        derecho = self.visit(node.child_by_field_name("right"))
        return NodoAsignacion(izquierdo, derecho)

    def visit_expression_statement(self, node):
        expr = node.child_by_field_name("expression") or node.children[0]
        return self.visit(expr)

    def visit_return_statement(self, node):
        valor = node.child_by_field_name("argument")
        return NodoRetorno(self.visit(valor) if valor else NodoValor(None))

    def visit_if_statement(self, node):
        cond = self.visit(node.child_by_field_name("condition"))
        conseq = node.child_by_field_name("consequence")
        alt = node.child_by_field_name("alternative")
        bloque_si = [self.visit(c) for c in conseq.children if c.is_named] if conseq else []
        bloque_sino = [self.visit(c) for c in alt.children if c.is_named] if alt else []
        return NodoCondicional(cond, bloque_si, bloque_sino)

    def visit_function_definition(self, node):
        nombre_n = node.child_by_field_name("name")
        params_n = node.child_by_field_name("parameters")
        body_n = node.child_by_field_name("body")
        nombre = nombre_n.text.decode() if nombre_n else ""
        params = [c.text.decode() for c in params_n.children if c.type == "identifier"] if params_n else []
        cuerpo = [self.visit(c) for c in body_n.children if c.is_named] if body_n else []
        return NodoFuncion(nombre, params, cuerpo)
