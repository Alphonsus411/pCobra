# -*- coding: utf-8 -*-
"""
Transpilador inverso desde Python a Cobra.

Este módulo implementa la conversión de código Python al AST de Cobra,
permitiendo la traducción de programas Python al lenguaje Cobra.
"""

import ast
from typing import Any, List, Optional, Union

from pcobra.cobra.core.ast_nodes import (
    NodoAST,
    NodoAsignacion,
    NodoBucleMientras,
    NodoCondicional,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
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
    NodoLista,
    NodoDiccionario,
    NodoListaTipo,
    NodoDiccionarioTipo,
    NodoListaComprehension,
    NodoDiccionarioComprehension,
)
from pcobra.cobra.core import Token, TipoToken
from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler


class ReverseFromPython(BaseReverseTranspiler):
    """Convierte código Python en nodos del AST de Cobra."""

    # Constantes de clase para operadores
    OPERADORES_BINARIOS = {
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

    OPERADORES_UNARIOS = {
        ast.UAdd: Token(TipoToken.SUMA, "+"),
        ast.USub: Token(TipoToken.RESTA, "-"),
        ast.Not: Token(TipoToken.NOT, "not"),
    }

    def __init__(self) -> None:
        super().__init__()
        self.ast: List[NodoAST] = []

    def generate_ast(self, code: str) -> List[NodoAST]:
        """
        Genera el AST de Cobra a partir de código Python.

        Args:
            code: Código fuente Python a transpiliar.

        Returns:
            Lista de nodos AST de Cobra.

        Raises:
            SyntaxError: Si el código Python contiene errores de sintaxis.
            NotImplementedError: Si se encuentra un nodo Python no soportado.
        """
        try:
            tree = ast.parse(code)
            self.ast = [self.visit(stmt) for stmt in tree.body]
            return self.ast
        except SyntaxError as e:
            raise SyntaxError(f"Error de sintaxis en el código Python: {str(e)}") from e

    def visit(self, node: ast.AST) -> NodoAST:
        """
        Visita un nodo del AST de Python y lo convierte a su equivalente en Cobra.

        Args:
            node: Nodo del AST de Python a visitar.

        Returns:
            Nodo equivalente del AST de Cobra.
        """
        metodo = getattr(self, f"visit_{node.__class__.__name__}", None)
        if metodo is None:
            return self.generic_visit(node)
        return metodo(node)

    def generic_visit(self, node: ast.AST) -> NodoAST:
        """Maneja nodos no soportados explícitamente."""
        raise NotImplementedError(f"Nodo de Python no soportado: {node.__class__.__name__}")

    # Nodos simples -----------------------------------------------------
    def visit_Name(self, node: ast.Name) -> NodoIdentificador:
        """Convierte un identificador."""
        return NodoIdentificador(node.id)

    def visit_Constant(self, node: ast.Constant) -> NodoValor:
        """Convierte un valor constante."""
        return NodoValor(node.value)

    def visit_Pass(self, node: ast.Pass) -> NodoPasar:
        """Convierte una sentencia pass."""
        return NodoPasar()

    def visit_Break(self, node: ast.Break) -> NodoRomper:
        """Convierte una sentencia break."""
        return NodoRomper()

    def visit_Continue(self, node: ast.Continue) -> NodoContinuar:
        """Convierte una sentencia continue."""
        return NodoContinuar()

    def visit_List(self, node: ast.List) -> NodoLista:
        """Convierte una lista de Python."""
        elementos = [self.visit(e) for e in node.elts]
        return NodoLista(elementos)

    def visit_Dict(self, node: ast.Dict) -> NodoDiccionario:
        """Convierte un diccionario de Python."""
        pares = [
            (self.visit(k), self.visit(v)) for k, v in zip(node.keys, node.values)
        ]
        return NodoDiccionario(pares)

    def visit_ListComp(self, node: ast.ListComp) -> NodoListaComprehension:
        """Convierte una comprensión de lista."""
        if len(node.generators) != 1:
            raise NotImplementedError("Solo se soporta una cláusula 'for'")
        gen = node.generators[0]
        if not isinstance(gen.target, ast.Name):
            raise NotImplementedError("Variable de comprensión no soportada")
        variable = gen.target.id
        iterable = self.visit(gen.iter)
        condicion = self.visit(gen.ifs[0]) if gen.ifs else None
        expresion = self.visit(node.elt)
        return NodoListaComprehension(expresion, variable, iterable, condicion)

    def visit_DictComp(self, node: ast.DictComp) -> NodoDiccionarioComprehension:
        """Convierte una comprensión de diccionario."""
        if len(node.generators) != 1:
            raise NotImplementedError("Solo se soporta una cláusula 'for'")
        gen = node.generators[0]
        if not isinstance(gen.target, ast.Name):
            raise NotImplementedError("Variable de comprensión no soportada")
        variable = gen.target.id
        iterable = self.visit(gen.iter)
        condicion = self.visit(gen.ifs[0]) if gen.ifs else None
        clave = self.visit(node.key)
        valor = self.visit(node.value)
        return NodoDiccionarioComprehension(clave, valor, variable, iterable, condicion)

    # Operaciones -------------------------------------------------------
    def visit_BinOp(self, node: ast.BinOp) -> NodoOperacionBinaria:
        """Convierte una operación binaria."""
        op_token = self.OPERADORES_BINARIOS.get(type(node.op))
        if op_token is None:
            raise NotImplementedError(f"Operador binario no soportado: {type(node.op).__name__}")
        return NodoOperacionBinaria(
            self.visit(node.left),
            op_token,
            self.visit(node.right)
        )

    def visit_UnaryOp(self, node: ast.UnaryOp) -> NodoOperacionUnaria:
        """Convierte una operación unaria."""
        op_token = self.OPERADORES_UNARIOS.get(type(node.op))
        if op_token is None:
            raise NotImplementedError(f"Operador unario no soportado: {type(node.op).__name__}")
        return NodoOperacionUnaria(op_token, self.visit(node.operand))

    def visit_Compare(self, node: ast.Compare) -> NodoOperacionBinaria:
        """Convierte una comparación, manejando comparaciones encadenadas."""

        comparadores = [self.visit(node.left)] + [self.visit(c) for c in node.comparators]
        ops: List[Token] = []
        for op_node in node.ops:
            token = self.OPERADORES_BINARIOS.get(type(op_node))
            if token is None:
                raise NotImplementedError(
                    f"Operador de comparación no soportado: {type(op_node).__name__}"
                )
            ops.append(token)

        resultado = NodoOperacionBinaria(comparadores[0], ops[0], comparadores[1])

        if len(ops) == 1:
            return resultado

        and_token = self.OPERADORES_BINARIOS[ast.And]

        for i in range(1, len(ops)):
            comparacion = NodoOperacionBinaria(comparadores[i], ops[i], comparadores[i + 1])
            resultado = NodoOperacionBinaria(resultado, and_token, comparacion)

        return resultado

    # Expresiones -------------------------------------------------------
    def visit_Call(self, node: ast.Call) -> Union[NodoLlamadaMetodo, NodoLlamadaFuncion]:
        """Convierte una llamada a función o método."""
        args = [self.visit(a) for a in node.args]
        
        if isinstance(node.func, ast.Attribute):
            return NodoLlamadaMetodo(
                self.visit(node.func.value),
                node.func.attr,
                args
            )
        
        if isinstance(node.func, ast.Name):
            nombre = node.func.id
            if nombre == "proyectar":
                hb = args[0] if args else NodoValor(None)
                modo = args[1] if len(args) > 1 else NodoValor(None)
                return NodoProyectar(hb, modo)
            if nombre == "transformar":
                hb = args[0] if args else NodoValor(None)
                oper = args[1] if len(args) > 1 else NodoValor(None)
                params = args[2:] if len(args) > 2 else []
                return NodoTransformar(hb, oper, params)
            if nombre == "graficar":
                hb = args[0] if args else NodoValor(None)
                return NodoGraficar(hb)
            return NodoLlamadaFuncion(nombre, args)
        
        raise NotImplementedError(f"Tipo de llamada no soportado: {type(node.func).__name__}")

    def visit_Attribute(self, node: ast.Attribute) -> NodoAtributo:
        """Convierte un acceso a atributo."""
        return NodoAtributo(self.visit(node.value), node.attr)

    # Sentencias -------------------------------------------------------
    def visit_Assign(self, node: ast.Assign) -> NodoAsignacion:
        """Convierte una asignación."""
        target = node.targets[0]
        if isinstance(target, ast.Name):
            nombre = target.id
        else:
            nombre = self.visit(target)
        valor = self.visit(node.value)
        if isinstance(valor, NodoLista):
            return NodoListaTipo(nombre, "Any", valor.elementos)
        if isinstance(valor, NodoDiccionario):
            return NodoDiccionarioTipo(nombre, "Any", "Any", valor.elementos)
        return NodoAsignacion(nombre, valor)

    def visit_Return(self, node: ast.Return) -> NodoRetorno:
        """Convierte un return."""
        valor = self.visit(node.value) if node.value else NodoValor(None)
        return NodoRetorno(valor)

    def visit_Expr(self, node: ast.Expr) -> NodoAST:
        """Convierte una expresión."""
        return self.visit(node.value)

    def visit_If(self, node: ast.If) -> NodoCondicional:
        """Convierte un if-else."""
        return NodoCondicional(
            self.visit(node.test),
            [self.visit(n) for n in node.body],
            [self.visit(n) for n in node.orelse]
        )

    def visit_While(self, node: ast.While) -> NodoBucleMientras:
        """Convierte un while."""
        return NodoBucleMientras(
            self.visit(node.test),
            [self.visit(n) for n in node.body]
        )

    def visit_For(self, node: ast.For) -> NodoPara:
        """Convierte un for."""
        var = node.target.id if isinstance(node.target, ast.Name) else self.visit(node.target)
        return NodoPara(
            var,
            self.visit(node.iter),
            [self.visit(n) for n in node.body]
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> NodoFuncion:
        """Convierte una definición de función."""
        return NodoFuncion(
            node.name,
            [arg.arg for arg in node.args.args],
            [self.visit(n) for n in node.body],
            decoradores=[self.visit(d) for d in node.decorator_list]
        )

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> NodoFuncion:
        """Convierte una definición de función asíncrona."""
        return NodoFuncion(
            node.name,
            [arg.arg for arg in node.args.args],
            [self.visit(n) for n in node.body],
            decoradores=[self.visit(d) for d in node.decorator_list],
            asincronica=True
        )