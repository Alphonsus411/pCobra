"""Transpilador simple de Cobra a LaTeX."""

from cobra.core.ast_nodes import (
    NodoValor,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoAsignacion,
    NodoFuncion,
    NodoImprimir,
    NodoAtributo,
)
from core.visitor import NodeVisitor
from cobra.transpilers.common.utils import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code
from cobra.macro import expandir_macros

from cobra.transpilers.transpiler.latex_nodes.asignacion import visit_asignacion as _visit_asignacion
from cobra.transpilers.transpiler.latex_nodes.funcion import visit_funcion as _visit_funcion
from cobra.transpilers.transpiler.latex_nodes.llamada_funcion import (
    visit_llamada_funcion as _visit_llamada_funcion,
)
from cobra.transpilers.transpiler.latex_nodes.imprimir import visit_imprimir as _visit_imprimir
from cobra.transpilers.transpiler.latex_nodes.retorno import visit_retorno as _visit_retorno

latex_nodes = {
    "asignacion": _visit_asignacion,
    "funcion": _visit_funcion,
    "llamada_funcion": _visit_llamada_funcion,
    "imprimir": _visit_imprimir,
    "retorno": _visit_retorno,
}


class TranspiladorLatex(BaseTranspiler):
    def __init__(self):
        self.codigo = []
        self.indent = 0

    def generate_code(self, ast):
        """Genera un documento LaTeX completo a partir del AST."""
        self.codigo = []
        cuerpo = self.transpilar(ast)
        encabezado = "\\documentclass{article}\n\\begin{document}\n"
        pie = "\n\\end{document}"
        return encabezado + cuerpo + pie

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
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(optimize_constants(nodos))
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


for nombre, funcion in latex_nodes.items():
    setattr(TranspiladorLatex, f"visit_{nombre}", funcion)
