"""Transpilador que genera código C++ a partir de Cobra.

Los parámetros de tipo de Cobra se traducen a plantillas ``template`` propias
de C++."""

from pcobra.core.ast_nodes import (
    NodoLista,
    NodoDiccionario,
    NodoListaTipo,
    NodoDiccionarioTipo,
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
    NodoOption,
    NodoPattern,
    NodoInterface,
    NodoGarantia,
    NodoDecorador,
    NodoImport,
    NodoUsar,
    NodoThrow,
    NodoTryCatch,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
)
from pcobra.cobra.core import TipoToken
from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.common.utils import (
    BaseTranspiler,
    get_runtime_hooks,
    get_standard_imports,
)
from pcobra.core.optimizations import optimize_constants, remove_dead_code, inline_functions
from pcobra.cobra.macro import expandir_macros

from pcobra.cobra.transpilers.transpiler.cpp_nodes.asignacion import visit_asignacion as _visit_asignacion
from pcobra.cobra.transpilers.transpiler.cpp_nodes.condicional import visit_condicional as _visit_condicional
from pcobra.cobra.transpilers.transpiler.cpp_nodes.garantia import visit_garantia as _visit_garantia
from pcobra.cobra.transpilers.transpiler.cpp_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from pcobra.cobra.transpilers.transpiler.cpp_nodes.funcion import visit_funcion as _visit_funcion
from pcobra.cobra.transpilers.transpiler.cpp_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from pcobra.cobra.transpilers.transpiler.cpp_nodes.holobit import visit_holobit as _visit_holobit
from pcobra.cobra.transpilers.transpiler.cpp_nodes.clase import visit_clase as _visit_clase
from pcobra.cobra.transpilers.transpiler.cpp_nodes.metodo import visit_metodo as _visit_metodo
from pcobra.cobra.transpilers.transpiler.cpp_nodes.yield_ import visit_yield as _visit_yield
from pcobra.cobra.transpilers.transpiler.cpp_nodes.romper import visit_romper as _visit_romper
from pcobra.cobra.transpilers.transpiler.cpp_nodes.continuar import visit_continuar as _visit_continuar
from pcobra.cobra.transpilers.transpiler.cpp_nodes.pasar import visit_pasar as _visit_pasar
from pcobra.cobra.transpilers.transpiler.cpp_nodes.switch import visit_switch as _visit_switch
from pcobra.cobra.transpilers.transpiler.cpp_nodes.option import visit_option as _visit_option
from pcobra.cobra.transpilers.transpiler.cpp_nodes.pattern import visit_pattern as _visit_pattern
from pcobra.cobra.transpilers.transpiler.cpp_nodes.retorno import (
    visit_retorno as _visit_retorno,
)


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
    if getattr(nodo, "asincronico", False):
        ctx = self.obtener_valor(nodo.contexto)
        alias = f" as {nodo.alias}" if nodo.alias else ""
        self.agregar_linea(
            f"// async with {ctx}{alias} no tiene equivalente directo en C++"
        )
    self.agregar_linea("{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_import_desde(self, nodo):
    alias = f" {nodo.alias}" if nodo.alias else ""
    self.agregar_linea(f"// from {nodo.modulo} import {nodo.nombre}{alias}")


def visit_lista_tipo(self, nodo):
    elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
    self.agregar_linea(
        f"std::vector<{nodo.tipo}> {nodo.nombre} = {{{elems}}};"
    )


def visit_diccionario_tipo(self, nodo):
    pares = ", ".join(
        f"{{{self.obtener_valor(k)}, {self.obtener_valor(v)}}}" for k, v in nodo.elementos
    )
    self.agregar_linea(
        f"std::map<{nodo.tipo_clave}, {nodo.tipo_valor}> {nodo.nombre} = {{{pares}}};"
    )




def visit_interface(self, nodo):
    """Transpila una interfaz a una struct con métodos virtuales puros."""
    self.agregar_linea(f"struct {nodo.nombre} {{")
    self.indent += 1
    for metodo in getattr(nodo, "metodos", []):
        params = ", ".join(f"auto {p}" for p in metodo.parametros)
        self.agregar_linea(f"virtual void {metodo.nombre}({params}) = 0;")
    self.indent -= 1
    self.agregar_linea("};")



def visit_decorador(self, nodo: NodoDecorador):
    expresion = self.obtener_valor(getattr(nodo, "expresion", nodo))
    self.agregar_linea(f"// @decorador {expresion}")


def visit_import(self, nodo: NodoImport):
    self.agregar_linea(f"// import {nodo.ruta}")


def visit_usar(self, nodo: NodoUsar):
    self.agregar_linea(f"// usar {nodo.modulo}")


def visit_throw(self, nodo: NodoThrow):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"throw std::runtime_error({valor});")


def visit_try_catch(self, nodo: NodoTryCatch):
    nombre = nodo.nombre_excepcion or "error"
    self.agregar_linea("try {")
    self.indent += 1
    for inst in nodo.bloque_try:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea(f"}} catch (const std::runtime_error& {nombre}) {{")
    self.indent += 1
    for inst in nodo.bloque_catch:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")


def visit_proyectar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobra_proyectar({hb}, {modo});")


