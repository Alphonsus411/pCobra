"""Adaptadores entre el IR de Hololang y el AST de Cobra."""

from __future__ import annotations

import ast as pyast
import re
from collections.abc import Sequence
from typing import Any, Iterable, List

from pcobra.core.hololang_ir import (
    HololangAssignment,
    HololangCall,
    HololangExpressionStatement,
    HololangFor,
    HololangFunction,
    HololangHolobit,
    HololangIf,
    HololangModule,
    HololangPrint,
    HololangReturn,
    HololangStatement,
    HololangUnknown,
    HololangWhile,
)

from pcobra.cobra.core import Token, TipoToken
from pcobra.cobra.core.ast_nodes import (
    NodoAtributo,
    NodoAsignacion,
    NodoBucleMientras,
    NodoCondicional,
    NodoDecorador,
    NodoDiccionario,
    NodoFuncion,
    NodoHolobit,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoLista,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoPara,
    NodoRetorno,
    NodoValor,
)

__all__ = ["is_hololang_ir", "hololang_ir_to_cobra_ast", "ensure_cobra_ast"]


_KEYWORD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bverdadero\b"), "True"),
    (re.compile(r"\bfalso\b"), "False"),
    (re.compile(r"\bnull\b"), "None"),
    (re.compile(r"\bAND\b"), "and"),
    (re.compile(r"\bOR\b"), "or"),
    (re.compile(r"\bNOT\b"), "not"),
]


def is_hololang_ir(obj: Any) -> bool:
    """Determina si ``obj`` corresponde al IR de Hololang."""

    if isinstance(obj, HololangModule):
        return True
    if isinstance(obj, HololangStatement):
        return True
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        return all(isinstance(elem, HololangStatement) for elem in obj)
    return False


def ensure_cobra_ast(programa: Any) -> list[Any]:
    """Devuelve nodos AST de Cobra a partir de ``programa``."""

    if programa is None:
        return []
    if isinstance(programa, HololangModule):
        return [
            _convert_statement(stmt)
            for stmt in programa.body
            if stmt is not None
        ]
    if isinstance(programa, Sequence) and not isinstance(programa, (str, bytes)):
        if all(isinstance(elem, HololangStatement) for elem in programa):
            return [_convert_statement(stmt) for stmt in programa if stmt is not None]
        return list(programa)
    if isinstance(programa, HololangStatement):
        return [_convert_statement(programa)]
    return programa


def hololang_ir_to_cobra_ast(programa: Any) -> list[Any]:
    """Alias público de :func:`ensure_cobra_ast`."""

    return ensure_cobra_ast(programa)


