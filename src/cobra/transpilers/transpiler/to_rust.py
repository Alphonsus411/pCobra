"""Transpilador que genera código Rust a partir de Cobra.

Los parámetros de tipo de Cobra se convierten en genéricos idiomáticos de Rust."""

from core.ast_nodes import (
    NodoLista,
    NodoDiccionario,
    NodoValor,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoAtributo,
    NodoInstancia,
    NodoThrow,
    NodoTryCatch,
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoLambda,
    NodoWith,
    NodoImportDesde,
    NodoOption,
    NodoSwitch,
    NodoCase,
    NodoPattern,
    NodoGuard,
    NodoInterface,
)
from cobra.lexico.lexer import TipoToken
from core.visitor import NodeVisitor
from cobra.transpilers.base import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros

from cobra.transpilers.transpiler.rust_nodes.asignacion import visit_asignacion as _visit_asignacion
from cobra.transpilers.transpiler.rust_nodes.condicional import visit_condicional as _visit_condicional
from cobra.transpilers.transpiler.rust_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from cobra.transpilers.transpiler.rust_nodes.funcion import visit_funcion as _visit_funcion
from cobra.transpilers.transpiler.rust_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from cobra.transpilers.transpiler.rust_nodes.holobit import visit_holobit as _visit_holobit
from cobra.transpilers.transpiler.rust_nodes.clase import visit_clase as _visit_clase
from cobra.transpilers.transpiler.rust_nodes.metodo import visit_metodo as _visit_metodo
from cobra.transpilers.transpiler.rust_nodes.yield_ import visit_yield as _visit_yield
from cobra.transpilers.transpiler.rust_nodes.romper import visit_romper as _visit_romper
from cobra.transpilers.transpiler.rust_nodes.continuar import visit_continuar as _visit_continuar
from cobra.transpilers.transpiler.rust_nodes.pasar import visit_pasar as _visit_pasar
from cobra.transpilers.transpiler.rust_nodes.switch import visit_switch as _visit_switch
from cobra.transpilers.transpiler.rust_nodes.try_catch import visit_try_catch as _visit_try_catch
from cobra.transpilers.transpiler.rust_nodes.throw import visit_throw as _visit_throw
from cobra.transpilers.transpiler.rust_nodes.option import visit_option as _visit_option


def visit_assert(self, nodo):
    cond = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"assert!({cond});")


def visit_del(self, nodo):
    nombre = self.obtener_valor(nodo.objetivo)
    self.agregar_linea(f"// del {nombre}")


def visit_global(self, nodo):
    """Marca variables globales en Rust."""
    nombres = ", ".join(nodo.nombres)
    # En Rust no existe un equivalente directo a "global" de Python,
    # por lo que se añade un comentario indicando su presencia.
    self.agregar_linea(f"// global {nombres}")


def visit_nolocal(self, nodo):
    """Marca variables no locales en Rust."""
    nombres = ", ".join(nodo.nombres)
    # Rust carece de un concepto equivalente a "nonlocal".
    # Se inserta un comentario para mantener la información de ámbito.
    self.agregar_linea(f"// nonlocal {nombres}")


def visit_with(self, nodo):
    self.agregar_linea("{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_import_desde(self, nodo):
    alias = f" as {nodo.alias}" if nodo.alias else ""
    self.agregar_linea(f"use {nodo.modulo}::{nodo.nombre}{alias};")


def visit_interface(self, nodo):
    """Transpila una interfaz a un trait de Rust."""
    self.agregar_linea(f"trait {nodo.nombre} {{")
    self.indent += 1
    for metodo in getattr(nodo, "metodos", []):
        params = ", ".join(f"{p}: &dyn std::any::Any" for p in metodo.parametros)
        self.agregar_linea(f"fn {metodo.nombre}({params});")
    self.indent -= 1
    self.agregar_linea("}")


class TranspiladorRust(BaseTranspiler):
    """Transpila el AST de Cobra a código Rust sencillo."""

    def __init__(self):
        self.codigo = []
        self.indent = 0

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def obtener_valor(self, nodo):
        match nodo:
            case NodoValor():
                return str(nodo.valor)
            case NodoAtributo():
                obj = self.obtener_valor(nodo.objeto)
                return f"{obj}.{nodo.nombre}"
            case NodoInstancia():
                args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
                return f"{nodo.nombre_clase}::new({args})"
            case NodoIdentificador():
                return nodo.nombre
            case NodoOperacionBinaria():
                izq = self.obtener_valor(nodo.izquierda)
                der = self.obtener_valor(nodo.derecha)
                op_map = {TipoToken.AND: "&&", TipoToken.OR: "||"}
                op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
                return f"{izq} {op} {der}"
            case NodoOperacionUnaria():
                val = self.obtener_valor(nodo.operando)
                op = "!" if nodo.operador.tipo == TipoToken.NOT else nodo.operador.valor
                return f"{op}{val}" if op != "!" else f"!{val}"
            case NodoLambda():
                params = ", ".join(f"{p}: impl std::any::Any" for p in nodo.parametros)
                cuerpo = self.obtener_valor(nodo.cuerpo)
                return f"|{', '.join(nodo.parametros)}| {{ {cuerpo} }}"
            case NodoOption():
                if nodo.valor is None:
                    return "None"
                return f"Some({self.obtener_valor(nodo.valor)})"
            case NodoLista():
                elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
                return f"vec![{elems}]"
            case NodoDiccionario():
                pares = ", ".join(
                    f"({self.obtener_valor(k)}, {self.obtener_valor(v)})"
                    for k, v in nodo.elementos
                )
                return f"std::collections::HashMap::from([{pares}])"
            case NodoPattern():
                if isinstance(nodo.valor, list):
                    elems = ", ".join(self.obtener_valor(p) for p in nodo.valor)
                    return f"({elems})"
                else:
                    return "_" if nodo.valor == "_" else self.obtener_valor(nodo.valor)
            case NodoGuard():
                patron = self.obtener_valor(nodo.patron)
                guardia = self.obtener_valor(nodo.condicion)
                return f"{patron} if {guardia}"
            case _:
                return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            nodo.aceptar(self)
        return "\n".join(self.codigo)


# Asignar los visitantes externos a la clase
TranspiladorRust.visit_asignacion = _visit_asignacion
TranspiladorRust.visit_condicional = _visit_condicional
TranspiladorRust.visit_bucle_mientras = _visit_bucle_mientras
TranspiladorRust.visit_funcion = _visit_funcion
TranspiladorRust.visit_llamada_funcion = _visit_llamada_funcion
TranspiladorRust.visit_holobit = _visit_holobit
TranspiladorRust.visit_clase = _visit_clase
TranspiladorRust.visit_metodo = _visit_metodo
TranspiladorRust.visit_interface = visit_interface
TranspiladorRust.visit_yield = _visit_yield
TranspiladorRust.visit_romper = _visit_romper
TranspiladorRust.visit_continuar = _visit_continuar
TranspiladorRust.visit_pasar = _visit_pasar
TranspiladorRust.visit_assert = visit_assert
TranspiladorRust.visit_del = visit_del
TranspiladorRust.visit_global = visit_global
TranspiladorRust.visit_nolocal = visit_nolocal
TranspiladorRust.visit_no_local = visit_nolocal
TranspiladorRust.visit_with = visit_with
TranspiladorRust.visit_import_desde = visit_import_desde
TranspiladorRust.visit_switch = _visit_switch
TranspiladorRust.visit_try_catch = _visit_try_catch
TranspiladorRust.visit_throw = _visit_throw
TranspiladorRust.visit_option = _visit_option
