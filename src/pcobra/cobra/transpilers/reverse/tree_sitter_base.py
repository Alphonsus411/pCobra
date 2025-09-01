# -*- coding: utf-8 -*-
"""Transpiladores inversos basados en tree-sitter."""
from __future__ import annotations
from typing import Any, List, Optional, Union
import logging
from dataclasses import dataclass
from tree_sitter import Node, Tree
from tree_sitter_languages import get_parser
try:  # Compatibilidad con versiones antiguas
    from tree_sitter_languages import TreeSitterLanguageError as TreeSitterError  # type: ignore
except Exception:  # pragma: no cover - dependencia opcional
    class TreeSitterError(Exception):
        """Excepción genérica para errores de tree-sitter."""
        pass

from cobra.transpilers.reverse.base import BaseReverseTranspiler
from cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
    NodoRetorno,
    NodoIdentificador,
    NodoValor,
)

# Configuración del logging
logger = logging.getLogger(__name__)

# Constantes
COMILLAS_SIMPLES = "'"
COMILLAS_DOBLES = '"'
CODIFICACION = "utf-8"


@dataclass
class TreeSitterNode:
    """Wrapper para nodos de tree-sitter con validación."""
    node: Node

    def get_text(self) -> str:
        """Obtiene el texto del nodo de forma segura."""
        if hasattr(self.node, 'text'):
            try:
                return self.node.text.decode(CODIFICACION)
            except UnicodeDecodeError as e:
                logger.error(f"Error decodificando texto del nodo: {e}")
                return ""
        return ""


class TreeSitterReverseTranspiler(BaseReverseTranspiler):
    """Convierte código de varios lenguajes a nodos Cobra usando tree-sitter."""

    LANGUAGE: str = ""

    def __init__(self) -> None:
        """Inicializa el transpilador."""
        super().__init__()
        if not self.LANGUAGE:
            raise ValueError("LANGUAGE debe definirse en la subclase")
        try:
            self.parser = get_parser(self.LANGUAGE)
        except Exception as exc:
            raise NotImplementedError(
                f"No hay gramática tree-sitter para {self.LANGUAGE}"
            ) from exc

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST a partir del código fuente.

        Args:
            code: Código fuente a procesar

        Returns:
            Lista de nodos del AST

        Raises:
            ValueError: Si el código está vacío o es inválido
        """
        if not code:
            raise ValueError("El código fuente no puede estar vacío")

        try:
            encoded_code = code.encode(CODIFICACION)
            tree = self.parser.parse(encoded_code)
            self.ast = [
                self.visit(child)
                for child in tree.root_node.children
                if child.is_named
            ]
            return self.ast
        except UnicodeEncodeError as e:
            raise ValueError(f"Error codificando el código fuente: {e}") from e

    def visit(self, node: Node) -> Any:
        """Visita un nodo del AST.

        Args:
            node: Nodo a visitar

        Returns:
            Nodo del AST de Cobra correspondiente
        """
        if not node:
            return None

        method = getattr(self, f"visit_{node.type}", None)
        if method is None:
            return self.generic_visit(node)
        return method(node)

    def generic_visit(self, node: Node) -> Any:
        """Manejo genérico de nodos no soportados.

        Args:
            node: Nodo no soportado

        Raises:
            NotImplementedError: Siempre, indicando el tipo de nodo no soportado
        """
        raise NotImplementedError(f"Nodo no soportado: {node.type}")

    def visit_identifier(self, node: Node) -> NodoIdentificador:
        """Procesa un identificador.

        Args:
            node: Nodo identificador

        Returns:
            NodoIdentificador correspondiente
        """
        return NodoIdentificador(TreeSitterNode(node).get_text())

    def visit_number(self, node: Node) -> NodoValor:
        """Procesa un número literal.

        Args:
            node: Nodo número

        Returns:
            NodoValor con el valor numérico correspondiente
        """
        texto = TreeSitterNode(node).get_text()
        try:
            return NodoValor(int(texto))
        except ValueError:
            try:
                return NodoValor(float(texto))
            except ValueError:
                logger.warning(f"No se pudo convertir el número: {texto}")
                return NodoValor(texto)

    def visit_string(self, node: Node) -> NodoValor:
        """Procesa una cadena literal.

        Args:
            node: Nodo cadena

        Returns:
            NodoValor con la cadena procesada
        """
        texto = TreeSitterNode(node).get_text()
        return NodoValor(texto.strip(COMILLAS_SIMPLES + COMILLAS_DOBLES))

    def visit_call_expression(self, node: Node) -> NodoLlamadaFuncion:
        """Procesa una llamada a función.

        Args:
            node: Nodo de llamada a función

        Returns:
            NodoLlamadaFuncion correspondiente
        """
        nombre = node.child_by_field_name("function")
        args = node.child_by_field_name("arguments")

        nombre_txt = TreeSitterNode(nombre).get_text() if nombre else ""
        argumentos = []

        if args:
            argumentos = [
                self.visit(child)
                for child in args.children
                if child.is_named
            ]

        if nombre_txt == "proyectar":
            hb = argumentos[0] if argumentos else NodoValor(None)
            modo = argumentos[1] if len(argumentos) > 1 else NodoValor(None)
            return NodoProyectar(hb, modo)
        if nombre_txt == "transformar":
            hb = argumentos[0] if argumentos else NodoValor(None)
            oper = argumentos[1] if len(argumentos) > 1 else NodoValor(None)
            params = argumentos[2:] if len(argumentos) > 2 else []
            return NodoTransformar(hb, oper, params)
        if nombre_txt == "graficar":
            hb = argumentos[0] if argumentos else NodoValor(None)
            return NodoGraficar(hb)

        return NodoLlamadaFuncion(nombre_txt, argumentos)

    def visit_assignment_expression(self, node: Node) -> NodoAsignacion:
        """Procesa una expresión de asignación.

        Args:
            node: Nodo de asignación

        Returns:
            NodoAsignacion correspondiente
        """
        izquierdo = self.visit(node.child_by_field_name("left"))
        derecho = self.visit(node.child_by_field_name("right"))
        return NodoAsignacion(izquierdo, derecho)

    def visit_expression_statement(self, node: Node) -> Any:
        """Procesa una sentencia de expresión.

        Args:
            node: Nodo de expresión

        Returns:
            Nodo del AST correspondiente
        """
        expr = node.child_by_field_name("expression") or node.children[0]
        return self.visit(expr)

    def visit_return_statement(self, node: Node) -> NodoRetorno:
        """Procesa una sentencia return.

        Args:
            node: Nodo return

        Returns:
            NodoRetorno correspondiente
        """
        valor = node.child_by_field_name("argument")
        return NodoRetorno(self.visit(valor) if valor else NodoValor(None))

    def visit_if_statement(self, node: Node) -> NodoCondicional:
        """Procesa una sentencia if.

        Args:
            node: Nodo if

        Returns:
            NodoCondicional correspondiente
        """
        cond = self.visit(node.child_by_field_name("condition"))
        conseq = node.child_by_field_name("consequence")
        alt = node.child_by_field_name("alternative")

        bloque_si = [
            self.visit(c)
            for c in conseq.children
            if c.is_named
        ] if conseq else []

        bloque_sino = [
            self.visit(c)
            for c in alt.children
            if c.is_named
        ] if alt else []

        return NodoCondicional(cond, bloque_si, bloque_sino)

    def visit_function_definition(self, node: Node) -> NodoFuncion:
        """Procesa una definición de función.

        Args:
            node: Nodo de definición de función

        Returns:
            NodoFuncion correspondiente
        """
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