def _convert_statement(stmt: HololangStatement) -> Any:
    if isinstance(stmt, HololangAssignment):
        destino = _parse_target(stmt.target)
        valor = _parse_expression(stmt.value)
        return NodoAsignacion(destino, valor, stmt.inference)

    if isinstance(stmt, HololangIf):
        condicion = _parse_expression(stmt.condition)
        bloque_si = [_convert_statement(s) for s in stmt.then_branch]
        bloque_sino = [_convert_statement(s) for s in stmt.else_branch]
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    if isinstance(stmt, HololangWhile):
        condicion = _parse_expression(stmt.condition)
        cuerpo = [_convert_statement(s) for s in stmt.body]
        return NodoBucleMientras(condicion, cuerpo)

    if isinstance(stmt, HololangFor):
        variable = _parse_target(stmt.target)
        iterable = _parse_expression(stmt.iterable)
        cuerpo = [_convert_statement(s) for s in stmt.body]
        return NodoPara(variable, iterable, cuerpo)

    if isinstance(stmt, HololangFunction):
        cuerpo = [_convert_statement(s) for s in stmt.body]
        decoradores = [
            NodoDecorador(_parse_expression(expr))
            for expr in stmt.decorators
            if expr
        ]
        return NodoFuncion(
            stmt.name,
            list(stmt.parameters),
            cuerpo,
            decoradores=decoradores,
            asincronica=stmt.async_flag,
        )

    if isinstance(stmt, HololangReturn):
        if stmt.value is None:
            valor = NodoValor(None)
        else:
            valor = _parse_expression(stmt.value)
        return NodoRetorno(valor)

    if isinstance(stmt, HololangCall):
        expresion = _parse_expression(_format_call(stmt.name, stmt.arguments))
        if isinstance(expresion, (NodoLlamadaFuncion, NodoLlamadaMetodo)):
            return expresion
        argumentos = [_parse_expression(arg) for arg in stmt.arguments]
        return NodoLlamadaFuncion(stmt.name, argumentos)

    if isinstance(stmt, HololangExpressionStatement):
        return _parse_expression(stmt.expression)

    if isinstance(stmt, HololangPrint):
        return NodoImprimir(_parse_expression(stmt.expression))

    if isinstance(stmt, HololangHolobit):
        nombre = stmt.name or None
        valores = [_parse_expression(valor) for valor in stmt.values]
        return NodoHolobit(nombre, valores)

    if isinstance(stmt, HololangUnknown):
        raise ValueError(
            f"Nodo IR de Hololang no soportado: {stmt.description}"
        )

    raise TypeError(f"Tipo de instrucción no reconocido: {type(stmt)!r}")


def _parse_target(texto: str) -> Any:
    expresion = _parse_expression(texto)
    if isinstance(expresion, NodoIdentificador):
        return expresion.nombre
    return expresion


def _format_call(nombre: str, argumentos: Iterable[str]) -> str:
    args = ", ".join(argumentos)
    return f"{nombre}({args})" if args else f"{nombre}()"


def _parse_expression(texto: str | None) -> Any:
    if texto is None:
        return NodoValor(None)
    texto = texto.strip()
    if not texto:
        return NodoValor(None)

    normalizado = texto.replace("::", ".")
    for patron, reemplazo in _KEYWORD_PATTERNS:
        normalizado = patron.sub(reemplazo, normalizado)

    try:
        tree = pyast.parse(normalizado, mode="eval")
    except SyntaxError:
        return NodoValor(texto)

    return _python_ast_to_cobra(tree.body, original=texto)


def _python_ast_to_cobra(node: pyast.AST, *, original: str) -> Any:
    if isinstance(node, pyast.Constant):
        return NodoValor(node.value)

    if isinstance(node, pyast.Name):
        return NodoIdentificador(node.id)

    if isinstance(node, pyast.Attribute):
        base = _python_ast_to_cobra(node.value, original=original)
        return NodoAtributo(base, node.attr)

    if isinstance(node, pyast.Call):
        argumentos = [_python_ast_to_cobra(arg, original=original) for arg in node.args]
        if isinstance(node.func, pyast.Attribute):
            objeto = _python_ast_to_cobra(node.func.value, original=original)
            return NodoLlamadaMetodo(objeto, node.func.attr, argumentos)
        if isinstance(node.func, pyast.Name):
            return NodoLlamadaFuncion(node.func.id, argumentos)
        return NodoLlamadaFuncion(_safe_unparse(node.func), argumentos)

    if isinstance(node, pyast.BinOp):
        izquierda = _python_ast_to_cobra(node.left, original=original)
        derecha = _python_ast_to_cobra(node.right, original=original)
        token = _map_binop(node.op)
        return NodoOperacionBinaria(izquierda, token, derecha)

    if isinstance(node, pyast.BoolOp):
        valores = [_python_ast_to_cobra(v, original=original) for v in node.values]
        if not valores:
            return NodoValor(None)
        generador_token = _map_boolop(node.op)
        actual = valores[0]
        for siguiente in valores[1:]:
            actual = NodoOperacionBinaria(actual, generador_token(), siguiente)
        return actual

    if isinstance(node, pyast.Compare):
        izquierda = _python_ast_to_cobra(node.left, original=original)
        resultado = izquierda
        for operador, comparador in zip(node.ops, node.comparators):
            token = _map_compare_op(operador)
            derecha = _python_ast_to_cobra(comparador, original=original)
            resultado = NodoOperacionBinaria(resultado, token, derecha)
        return resultado

    if isinstance(node, pyast.UnaryOp):
        operando = _python_ast_to_cobra(node.operand, original=original)
        token = _map_unary_op(node.op)
        return NodoOperacionUnaria(token, operando)

    if isinstance(node, pyast.List):
        return NodoLista([_python_ast_to_cobra(e, original=original) for e in node.elts])

    if isinstance(node, pyast.Tuple):
        return NodoLista([_python_ast_to_cobra(e, original=original) for e in node.elts])

    if isinstance(node, pyast.Dict):
        elementos: List[tuple[Any, Any]] = []
        for clave, valor in zip(node.keys, node.values):
            if clave is None:
                clave_ast = NodoValor(None)
            else:
                clave_ast = _python_ast_to_cobra(clave, original=original)
            valor_ast = _python_ast_to_cobra(valor, original=original)
            elementos.append((clave_ast, valor_ast))
        return NodoDiccionario(elementos)

    if isinstance(node, pyast.Subscript):
        return NodoValor(_safe_unparse(node))

    return NodoValor(original)


