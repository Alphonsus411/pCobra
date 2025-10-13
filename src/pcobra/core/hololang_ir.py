"""Representación intermedia para Hololang.

Este módulo define una serie de estructuras de datos ligeras que modelan
instrucciones de Hololang y una utilidad para transformar el AST de Cobra a
esta representación.  El objetivo es proporcionar un formato intermedio
estable que pueda ser consumido por backends como el generador de ensamblador
sin depender de los nodos específicos del AST de Cobra.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence

from pcobra.cobra.core import Token, TipoToken

from .ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoCondicional,
    NodoFuncion,
    NodoHolobit,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoLista,
    NodoDiccionario,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoRetorno,
    NodoValor,
    NodoFor,
    NodoPara,
)


# ---------------------------------------------------------------------------
#  Dataclasses que describen el IR de Hololang
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class HololangStatement:
    """Clase base para instrucciones Hololang."""


@dataclass(slots=True)
class HololangAssignment(HololangStatement):
    """Asignación simple ``SET``."""

    target: str
    value: str
    inference: bool = False


@dataclass(slots=True)
class HololangIf(HololangStatement):
    """Bloque condicional ``IF``."""

    condition: str
    then_branch: List[HololangStatement] = field(default_factory=list)
    else_branch: List[HololangStatement] = field(default_factory=list)


@dataclass(slots=True)
class HololangWhile(HololangStatement):
    """Bucle ``WHILE``."""

    condition: str
    body: List[HololangStatement] = field(default_factory=list)


@dataclass(slots=True)
class HololangFor(HololangStatement):
    """Bucle ``FOR`` estilo ``for-in``."""

    target: str
    iterable: str
    body: List[HololangStatement] = field(default_factory=list)


@dataclass(slots=True)
class HololangFunction(HololangStatement):
    """Definición de función."""

    name: str
    parameters: List[str] = field(default_factory=list)
    body: List[HololangStatement] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    async_flag: bool = False


@dataclass(slots=True)
class HololangReturn(HololangStatement):
    """Sentencia ``RETURN``."""

    value: Optional[str] = None


@dataclass(slots=True)
class HololangCall(HololangStatement):
    """Llamada a función o método utilizada como instrucción."""

    name: str
    arguments: List[str] = field(default_factory=list)


@dataclass(slots=True)
class HololangExpressionStatement(HololangStatement):
    """Instrucción genérica basada en una expresión textual."""

    expression: str


@dataclass(slots=True)
class HololangPrint(HololangStatement):
    """Instrucción de impresión."""

    expression: str


@dataclass(slots=True)
class HololangHolobit(HololangStatement):
    """Declaración de holobit."""

    name: str
    values: List[str] = field(default_factory=list)


@dataclass(slots=True)
class HololangUnknown(HololangStatement):
    """Nodo para representar construcciones aún no soportadas."""

    description: str


@dataclass(slots=True)
class HololangModule:
    """Contenedor superior del IR."""

    body: List[HololangStatement] = field(default_factory=list)

    def extend(self, statements: Iterable[HololangStatement]) -> None:
        self.body.extend(statements)


# ---------------------------------------------------------------------------
#  Funciones auxiliares de conversión
# ---------------------------------------------------------------------------


def _token_to_text(token: Token) -> str:
    valor = getattr(token, "valor", None)
    if valor is None:
        return str(token)
    if isinstance(valor, str):
        return valor
    return str(valor)


def _value_to_text(valor) -> str:
    if isinstance(valor, str):
        return repr(valor)
    if isinstance(valor, bool):
        return "verdadero" if valor else "falso"
    if valor is None:
        return "null"
    return str(valor)


def _expr_to_text(expr) -> str:
    """Convierte expresiones del AST a una representación textual básica."""

    if expr is None:
        return "null"

    if isinstance(expr, str):
        return expr

    if isinstance(expr, NodoValor):
        return _value_to_text(expr.valor)

    if isinstance(expr, NodoIdentificador):
        return expr.nombre

    if isinstance(expr, NodoLlamadaFuncion):
        args = ", ".join(_expr_to_text(arg) for arg in expr.argumentos)
        return f"{expr.nombre}({args})"

    if isinstance(expr, NodoLlamadaMetodo):
        obj = _expr_to_text(expr.objeto)
        args = ", ".join(_expr_to_text(arg) for arg in expr.argumentos)
        return f"{obj}.{expr.nombre_metodo}({args})"

    if isinstance(expr, NodoOperacionBinaria):
        izq = _expr_to_text(expr.izquierda)
        der = _expr_to_text(expr.derecha)
        op = _token_to_text(expr.operador)
        if expr.operador.tipo == TipoToken.AND:
            op = "AND"
        elif expr.operador.tipo == TipoToken.OR:
            op = "OR"
        return f"{izq} {op} {der}"

    if isinstance(expr, NodoOperacionUnaria):
        val = _expr_to_text(expr.operando)
        op = _token_to_text(expr.operador)
        if expr.operador.tipo == TipoToken.NOT:
            return f"NOT {val}"
        return f"{op}{val}"

    if isinstance(expr, NodoLista):
        elementos = ", ".join(_expr_to_text(e) for e in expr.elementos)
        return f"[{elementos}]"

    if isinstance(expr, NodoDiccionario):
        elementos = ", ".join(
            f"{_expr_to_text(k)}: {_expr_to_text(v)}" for k, v in expr.elementos
        )
        return f"{{{elementos}}}"

    if isinstance(expr, NodoHolobit):
        valores = ", ".join(_expr_to_text(v) for v in expr.valores)
        nombre = expr.nombre or "holobit"
        return f"{nombre}[{valores}]"

    if isinstance(expr, Token):
        return _token_to_text(expr)

    return _value_to_text(getattr(expr, "valor", expr))


def _target_name(variable) -> str:
    if isinstance(variable, NodoIdentificador):
        return variable.nombre
    if isinstance(variable, Token):
        return _token_to_text(variable)
    return str(variable)


def _convert_statement(node) -> HololangStatement:
    if isinstance(node, NodoAsignacion):
        nombre = getattr(node, "identificador", node.variable)
        valor = getattr(node, "expresion", getattr(node, "valor", None))
        return HololangAssignment(_target_name(nombre), _expr_to_text(valor), node.inferencia)

    if isinstance(node, NodoCondicional):
        cond = _expr_to_text(node.condicion)
        then_branch = [_convert_statement(n) for n in node.bloque_si]
        else_branch = [_convert_statement(n) for n in node.bloque_sino]
        return HololangIf(cond, then_branch, else_branch)

    if isinstance(node, NodoBucleMientras):
        condicion = _expr_to_text(node.condicion)
        cuerpo = [_convert_statement(n) for n in node.cuerpo]
        return HololangWhile(condicion, cuerpo)

    if isinstance(node, NodoFor):
        objetivo = _target_name(node.variable)
        iterable = _expr_to_text(node.iterable)
        cuerpo = [_convert_statement(n) for n in node.cuerpo]
        return HololangFor(objetivo, iterable, cuerpo)

    if isinstance(node, NodoPara):
        objetivo = _target_name(node.variable)
        iterable = _expr_to_text(node.iterable)
        cuerpo = [_convert_statement(n) for n in node.cuerpo]
        return HololangFor(objetivo, iterable, cuerpo)

    if isinstance(node, NodoFuncion):
        cuerpo = [_convert_statement(n) for n in node.cuerpo]
        decoradores = [_expr_to_text(d) for d in getattr(node, "decoradores", [])]
        return HololangFunction(
            name=node.nombre,
            parameters=list(node.parametros),
            body=cuerpo,
            decorators=decoradores,
            async_flag=getattr(node, "asincronica", False),
        )

    if isinstance(node, NodoRetorno):
        valor = _expr_to_text(node.expresion) if getattr(node, "expresion", None) else None
        return HololangReturn(valor)

    if isinstance(node, NodoLlamadaFuncion):
        args = [_expr_to_text(arg) for arg in node.argumentos]
        return HololangCall(node.nombre, args)

    if isinstance(node, NodoLlamadaMetodo):
        objeto = _expr_to_text(node.objeto)
        args = [_expr_to_text(arg) for arg in node.argumentos]
        return HololangCall(f"{objeto}.{node.nombre_metodo}", args)

    if isinstance(node, NodoImprimir):
        return HololangPrint(_expr_to_text(node.expresion))

    if isinstance(node, NodoHolobit):
        return HololangHolobit(node.nombre or "", [_expr_to_text(v) for v in node.valores])

    return HololangUnknown(f"Nodo {type(node).__name__} no soportado")


def build_hololang_ir(ast: Sequence) -> HololangModule:
    """Convierte una secuencia de nodos AST a un :class:`HololangModule`."""

    module = HololangModule()
    if ast is None:
        return module

    statements = [_convert_statement(node) for node in ast]
    module.extend(statements)
    return module

