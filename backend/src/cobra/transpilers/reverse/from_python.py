# -*- coding: utf-8 -*-
"""Transpilador inverso desde Python a Cobra."""

import ast
from typing import Any, List

from core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoCondicional,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoRetorno,
    NodoValor,
    NodoIdentificador,
    NodoPara,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoAtributo,
    NodoPasar,
    NodoRomper,
    NodoContinuar,
)
from cobra.lexico.lexer import Token, TipoToken
from src.cobra.transpilers.reverse.base import BaseReverseTranspiler


_OP_BINARIA = {
    ast.Add: Token(TipoToken.SUMA, "+"),
    ast.Sub: Token(TipoToken.RESTA, "-"),
    ast.Mult: Token(TipoToken.MULT, "*"),
    ast.Div: Token(TipoToken.DIV, "/"),
    ast.Mod: Token(TipoToken.MOD, "%"),
    ast.Eq: Token(TipoToken.IGUAL, "=="),
    ast.NotEq: Token(TipoToken.DIFERENTE, "!="),
    ast.Lt: Token(TipoToken.MENORQUE, "<"),
    ast.Gt: Token(TipoToken.MAYORQUE, ">"),
    ast.LtE: Token(TipoToken.MENORIGUAL, "<="),
    ast.GtE: Token(TipoToken.MAYORIGUAL, ">="),
    ast.And: Token(TipoToken.AND, "and"),
    ast.Or: Token(TipoToken.OR, "or"),
}

_OP_UNARIA = {
    ast.UAdd: Token(TipoToken.SUMA, "+"),
    ast.USub: Token(TipoToken.RESTA, "-"),
    ast.Not: Token(TipoToken.NOT, "not"),
}


class ReverseFromPython(BaseReverseTranspiler):
    """Convierte código Python en nodos del AST de Cobra."""

    def generate_ast(self, code: str):
        tree = ast.parse(code)
        self.ast = [self.visit(stmt) for stmt in tree.body]
        return self.ast

    # Ajustar el dispatch para nodos de ``ast`` escritos en CamelCase
    def visit(self, node):  # type: ignore[override]
        metodo = getattr(self, f"visit_{node.__class__.__name__}", None)
        if metodo is None:
            return self.generic_visit(node)
        return metodo(node)

    # Utilizamos los métodos visit_ heredados de NodeVisitor
    def generic_visit(self, node):
        raise NotImplementedError(f"Nodo de Python no soportado: {node.__class__.__name__}")

    # Nodos simples -----------------------------------------------------
    def visit_Name(self, node: ast.Name):
        return NodoIdentificador(node.id)

    def visit_Constant(self, node: ast.Constant):
        return NodoValor(node.value)

    def visit_Pass(self, node: ast.Pass):
        return NodoPasar()

    def visit_Break(self, node: ast.Break):
        return NodoRomper()

    def visit_Continue(self, node: ast.Continue):
        return NodoContinuar()

    # Operaciones -------------------------------------------------------
    def visit_BinOp(self, node: ast.BinOp):
        op_token = _OP_BINARIA.get(type(node.op))
        izquierda = self.visit(node.left)
        derecha = self.visit(node.right)
        if op_token is None:
            raise NotImplementedError(f"Operador binario no soportado: {type(node.op).__name__}")
        return NodoOperacionBinaria(izquierda, op_token, derecha)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        op_token = _OP_UNARIA.get(type(node.op))
        operando = self.visit(node.operand)
        if op_token is None:
            raise NotImplementedError(f"Operador unario no soportado: {type(node.op).__name__}")
        return NodoOperacionUnaria(op_token, operando)

    def visit_Compare(self, node: ast.Compare):
        izquierda = self.visit(node.left)
        op = _OP_BINARIA.get(type(node.ops[0]))
        derecha = self.visit(node.comparators[0])
        if op is None:
            raise NotImplementedError(f"Operador de comparación no soportado: {type(node.ops[0]).__name__}")
        return NodoOperacionBinaria(izquierda, op, derecha)

    # Expresiones -------------------------------------------------------
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            obj = self.visit(node.func.value)
            nombre = node.func.attr
            args = [self.visit(a) for a in node.args]
            return NodoLlamadaMetodo(obj, nombre, args)
        else:
            nombre = node.func.id if isinstance(node.func, ast.Name) else str(node.func)
            args = [self.visit(a) for a in node.args]
            return NodoLlamadaFuncion(nombre, args)

    def visit_Attribute(self, node: ast.Attribute):
        obj = self.visit(node.value)
        return NodoAtributo(obj, node.attr)

    # Sentencias -------------------------------------------------------
    def visit_Assign(self, node: ast.Assign):
        target = node.targets[0]
        nombre = target.id if isinstance(target, ast.Name) else self.visit(target)
        valor = self.visit(node.value)
        return NodoAsignacion(nombre, valor)

    def visit_Return(self, node: ast.Return):
        valor = self.visit(node.value) if node.value else NodoValor(None)
        return NodoRetorno(valor)

    def visit_Expr(self, node: ast.Expr):
        return self.visit(node.value)

    def visit_If(self, node: ast.If):
        cond = self.visit(node.test)
        bloque_si = [self.visit(n) for n in node.body]
        bloque_sino = [self.visit(n) for n in node.orelse]
        return NodoCondicional(cond, bloque_si, bloque_sino)

    def visit_While(self, node: ast.While):
        cond = self.visit(node.test)
        cuerpo = [self.visit(n) for n in node.body]
        return NodoBucleMientras(cond, cuerpo)

    def visit_For(self, node: ast.For):
        var = node.target.id if isinstance(node.target, ast.Name) else self.visit(node.target)
        iterable = self.visit(node.iter)
        cuerpo = [self.visit(n) for n in node.body]
        return NodoPara(var, iterable, cuerpo)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        params = [arg.arg for arg in node.args.args]
        cuerpo = [self.visit(n) for n in node.body]
        decoradores = [self.visit(d) for d in node.decorator_list]
        return NodoFuncion(node.name, params, cuerpo, decoradores=decoradores)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        params = [arg.arg for arg in node.args.args]
        cuerpo = [self.visit(n) for n in node.body]
        decoradores = [self.visit(d) for d in node.decorator_list]
        return NodoFuncion(node.name, params, cuerpo, decoradores=decoradores, asincronica=True)
