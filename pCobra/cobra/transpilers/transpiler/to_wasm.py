"""Transpilador muy básico que genera código WebAssembly en formato WAT."""

from cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoOperacionBinaria,
    NodoValor,
    NodoIdentificador,
)
from cobra.core import TipoToken
from core.visitor import NodeVisitor
from cobra.transpilers.common.utils import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros


class TranspiladorWasm(BaseTranspiler):
    """Transpila el AST de Cobra a WebAssembly (WAT) de forma sencilla."""

    def __init__(self):
        self.codigo = []
        self.indent = 0

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor) or isinstance(nodo, int):
            valor = nodo.valor if hasattr(nodo, "valor") else nodo
            return f"(i32.const {valor})"
        elif isinstance(nodo, NodoIdentificador):
            return f"(local.get ${nodo.nombre})"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {
                TipoToken.SUMA: "i32.add",
                TipoToken.RESTA: "i32.sub",
                TipoToken.MULT: "i32.mul",
                TipoToken.DIV: "i32.div_s",
            }
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"({op} {izq} {der})"
        else:
            return str(getattr(nodo, "valor", nodo))

    def visit_asignacion(self, nodo: NodoAsignacion):
        nombre = getattr(nodo, "identificador", nodo.variable)
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"(local.set ${nombre} {valor})")

    def visit_funcion(self, nodo: NodoFuncion):
        params = " ".join(f"(param ${p} i32)" for p in nodo.parametros)
        self.agregar_linea(f"(func ${nodo.nombre} {params}")
        self.indent += 1
        for inst in nodo.cuerpo:
            inst.aceptar(self)
        self.indent -= 1
        self.agregar_linea(")")

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            nodo.aceptar(self)
        return "\n".join(self.codigo)
