"""Transpilador simple de Cobra a PHP."""

from core.ast_nodes import (
    NodoValor,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoAsignacion,
    NodoFuncion,
    NodoImprimir,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoAtributo,
)
from cobra.lexico.lexer import TipoToken
from core.visitor import NodeVisitor
from ..base import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros


def visit_asignacion(self, nodo: NodoAsignacion):
    nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
    if isinstance(nombre_raw, NodoAtributo):
        nombre = self.obtener_valor(nombre_raw)
    else:
        nombre = f"${nombre_raw}"
    valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
    self.agregar_linea(f"{nombre} = {self.obtener_valor(valor)};")


def visit_funcion(self, nodo: NodoFuncion):
    params = ", ".join(f"${p}" for p in nodo.parametros)
    self.agregar_linea(f"function {nodo.nombre}({params}) {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"{nodo.nombre}({args});")


def visit_imprimir(self, nodo: NodoImprimir):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"echo {valor};")


php_nodes = {
    "asignacion": visit_asignacion,
    "funcion": visit_funcion,
    "llamada_funcion": visit_llamada_funcion,
    "imprimir": visit_imprimir,
}


class TranspiladorPHP(BaseTranspiler):
    """Transpila el AST de Cobra a un PHP muy básico."""

    def __init__(self):
        self.codigo = []
        self.indent = 0

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor):
            return str(nodo.valor)
        elif isinstance(nodo, NodoIdentificador):
            return f"${nodo.nombre}"
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}->{nodo.nombre}"
        elif isinstance(nodo, NodoLlamadaFuncion):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre}({args})"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "&&", TipoToken.OR: "||"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            op = "!" if nodo.operador.tipo == TipoToken.NOT else nodo.operador.valor
            return f"{op}{val}" if op != "!" else f"!{val}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            if hasattr(nodo, "aceptar"):
                nodo.aceptar(self)
            else:
                metodo = getattr(
                    self, f"visit_{nodo.__class__.__name__[4:].lower()}", None
                )
                if metodo:
                    metodo(nodo)
        return "\n".join(self.codigo)


for nombre, funcion in php_nodes.items():
    setattr(TranspiladorPHP, f"visit_{nombre}", funcion)
