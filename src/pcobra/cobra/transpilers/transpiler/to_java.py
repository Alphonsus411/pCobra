"""Transpilador sencillo de Cobra a Java."""

from pcobra.cobra.core.ast_nodes import (
    NodoDecorador,
    NodoImport,
    NodoUsar,
    NodoThrow,
    NodoTryCatch,
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
from pcobra.cobra.transpilers.common.utils import (
    ast_requires_holobit_runtime,
    BaseTranspiler,
    get_runtime_hooks,
    get_standard_imports,
)
from pcobra.cobra.core.optimizations import optimize_constants, remove_dead_code, inline_functions
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
    self.usa_runtime_holobit = True
    self.agregar_linea(f"Object {nombre} = cobra_holobit(new double[]{{{valores}}});")


def visit_proyectar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobra_proyectar({hb}, {modo});")


def visit_transformar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    op = self.obtener_valor(nodo.operacion)
    params = ", ".join(self.obtener_valor(p) for p in nodo.parametros)
    args = f", {params}" if params else ""
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobra_transformar({hb}, {op}{args});")


def visit_graficar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobra_graficar({hb});")


def visit_decorador(self, nodo: NodoDecorador):
    expresion = self.obtener_valor(getattr(nodo, "expresion", nodo))
    self.agregar_linea(f"// @decorador {expresion}")


def visit_import(self, nodo: NodoImport):
    self.agregar_linea(f"// import {nodo.ruta}")


def visit_usar(self, nodo: NodoUsar):
    self.agregar_linea(f"// usar {nodo.modulo}")


def visit_throw(self, nodo: NodoThrow):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"throw new UnsupportedOperationException(String.valueOf({valor}));")


def visit_try_catch(self, nodo: NodoTryCatch):
    nombre = nodo.nombre_excepcion or "error"
    self.agregar_linea("try {")
    self.indent += 1
    for inst in nodo.bloque_try:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea(f"}} catch (Exception {nombre}) {{")
    self.indent += 1
    for inst in nodo.bloque_catch:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_valor(self, nodo: NodoValor):
    self.agregar_linea(f"{self.obtener_valor(nodo)};")

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
        elif isinstance(nodo, NodoHolobit):
            valores = ", ".join(self.obtener_valor(v) for v in nodo.valores or [])
            self.usa_runtime_holobit = True
            return f"cobra_holobit(new double[]{{{valores}}})"
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
        self.codigo = []
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))

        funciones = []
        otros = []

        for nodo in nodos:
            if nodo.__class__.__name__ == "NodoFuncion":
                funciones.append(nodo)
            else:
                otros.append(nodo)

        imports = get_standard_imports("java")
        for imp in imports:
            self.agregar_linea(imp)
        if imports:
            self.agregar_linea("")

        self.agregar_linea("public class Main {")
        self.indent += 1

        self.usa_runtime_holobit = ast_requires_holobit_runtime(nodos)
        if self.usa_runtime_holobit:
            for hook in get_runtime_hooks("java"):
                self.agregar_linea(hook)

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


JAVA_FEATURE_NODE_SUPPORT = {
    "decoradores": ("visit_decorador", "visit_funcion"),
    "imports_corelibs": ("visit_usar", "visit_import", "visit_llamada_funcion"),
    "manejo_errores": ("visit_try_catch", "visit_throw"),
    "async": (),
    "tipos_compuestos": (),
}


# Asignar visitantes
for nombre, funcion in java_nodes.items():
    setattr(TranspiladorJava, f"visit_{nombre}", funcion)

TranspiladorJava.visit_decorador = visit_decorador
TranspiladorJava.visit_import = visit_import
TranspiladorJava.visit_usar = visit_usar
TranspiladorJava.visit_throw = visit_throw
TranspiladorJava.visit_try_catch = visit_try_catch
TranspiladorJava.visit_valor = visit_valor
