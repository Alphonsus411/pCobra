"""Transpilador que genera LLVM IR a partir del AST de Cobra."""

from __future__ import annotations

from typing import List

from pcobra.compiler.llvm_backend import generar_ir_funcion
from pcobra.core import ast_nodes
from pcobra.cobra.core import TipoToken


class TranspiladorLLVM:
    """Transpilador muy básico para LLVM.

    Solo maneja funciones sin parámetros cuyo cuerpo es una única expresión
    soportada por :mod:`pcobra.compiler.llvm_backend`.
    """

    def _to_expr(self, node):
        """Convierte nodos del AST a la representación esperada por el backend."""
        if isinstance(node, ast_nodes.NodoValor):
            return int(node.valor)
        if (
            isinstance(node, ast_nodes.NodoOperacionBinaria)
            and node.operador.tipo == TipoToken.SUMA
        ):
            return ("add", self._to_expr(node.izquierda), self._to_expr(node.derecha))
        raise NotImplementedError("Expresión no soportada para LLVM")

    def generate_code(self, ast: List[ast_nodes.NodoAST]) -> str:
        ir_funcs: List[str] = []
        for nodo in ast:
            if isinstance(nodo, ast_nodes.NodoFuncion) and not nodo.parametros:
                if nodo.cuerpo:
                    expr_node = getattr(nodo.cuerpo[0], "expresion", None)
                    if expr_node is not None:
                        expr = self._to_expr(expr_node)
                        ir_funcs.append(generar_ir_funcion(nodo.nombre, expr))
        return "\n\n".join(ir_funcs)
