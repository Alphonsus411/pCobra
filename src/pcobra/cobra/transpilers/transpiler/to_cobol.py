"""Transpilador que genera código COBOL a partir de Cobra."""

from pcobra.cobra.core.ast_nodes import (
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
from pcobra.cobra.core import TipoToken
from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.common.utils import BaseTranspiler
from pcobra.core.optimizations import optimize_constants
from pcobra.cobra.macro import expandir_macros

from pcobra.cobra.transpilers.transpiler.cobol_nodes.asignacion import visit_asignacion as _visit_asignacion
from pcobra.cobra.transpilers.transpiler.cobol_nodes.funcion import visit_funcion as _visit_funcion
from pcobra.cobra.transpilers.transpiler.cobol_nodes.llamada_funcion import (
    visit_llamada_funcion as _visit_llamada_funcion,
)
from pcobra.cobra.transpilers.transpiler.cobol_nodes.imprimir import (
    visit_imprimir as _visit_imprimir,
)
from pcobra.cobra.transpilers.transpiler.cobol_nodes.retorno import (
    visit_retorno as _visit_retorno,
)


cobol_nodes = {
    "asignacion": _visit_asignacion,
    "funcion": _visit_funcion,
    "llamada_funcion": _visit_llamada_funcion,
    "imprimir": _visit_imprimir,
    "retorno": _visit_retorno,
}


class TranspiladorCOBOL(BaseTranspiler):
    """Transpila el AST de Cobra a un COBOL muy simplificado."""

    def __init__(self):
        self.codigo = []
        self.indent = 0

    def generate_code(self, ast):
        self.codigo = []
        self.indent = 0
        self.transpilar(ast)
        return "\n".join(self.codigo)

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor):
            return str(nodo.valor)
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}-{nodo.nombre}"
        elif isinstance(nodo, NodoLlamadaFuncion):
            args = " ".join(self.obtener_valor(a) for a in nodo.argumentos)
            if args:
                return f"CALL '{nodo.nombre}' USING {args}"
            return f"CALL '{nodo.nombre}'"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "AND", TipoToken.OR: "OR"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            op = "NOT" if nodo.operador.tipo == TipoToken.NOT else nodo.operador.valor
            return f"{op} {val}" if op == "NOT" else f"{op}{val}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = optimize_constants(expandir_macros(nodos))
        self.agregar_linea("IDENTIFICATION DIVISION.")
        self.agregar_linea("PROGRAM-ID. MAIN.")
        self.agregar_linea("PROCEDURE DIVISION.")
        self.indent += 1
        for nodo in nodos:
            nodo.aceptar(self)
        self.agregar_linea("STOP RUN.")
        self.indent -= 1


for nombre, funcion in cobol_nodes.items():
    setattr(TranspiladorCOBOL, f"visit_{nombre}", funcion)
