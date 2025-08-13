"""Transpilador que genera LLVM IR a partir del AST de Cobra."""

from __future__ import annotations

from typing import List

from compiler.llvm_backend import generar_ir_funcion

from core import ast_nodes


class TranspiladorLLVM:
    """Transpilador muy básico para LLVM.

    Solo maneja funciones sin parámetros cuyo cuerpo es una única expresión
    soportada por :mod:`compiler.llvm_backend`.
    """

    def generate_code(self, ast: List[ast_nodes.NodoAST]) -> str:
        ir_funcs: List[str] = []
        for nodo in ast:
            if isinstance(nodo, ast_nodes.NodoFuncion) and not nodo.parametros:
                if nodo.cuerpo:
                    expr = getattr(nodo.cuerpo[0], "expresion", None)
                    if expr is not None:
                        ir_funcs.append(generar_ir_funcion(nodo.nombre, expr))
        return "\n\n".join(ir_funcs)
