"""Transpilador que genera código Rust a partir de Cobra."""

from src.core.ast_nodes import (
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
from src.cobra.lexico.lexer import TipoToken
from src.core.visitor import NodeVisitor
from src.core.optimizations import optimize_constants, remove_dead_code
from src.cobra.macro import expandir_macros

from .rust_nodes.asignacion import visit_asignacion as _visit_asignacion
from .rust_nodes.condicional import visit_condicional as _visit_condicional
from .rust_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from .rust_nodes.funcion import visit_funcion as _visit_funcion
from .rust_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from .rust_nodes.holobit import visit_holobit as _visit_holobit
from .rust_nodes.clase import visit_clase as _visit_clase
from .rust_nodes.metodo import visit_metodo as _visit_metodo
from .rust_nodes.yield_ import visit_yield as _visit_yield
from .rust_nodes.romper import visit_romper as _visit_romper
from .rust_nodes.continuar import visit_continuar as _visit_continuar
from .rust_nodes.pasar import visit_pasar as _visit_pasar

def visit_assert(self, nodo):
    cond = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"assert!({cond});")

def visit_del(self, nodo):
    nombre = self.obtener_valor(nodo.objetivo)
    self.agregar_linea(f"// del {nombre}")

def visit_global(self, nodo):
    pass

def visit_nolocal(self, nodo):
    pass

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


class TranspiladorRust(NodeVisitor):
    """Transpila el AST de Cobra a código Rust sencillo."""

    def __init__(self):
        self.codigo = []
        self.indent = 0

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
            return f"{nodo.nombre_clase}::new({args})"
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
            params = ", ".join(f"{p}: impl std::any::Any" for p in nodo.parametros)
            cuerpo = self.obtener_valor(nodo.cuerpo)
            return f"|{', '.join(nodo.parametros)}| {{ {cuerpo} }}"
        elif isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"vec![{elems}]"
        elif isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"({self.obtener_valor(k)}, {self.obtener_valor(v)})" for k, v in nodo.elementos
            )
            return f"std::collections::HashMap::from([{pares}])"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(optimize_constants(nodos))
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
TranspiladorRust.visit_yield = _visit_yield
TranspiladorRust.visit_romper = _visit_romper
TranspiladorRust.visit_continuar = _visit_continuar
TranspiladorRust.visit_pasar = _visit_pasar
TranspiladorRust.visit_assert = visit_assert
TranspiladorRust.visit_del = visit_del
TranspiladorRust.visit_global = visit_global
TranspiladorRust.visit_nolocal = visit_nolocal
TranspiladorRust.visit_with = visit_with
TranspiladorRust.visit_import_desde = visit_import_desde
