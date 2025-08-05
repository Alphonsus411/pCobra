# -*- coding: utf-8 -*-
"""Transpilador inverso desde Swift a Cobra usando tree-sitter.

Este módulo implementa la conversión de código Swift a nodos AST de Cobra
utilizando el parser tree-sitter.

Ejemplos:
    >>> from cobra.transpilers.reverse.from_swift import ReverseFromSwift
    >>> transpiler = ReverseFromSwift()
    >>> ast = transpiler.generate_ast("func hello() { print('Hello') }")
"""
import re
from typing import Any, List

from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoValor,
)

from .tree_sitter_base import TreeSitterReverseTranspiler, TreeSitterNode
from .base import BaseReverseTranspiler  # type: ignore


class ReverseFromSwift(TreeSitterReverseTranspiler):
    """Transpilador inverso de Swift a Cobra usando tree-sitter.

    Este transpilador convierte código fuente Swift en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.

    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter ("swift")
    """

    LANGUAGE = "swift"

    def __init__(self) -> None:
        try:
            super().__init__()
            self._has_parser = True
        except Exception:
            # Fallback cuando tree-sitter no está disponible
            BaseReverseTranspiler.__init__(self)
            self.parser = None  # type: ignore[assignment]
            self._has_parser = False

    def generate_ast(self, code: str) -> List[Any]:  # type: ignore[override]
        if self._has_parser and self.parser is not None:
            return super().generate_ast(code)
        return self._naive_parse(code)

    def _naive_parse(self, code: str) -> List[Any]:
        """Parser simplificado usado si tree-sitter no está disponible."""
        ast: List[Any] = []
        func_match = re.search(r"func\s+(\w+)\s*\([^)]*\)\s*{([^}]*)}", code, re.S)
        if func_match:
            nombre = func_match.group(1)
            cuerpo_codigo = func_match.group(2)
            cuerpo: List[Any] = []
            call_match = re.search(r"(\w+)\s*\(([^)]*)\)", cuerpo_codigo.strip())
            if call_match:
                nombre_llamada = call_match.group(1)
                argumento = call_match.group(2).strip().strip('"')
                cuerpo.append(NodoLlamadaFuncion(nombre_llamada, [NodoValor(argumento)]))
            ast.append(NodoFuncion(nombre, [], cuerpo))
        return ast

    # ------------------------------------------------------------------
    # Declaraciones
    def visit_function_declaration(self, node: Any) -> NodoFuncion:
        """Procesa una declaración de función de Swift."""

        # Nombre de la función
        head = node.child_by_field_name("name") or None
        if head is None:
            # algunos árboles tienen el identificador como hijo directo
            for child in node.children:
                if child.type == "identifier":
                    head = child
                    break
        nombre = TreeSitterNode(head).get_text() if head else ""

        # Parámetros
        parametros: List[str] = []
        firma = node.child_by_field_name("signature")
        if firma is None:
            # buscar un posible nodo de lista de parámetros
            for child in node.children:
                if child.type in {"parameter_list", "parameter_clause"}:
                    firma = child
                    break
        if firma:
            param_list = firma.child_by_field_name("parameters")
            if param_list is None:
                # algunos árboles tienen el nodo directamente
                param_list = next(
                    (c for c in firma.children if c.type in {"parameter_list", "tuple"}),
                    None,
                )
            if param_list:
                for param in param_list.children:
                    if param.type in {"parameter", "parameter_declaration", "identifier"}:
                        name_n = param.child_by_field_name("name") or param.child_by_field_name("parameter")
                        if name_n is None:
                            name_n = next(
                                (c for c in param.children if c.type == "identifier"),
                                None,
                            )
                        if name_n:
                            parametros.append(TreeSitterNode(name_n).get_text())

        # Cuerpo de la función
        cuerpo: List[Any] = []
        body = node.child_by_field_name("body")
        if body is None:
            body = next((c for c in node.children if c.type in {"code_block", "block"}), None)
        if body:
            cuerpo = [self.visit(c) for c in body.children if c.is_named]

        return NodoFuncion(nombre, parametros, cuerpo)

    def visit_variable_declaration(self, node: Any) -> NodoAsignacion:
        """Procesa una declaración de variable ``var``."""

        nombre_n = node.child_by_field_name("name")
        if nombre_n is None:
            nombre_n = next((c for c in node.children if c.type == "identifier"), None)

        valor_n = node.child_by_field_name("value")
        if valor_n is None:
            # buscar el primer hijo después del signo '='
            children = list(node.children)
            for i, ch in enumerate(children):
                if ch.type == "=" and i + 1 < len(children):
                    valor_n = next((c for c in children[i + 1:] if c.is_named), None)
                    break

        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""
        valor = self.visit(valor_n) if valor_n else NodoValor(None)

        return NodoAsignacion(nombre, valor, inferencia=True)

    def visit_call_expression(self, node: Any) -> NodoLlamadaFuncion:
        """Procesa una llamada a función."""

        nombre_n = node.child_by_field_name("function")
        if nombre_n is None:
            nombre_n = next((c for c in node.children if c.type == "identifier"), None)
        nombre = TreeSitterNode(nombre_n).get_text() if nombre_n else ""

        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            args_node = next(
                (c for c in node.children if c.type in {"argument_list", "tuple", "arguments"}),
                None,
            )

        argumentos: List[Any] = []
        if args_node:
            argumentos = [self.visit(c) for c in args_node.children if c.is_named]

        return NodoLlamadaFuncion(nombre, argumentos)