def _map_binop(op: pyast.operator) -> Token:
    if isinstance(op, pyast.Add):
        return Token(TipoToken.SUMA, "+")
    if isinstance(op, pyast.Sub):
        return Token(TipoToken.RESTA, "-")
    if isinstance(op, pyast.Mult):
        return Token(TipoToken.MULT, "*")
    if isinstance(op, pyast.Div):
        return Token(TipoToken.DIV, "/")
    if isinstance(op, pyast.Mod):
        return Token(TipoToken.MOD, "%")
    if isinstance(op, pyast.Pow):
        return Token(TipoToken.MULT, "**")
    return Token(TipoToken.SUMA, str(type(op).__name__))


def _map_boolop(op: pyast.boolop) -> callable[[], Token]:
    if isinstance(op, pyast.And):
        return lambda: Token(TipoToken.AND, "&&")
    if isinstance(op, pyast.Or):
        return lambda: Token(TipoToken.OR, "||")
    return lambda: Token(TipoToken.AND, str(type(op).__name__))


def _map_compare_op(op: pyast.cmpop) -> Token:
    if isinstance(op, pyast.Eq):
        return Token(TipoToken.IGUAL, "==")
    if isinstance(op, pyast.NotEq):
        return Token(TipoToken.DIFERENTE, "!=")
    if isinstance(op, pyast.Lt):
        return Token(TipoToken.MENORQUE, "<")
    if isinstance(op, pyast.LtE):
        return Token(TipoToken.MENORIGUAL, "<=")
    if isinstance(op, pyast.Gt):
        return Token(TipoToken.MAYORQUE, ">")
    if isinstance(op, pyast.GtE):
        return Token(TipoToken.MAYORIGUAL, ">=")
    if isinstance(op, pyast.Is):
        return Token(TipoToken.IGUAL, "==")
    if isinstance(op, pyast.IsNot):
        return Token(TipoToken.DIFERENTE, "!=")
    return Token(TipoToken.IGUAL, str(type(op).__name__))


def _map_unary_op(op: pyast.unaryop) -> Token:
    if isinstance(op, pyast.Not):
        return Token(TipoToken.NOT, "!")
    if isinstance(op, pyast.USub):
        return Token(TipoToken.RESTA, "-")
    if isinstance(op, pyast.UAdd):
        return Token(TipoToken.SUMA, "+")
    return Token(TipoToken.NOT, str(type(op).__name__))


def _safe_unparse(node: pyast.AST) -> str:
    try:
        return pyast.unparse(node)
    except Exception:  # pragma: no cover - compatibilidad
        return repr(node)
