"""Transpilador básico de Cobra a C."""

from core.ast_nodes import (
    NodoLista,
    NodoDiccionario,
    NodoValor,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoAtributo,
    NodoInstancia,
)
from cobra.lexico.lexer import TipoToken
from core.visitor import NodeVisitor
from src.cobra.transpilers.base import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros


def visit_asignacion(self, nodo):
    nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
    valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
    if isinstance(nombre_raw, NodoAtributo):
        nombre = self.obtener_valor(nombre_raw)
        self.agregar_linea(f"{nombre} = {self.obtener_valor(valor)};")
    else:
        nombre = nombre_raw
        self.agregar_linea(f"int {nombre} = {self.obtener_valor(valor)};")


def visit_funcion(self, nodo):
    params = ", ".join(f"int {p}" for p in nodo.parametros)
    self.agregar_linea(f"void {nodo.nombre}({params}) {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_llamada_funcion(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"{nodo.nombre}({args});")


def visit_condicional(self, nodo):
    cuerpo_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", []))
    cuerpo_sino = getattr(nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", []))
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"if ({condicion}) {{")
    self.indent += 1
    for instr in cuerpo_si:
        instr.aceptar(self)
    self.indent -= 1
    if cuerpo_sino:
        self.agregar_linea("} else {")
        self.indent += 1
        for instr in cuerpo_sino:
            instr.aceptar(self)
        self.indent -= 1
        self.agregar_linea("}")
    else:
        self.agregar_linea("}")


def visit_bucle_mientras(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"while ({condicion}) {{")
    self.indent += 1
    for instr in nodo.cuerpo:
        instr.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


c_nodes = {
    "asignacion": visit_asignacion,
    "funcion": visit_funcion,
    "llamada_funcion": visit_llamada_funcion,
    "condicional": visit_condicional,
    "bucle_mientras": visit_bucle_mientras,
}


class TranspiladorC(BaseTranspiler):
    """Transpila el AST de Cobra a un C muy básico."""

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
        elif isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"{{{elems}}}"
        elif isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"{{{self.obtener_valor(k)}, {self.obtener_valor(v)}}}"
                for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
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


for nombre, funcion in c_nodes.items():
    setattr(TranspiladorC, f"visit_{nombre}", funcion)
