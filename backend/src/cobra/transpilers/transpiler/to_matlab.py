"""Transpilador simple de Cobra a MATLAB."""

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
from backend.src.core.optimizations import optimize_constants, remove_dead_code, inline_functions
from backend.src.cobra.macro import expandir_macros

from .matlab_nodes.asignacion import visit_asignacion as _visit_asignacion
from .matlab_nodes.funcion import visit_funcion as _visit_funcion
from .matlab_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from .matlab_nodes.imprimir import visit_imprimir as _visit_imprimir

matlab_nodes = {
    "asignacion": _visit_asignacion,
    "funcion": _visit_funcion,
    "llamada_funcion": _visit_llamada_funcion,
    "imprimir": _visit_imprimir,
}


class TranspiladorMatlab(NodeVisitor):
    def __init__(self):
        self.codigo = []
        self.indent = 0

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
            op = "~" if nodo.operador.tipo == TipoToken.NOT else nodo.operador.valor
            return f"{op}{val}" if op != "~" else f"~{val}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            if hasattr(nodo, "aceptar"):
                nodo.aceptar(self)
            else:
                metodo = getattr(self, f"visit_{nodo.__class__.__name__[4:].lower()}", None)
                if metodo:
                    metodo(nodo)
        return "\n".join(self.codigo)


for nombre, funcion in matlab_nodes.items():
    setattr(TranspiladorMatlab, f"visit_{nombre}", funcion)
