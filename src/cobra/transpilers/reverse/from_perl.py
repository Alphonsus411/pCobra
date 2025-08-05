# -*- coding: utf-8 -*-
"""Transpilador inverso desde Perl a Cobra usando tree-sitter."""
from typing import Any, List

from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor
from .tree_sitter_base import TreeSitterNode, TreeSitterReverseTranspiler

class ReverseFromPerl(TreeSitterReverseTranspiler):
    """Transpilador inverso de Perl a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente Perl en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "perl"

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código Perl.

        Flattening de posibles listas de nodos producidas por las
        declaraciones múltiples.
        """
        ast_nodes = super().generate_ast(code)
        resultado: List[Any] = []
        for nodo in ast_nodes:
            if not nodo:
                continue
            if isinstance(nodo, list):
                resultado.extend(nodo)
            else:
                resultado.append(nodo)
        self.ast = resultado
        return resultado

    def visit_variable_declaration(self, node):
        """Procesa una declaración de variable Perl.

        Convierte declaraciones con ``my``, ``our`` o ``local`` en nodos
        ``NodoAsignacion`` de Cobra.
        """

        scope = node.children[0].text.decode() if node.children else ""
        if scope not in {"my", "our", "local"}:
            return self.generic_visit(node)

        declaracion = None
        for hijo in node.children:
            if hijo.type in {"single_var_declaration", "multi_var_declaration"}:
                declaracion = hijo
                break

        nombres: List[str] = []
        if declaracion is not None:
            if declaracion.type == "single_var_declaration":
                nombres.append(TreeSitterNode(declaracion).get_text().lstrip("$@%"))
            elif declaracion.type == "multi_var_declaration":
                for child in declaracion.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name")
                        if name_node is not None:
                            nombres.append(
                                TreeSitterNode(name_node).get_text().lstrip("$@%")
                            )

        def parse_value(nodo_valor):
            texto = TreeSitterNode(nodo_valor).get_text()
            if nodo_valor.type in {"integer", "number"}:
                try:
                    return NodoValor(int(texto))
                except ValueError:
                    return NodoValor(float(texto))
            if nodo_valor.type in {"float"}:
                return NodoValor(float(texto))
            if nodo_valor.type in {"string", "string_literal"}:
                return NodoValor(texto.strip("'\""))
            if nodo_valor.type in {"scalar_variable", "identifier"}:
                return NodoIdentificador(texto.lstrip("$@%"))
            return NodoValor(texto)

        valor_n = node.child_by_field_name("value")
        valores: List[Any] = []
        if valor_n is not None:
            if valor_n.type == "array":
                for child in valor_n.children:
                    if child.is_named:
                        valores.append(parse_value(child))
            else:
                valores.append(parse_value(valor_n))

        asignaciones = []
        for i, nombre in enumerate(nombres):
            valor = valores[i] if i < len(valores) else NodoValor(None)
            asignaciones.append(
                NodoAsignacion(NodoIdentificador(nombre), valor)
            )

        return asignaciones[0] if len(asignaciones) == 1 else asignaciones

    def visit_semi_colon(self, node):  # pragma: no cover - trivial
        """Ignora los puntos y coma explícitos."""
        return None
