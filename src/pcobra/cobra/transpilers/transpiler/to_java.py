"""Transpilador sencillo de Cobra a Java."""

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
    NodoLlamadaMetodo,
    NodoInstancia,
    NodoHolobit,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
)
from pcobra.cobra.core import TipoToken
from pcobra.cobra.transpilers.common.utils import BaseTranspiler
from pcobra.core.optimizations import optimize_constants, remove_dead_code, inline_functions
from pcobra.cobra.macro import expandir_macros

from pcobra.cobra.transpilers.transpiler.java_nodes.asignacion import (
    visit_asignacion as _visit_asignacion,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.funcion import (
    visit_funcion as _visit_funcion,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.llamada_funcion import (
    visit_llamada_funcion as _visit_llamada_funcion,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.imprimir import (
    visit_imprimir as _visit_imprimir,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.condicional import (
    visit_condicional as _visit_condicional,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.bucle_mientras import (
    visit_bucle_mientras as _visit_bucle_mientras,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.for_ import visit_for as _visit_for
from pcobra.cobra.transpilers.transpiler.java_nodes.clase import visit_clase as _visit_clase
from pcobra.cobra.transpilers.transpiler.java_nodes.metodo import visit_metodo as _visit_metodo
from pcobra.cobra.transpilers.transpiler.java_nodes.retorno import (
    visit_retorno as _visit_retorno,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.romper import visit_romper as _visit_romper
from pcobra.cobra.transpilers.transpiler.java_nodes.continuar import (
    visit_continuar as _visit_continuar,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.llamada_metodo import (
    visit_llamada_metodo as _visit_llamada_metodo,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.instancia import (
    visit_instancia as _visit_instancia,
)



def visit_holobit(self, nodo):
    valores = ", ".join(str(v) for v in nodo.valores or [])
    nombre = nodo.nombre or "hb"
    self.agregar_linea(f"double[] {nombre} = new double[]{{{valores}}};")


def visit_proyectar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobraProyectar({hb}, {modo});")


def visit_transformar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    op = self.obtener_valor(nodo.operacion)
    params = ", ".join(self.obtener_valor(p) for p in nodo.parametros)
    args = f", {params}" if params else ""
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobraTransformar({hb}, {op}{args});")


def visit_graficar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobraGraficar({hb});")

java_nodes = {
    "asignacion": _visit_asignacion,
    "funcion": _visit_funcion,
    "llamada_funcion": _visit_llamada_funcion,
    "imprimir": _visit_imprimir,
    "condicional": _visit_condicional,
    "bucle_mientras": _visit_bucle_mientras,
    "for": _visit_for,
    "clase": _visit_clase,
    "metodo": _visit_metodo,
    "retorno": _visit_retorno,
    "romper": _visit_romper,
    "continuar": _visit_continuar,
    "llamada_metodo": _visit_llamada_metodo,
    "instancia": _visit_instancia,
    "holobit": visit_holobit,
    "proyectar": visit_proyectar,
    "transformar": visit_transformar,
    "graficar": visit_graficar,
}


class TranspiladorJava(BaseTranspiler):
    def __init__(self):
        self.codigo = []
        self.indent = 0
        self.usa_runtime_holobit = False

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor):
            valor = nodo.valor
            if isinstance(valor, str):
                return f"\"{valor}\""
            if isinstance(valor, bool):
                return str(valor).lower()
            if valor is None:
                return "null"
            return str(valor)
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}.{nodo.nombre}"
        elif isinstance(nodo, NodoLlamadaFuncion):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre}({args})"
        elif isinstance(nodo, NodoLlamadaMetodo):
            obj = self.obtener_valor(nodo.objeto)
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{obj}.{nodo.nombre_metodo}({args})"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"new {nodo.nombre_clase}({args})"
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

        funciones = []
        otros = []

        for nodo in nodos:
            if nodo.__class__.__name__ == "NodoFuncion":
                funciones.append(nodo)
            else:
                otros.append(nodo)

        self.agregar_linea("public class Main {")
        self.indent += 1

        self.usa_runtime_holobit = any(n.__class__.__name__ in {"NodoProyectar", "NodoTransformar", "NodoGraficar"} for n in nodos)
        if self.usa_runtime_holobit:
            self.agregar_linea("private static void cobraProyectar(Object hb, Object modo) {")
            self.indent += 1
            self.agregar_linea('System.out.println("[cobra::proyectar] " + hb + " " + modo);')
            self.indent -= 1
            self.agregar_linea("}")
            self.agregar_linea("private static void cobraTransformar(Object hb, Object op, Object... params) {")
            self.indent += 1
            self.agregar_linea('System.out.println("[cobra::transformar] " + hb + " " + op);')
            self.indent -= 1
            self.agregar_linea("}")
            self.agregar_linea("private static void cobraGraficar(Object hb) {")
            self.indent += 1
            self.agregar_linea('System.out.println("[cobra::graficar] " + hb);')
            self.indent -= 1
            self.agregar_linea("}")

        for f in funciones:
            f.aceptar(self)

        self.agregar_linea("public static void main(String[] args) {")
        self.indent += 1
        for nodo in otros:
            if hasattr(nodo, "aceptar"):
                nodo.aceptar(self)
            else:
                metodo = getattr(
                    self, f"visit_{nodo.__class__.__name__[4:].lower()}", None
                )
                if metodo:
                    metodo(nodo)
        self.indent -= 1
        self.agregar_linea("}")

        self.indent -= 1
        self.agregar_linea("}")
        return "\n".join(self.codigo)


# Asignar visitantes
for nombre, funcion in java_nodes.items():
    setattr(TranspiladorJava, f"visit_{nombre}", funcion)

