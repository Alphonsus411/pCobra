"""Transpilador que genera código C++ a partir de Cobra."""

from core.ast_nodes import (
    NodoLista,
    NodoDiccionario,
    NodoValor,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoAtributo,
    NodoInstancia,
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoLambda,
    NodoWith,
    NodoImportDesde,
)
from cobra.lexico.lexer import TipoToken
from core.visitor import NodeVisitor
from cobra.transpilers.base import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros

from cobra.transpilers.transpiler.cpp_nodes.asignacion import visit_asignacion as _visit_asignacion
from cobra.transpilers.transpiler.cpp_nodes.condicional import visit_condicional as _visit_condicional
from cobra.transpilers.transpiler.cpp_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from cobra.transpilers.transpiler.cpp_nodes.funcion import visit_funcion as _visit_funcion
from cobra.transpilers.transpiler.cpp_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from cobra.transpilers.transpiler.cpp_nodes.holobit import visit_holobit as _visit_holobit
from cobra.transpilers.transpiler.cpp_nodes.clase import visit_clase as _visit_clase
from cobra.transpilers.transpiler.cpp_nodes.metodo import visit_metodo as _visit_metodo
from cobra.transpilers.transpiler.cpp_nodes.yield_ import visit_yield as _visit_yield
from cobra.transpilers.transpiler.cpp_nodes.romper import visit_romper as _visit_romper
from cobra.transpilers.transpiler.cpp_nodes.continuar import visit_continuar as _visit_continuar
from cobra.transpilers.transpiler.cpp_nodes.pasar import visit_pasar as _visit_pasar
from cobra.transpilers.transpiler.cpp_nodes.switch import visit_switch as _visit_switch


def visit_assert(self, nodo):
    cond = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"assert({cond});")


def visit_del(self, nodo):
    nombre = self.obtener_valor(nodo.objetivo)
    self.agregar_linea(f"/* del {nombre} */")


def visit_global(self, nodo):
    nombres = ", ".join(nodo.nombres)
    self.agregar_linea(f"// global {nombres}")


def visit_nolocal(self, nodo):
    nombres = ", ".join(nodo.nombres)
    self.agregar_linea(f"// nonlocal {nombres}")


def visit_with(self, nodo):
    self.agregar_linea("{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_import_desde(self, nodo):
    alias = f" {nodo.alias}" if nodo.alias else ""
    self.agregar_linea(f"// from {nodo.modulo} import {nodo.nombre}{alias}")


class TranspiladorCPP(BaseTranspiler):
    """Transpila el AST de Cobra a código C++ sencillo."""

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
        elif isinstance(nodo, NodoAtributo):
            obj = self.obtener_valor(nodo.objeto)
            return f"{obj}.{nodo.nombre}"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre_clase}({args})"
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
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
        elif isinstance(nodo, NodoLambda):
            params = ", ".join(nodo.parametros)
            cuerpo = self.obtener_valor(nodo.cuerpo)
            return f"[=]({params}){{ return {cuerpo}; }}"
        elif isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"std::vector{{{elems}}}"
        elif isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"{{{self.obtener_valor(k)}, {self.obtener_valor(v)}}}"
                for k, v in nodo.elementos
            )
            return f"std::map{{{pares}}}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            nodo.aceptar(self)
        return "\n".join(self.codigo)


# Asignar los visitantes externos a la clase
TranspiladorCPP.visit_asignacion = _visit_asignacion
TranspiladorCPP.visit_condicional = _visit_condicional
TranspiladorCPP.visit_bucle_mientras = _visit_bucle_mientras
TranspiladorCPP.visit_funcion = _visit_funcion
TranspiladorCPP.visit_llamada_funcion = _visit_llamada_funcion
TranspiladorCPP.visit_holobit = _visit_holobit
TranspiladorCPP.visit_clase = _visit_clase
TranspiladorCPP.visit_metodo = _visit_metodo
TranspiladorCPP.visit_yield = _visit_yield
TranspiladorCPP.visit_romper = _visit_romper
TranspiladorCPP.visit_continuar = _visit_continuar
TranspiladorCPP.visit_pasar = _visit_pasar
TranspiladorCPP.visit_assert = visit_assert
TranspiladorCPP.visit_del = visit_del
TranspiladorCPP.visit_global = visit_global
TranspiladorCPP.visit_nolocal = visit_nolocal
TranspiladorCPP.visit_no_local = visit_nolocal
TranspiladorCPP.visit_with = visit_with
TranspiladorCPP.visit_import_desde = visit_import_desde
TranspiladorCPP.visit_switch = _visit_switch