def visit_transformar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    op = self.obtener_valor(nodo.operacion)
    params = ", ".join(f"cobra_runtime_arg({self.obtener_valor(p)})" for p in nodo.parametros)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobra_transformar({hb}, {op}, {{{params}}});")


def visit_graficar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobra_graficar({hb});")

class TranspiladorCPP(BaseTranspiler):
    """Transpila el AST de Cobra a código C++ sencillo."""

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
            if isinstance(nodo.valor, str):
                return '"' + nodo.valor.replace("\\", "\\\\").replace('"', '\\"') + '"'
            if nodo.valor is None:
                return "nullptr"
            if isinstance(nodo.valor, bool):
                return str(nodo.valor).lower()
            return str(nodo.valor)
        elif isinstance(nodo, NodoAtributo):
            obj = self.obtener_valor(nodo.objeto)
            return f"{obj}.{nodo.nombre}"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre_clase}({args})"
        elif isinstance(nodo, NodoProyectar):
            hb = self.obtener_valor(nodo.holobit)
            modo = self.obtener_valor(nodo.modo)
            self.usa_runtime_holobit = True
            return f"cobra_proyectar({hb}, {modo})"
        elif isinstance(nodo, NodoTransformar):
            hb = self.obtener_valor(nodo.holobit)
            op = self.obtener_valor(nodo.operacion)
            self.usa_runtime_holobit = True
            params = ", ".join(f"cobra_runtime_arg({self.obtener_valor(p)})" for p in nodo.parametros)
            return f"cobra_transformar({hb}, {op}, {{{params}}})"
        elif isinstance(nodo, NodoGraficar):
            hb = self.obtener_valor(nodo.holobit)
            self.usa_runtime_holobit = True
            return f"cobra_graficar({hb})"
        elif getattr(nodo.__class__, "__name__", "") == "NodoHolobit":
            valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
            self.usa_runtime_holobit = True
            return f"cobra_holobit({{ {valores} }})"
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
        elif isinstance(nodo, NodoOption):
            if nodo.valor is None:
                return "std::nullopt"
            return self.obtener_valor(nodo.valor)
        elif isinstance(nodo, NodoPattern):
            if isinstance(nodo.valor, list):
                elems = ", ".join(self.obtener_valor(e) for e in nodo.valor)
                return f"({elems})"
            return "_" if nodo.valor == "_" else self.obtener_valor(nodo.valor)
        elif isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"std::vector{{{elems}}}"
        elif isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"{{{self.obtener_valor(k)}, {self.obtener_valor(v)}}}"
                for k, v in nodo.elementos
            )
            return f"std::map{{{pares}}}"
        elif isinstance(nodo, NodoListaTipo):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"std::vector<{nodo.tipo}>{{{elems}}}"
        elif isinstance(nodo, NodoDiccionarioTipo):
            pares = ", ".join(
                f"{{{self.obtener_valor(k)}, {self.obtener_valor(v)}}}" for k, v in nodo.elementos
            )
            return f"std::map<{nodo.tipo_clave}, {nodo.tipo_valor}>{{{pares}}}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(optimize_constants(nodos))
        for nodo in nodos:
            nodo.aceptar(self)
        lineas = list(self.codigo)

        imports = get_standard_imports("cpp")
        if imports:
            lineas = list(imports) + [""] + lineas

        if self.usa_runtime_holobit:
            hooks = get_runtime_hooks("cpp")
            if hooks:
                lineas = [
                    "#include <algorithm>",
                    "#include <cmath>",
                    "#include <cctype>",
                    "#include <initializer_list>",
                    "#include <iostream>",
                    "#include <sstream>",
                    "#include <string>",
                    "#include <vector>",
                    "",
                ] + hooks + [""] + lineas
        return "\n".join(lineas)


CPP_FEATURE_NODE_SUPPORT = {
    "decoradores": ("visit_decorador", "visit_funcion"),
    "imports_corelibs": ("visit_usar", "visit_import", "visit_llamada_funcion"),
    "manejo_errores": ("visit_try_catch", "visit_throw"),
    "async": (),
    "tipos_compuestos": ("visit_lista", "visit_diccionario", "visit_lista_tipo", "visit_diccionario_tipo"),
}


# Asignar los visitantes externos a la clase
TranspiladorCPP.visit_asignacion = _visit_asignacion
TranspiladorCPP.visit_condicional = _visit_condicional
TranspiladorCPP.visit_garantia = _visit_garantia
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
TranspiladorCPP.visit_lista_tipo = visit_lista_tipo
TranspiladorCPP.visit_diccionario_tipo = visit_diccionario_tipo
TranspiladorCPP.visit_interface = visit_interface
TranspiladorCPP.visit_option = _visit_option
TranspiladorCPP.visit_pattern = _visit_pattern
TranspiladorCPP.visit_retorno = _visit_retorno
TranspiladorCPP.visit_decorador = visit_decorador
TranspiladorCPP.visit_import = visit_import
TranspiladorCPP.visit_usar = visit_usar
TranspiladorCPP.visit_throw = visit_throw
TranspiladorCPP.visit_try_catch = visit_try_catch

TranspiladorCPP.visit_proyectar = visit_proyectar
TranspiladorCPP.visit_transformar = visit_transformar
TranspiladorCPP.visit_graficar = visit_graficar
