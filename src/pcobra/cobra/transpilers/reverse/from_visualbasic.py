# -*- coding: utf-8 -*-
"""Transpilador inverso desde VisualBasic a Cobra usando tree-sitter."""

from __future__ import annotations

import re
from typing import Any, List

from pcobra.cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoValor,
)
from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode
from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler  # type: ignore


def _parse_expression(texto: str) -> Any:
    """Convierte una expresión textual en un nodo del AST de Cobra."""
    text = texto.strip()
    if text.startswith(("'", '"')) and text.endswith(("'", '"')):
        return NodoValor(text[1:-1])
    try:
        return NodoValor(int(text))
    except ValueError:
        try:
            return NodoValor(float(text))
        except ValueError:
            return NodoIdentificador(text)


class ReverseFromVisualBasic(TreeSitterReverseTranspiler):
    """Transpilador inverso de VisualBasic a Cobra."""

    LANGUAGE = "vbscript"

    def __init__(self) -> None:
        try:
            super().__init__()
            self._has_parser = True
        except Exception:
            BaseReverseTranspiler.__init__(self)
            self.parser = None  # type: ignore[assignment]
            self._has_parser = False

    # ------------------------------------------------------------------
    # Entrada
    def generate_ast(self, code: str) -> List[Any]:  # type: ignore[override]
        if self._has_parser and self.parser is not None:
            return super().generate_ast(code)
        return self._naive_parse(code)

    def _naive_parse(self, code: str) -> List[Any]:
        ast: List[Any] = []
        func_re = re.compile(
            r"(?is)(?:Function|Sub)\s+([A-Za-z_][\w]*)\s*\(([^)]*)\)\s*(?:As\s+\w+)?\s*\n(.*?)\nEnd\s+(?:Function|Sub)"
        )
        last_end = 0
        for match in func_re.finditer(code):
            nombre, params_txt, cuerpo_txt = match.groups()
            params = [
                p.strip().split()[-1]
                for p in params_txt.split(",")
                if p.strip()
            ]
            cuerpo: List[Any] = []
            for raw in cuerpo_txt.splitlines():
                line = raw.strip()
                if not line or line.startswith("'"):
                    continue
                m_assign = re.match(
                    r"(?:Dim\s+)?([A-Za-z_][\w]*)\s*(?:As\s+\w+)?\s*=\s*(.+)",
                    line,
                    re.IGNORECASE,
                )
                if m_assign:
                    var, expr = m_assign.groups()
                    cuerpo.append(
                        NodoAsignacion(NodoIdentificador(var), _parse_expression(expr))
                    )
                    continue
                m_call = re.match(r"([A-Za-z_][\w]*)\s*\((.*)\)", line)
                if m_call:
                    nombre_llamada, args_txt = m_call.groups()
                    args = [
                        _parse_expression(a.strip())
                        for a in args_txt.split(",")
                        if a.strip()
                    ]
                    cuerpo.append(NodoLlamadaFuncion(nombre_llamada, args))
                    continue
            ast.append(NodoFuncion(nombre, params, cuerpo))
            last_end = match.end()

        for raw in code[last_end:].splitlines():
            line = raw.strip()
            if not line or line.startswith("'"):
                continue
            m_assign = re.match(
                r"(?:Dim\s+)?([A-Za-z_][\w]*)\s*(?:As\s+\w+)?\s*=\s*(.+)",
                line,
                re.IGNORECASE,
            )
            if m_assign:
                var, expr = m_assign.groups()
                ast.append(
                    NodoAsignacion(NodoIdentificador(var), _parse_expression(expr))
                )
        self.ast = ast
        return ast

    # ------------------------------------------------------------------
    # Nodos tree-sitter (cuando está disponible)
    def visit_function(self, node: Any) -> NodoFuncion:
        nombre = ""
        params: List[str] = []
        body = None
        for child in node.children:
            if child.type == "new_identifier":
                nombre = TreeSitterNode(child).get_text()
            elif child.type == "parameter_list":
                for p in child.children:
                    if p.type in {"identifier", "new_identifier"}:
                        params.append(TreeSitterNode(p).get_text())
                    elif p.type == "parameter":
                        idn = next(
                            (c for c in p.children if c.type in {"identifier", "new_identifier"}),
                            None,
                        )
                        if idn:
                            params.append(TreeSitterNode(idn).get_text())
            elif child.type in {"_inline_statement_block", "block"}:
                body = child
        cuerpo = [
            self.visit(c)
            for c in body.children
            if c.is_named
        ] if body else []
        return NodoFuncion(nombre, params, cuerpo)

    def visit_subroutine(self, node: Any) -> NodoFuncion:
        return self.visit_function(node)

    def visit_variable_assignment(self, node: Any) -> NodoAsignacion:
        izquierdo = self.visit(node.children[0])
        derecho = self.visit(node.children[-1])
        return NodoAsignacion(izquierdo, derecho)

    def visit_variable_declaration(self, node: Any) -> Any:
        asign = next(
            (c for c in node.children if c.type == "_variable_declaration_assignment"),
            None,
        )
        return self.visit(asign) if asign else None

    def visit__variable_declaration_assignment(self, node: Any) -> NodoAsignacion:
        nombre_n = next(
            (c for c in node.children if c.type in {"variable_declaration_identifier", "identifier", "new_identifier"}),
            None,
        )
        valor_n = node.children[-1]
        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
        valor = self.visit(valor_n)
        return NodoAsignacion(NodoIdentificador(nombre), valor)

    def visit_function_call(self, node: Any) -> NodoLlamadaFuncion:
        nombre_n = node.child_by_field_name("function")
        if nombre_n is None:
            nombre_n = next((c for c in node.children if c.type == "identifier"), None)
        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
        args_n = node.child_by_field_name("arguments")
        argumentos = [
            self.visit(c)
            for c in args_n.children
            if c.is_named
        ] if args_n else []
        return NodoLlamadaFuncion(nombre, argumentos)

    def visit_invocation_statement(self, node: Any) -> NodoLlamadaFuncion:
        call = next((c for c in node.children if c.type == "function_call"), None)
        if call:
            return self.visit_function_call(call)
        nombre = TreeSitterNode(node.children[0]).get_text()
        args = [self.visit(c) for c in node.children[1:] if c.is_named]
        return NodoLlamadaFuncion(nombre, args)
