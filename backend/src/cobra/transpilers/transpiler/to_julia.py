"""Transpilador simple de Cobra a Julia."""

from backend.src.core.ast_nodes import (
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
from backend.src.cobra.lexico.lexer import TipoToken
from backend.src.core.visitor import NodeVisitor
from ..base import BaseTranspiler
from backend.src.core.optimizations import optimize_constants, remove_dead_code, inline_functions
from backend.src.cobra.macro import expandir_macros


def visit_asignacion(self, nodo: NodoAsignacion):
    nombre = getattr(nodo, "identificador", nodo.variable)
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"{nombre} = {valor}")


def visit_funcion(self, nodo: NodoFuncion):
    params = ", ".join(nodo.parametros)
    self.agregar_linea(f"function {nodo.nombre}({params})")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("end")


def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"{nodo.nombre}({args})")


def visit_imprimir(self, nodo: NodoImprimir):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"println({valor})")


julia_nodes = {
    "asignacion": visit_asignacion,
    "funcion": visit_funcion,
    "llamada_funcion": visit_llamada_funcion,
    "imprimir": visit_imprimir,
}


class TranspiladorJulia(BaseTranspiler):
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
            return nodo.nombre
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}.{nodo.nombre}"
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
            metodo = getattr(self, f"visit_{nodo.__class__.__name__[4:].lower()}", None)
            if metodo:
                metodo(nodo)
        return "\n".join(self.codigo)


for nombre, funcion in julia_nodes.items():
    setattr(TranspiladorJulia, f"visit_{nombre}", funcion)
