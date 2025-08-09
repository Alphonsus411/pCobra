"""Transpilador que genera código JavaScript a partir de Cobra.

Los parámetros de tipo se omiten porque JavaScript no soporta genéricos de
forma nativa, por lo que se recurre a tipos dinámicos."""

from cobra.core.ast_nodes import (
    NodoLista,
    NodoDiccionario,
    NodoListaTipo,
    NodoDiccionarioTipo,
    NodoListaComprehension,
    NodoDiccionarioComprehension,
    NodoValor,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoAtributo,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoLambda,
    NodoWith,
    NodoImportDesde,
    NodoImport,
    NodoExport,
    NodoEsperar,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
    NodoOption,
    NodoPattern,
    NodoEnum,
    NodoInterface,
)
from cobra.core import TipoToken
from core.visitor import NodeVisitor
from cobra.transpilers.base import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros
from cobra.transpilers.import_helper import get_standard_imports
from cobra.transpilers.module_map import get_mapped_path

from cobra.transpilers.transpiler.js_nodes.asignacion import visit_asignacion as _visit_asignacion
from cobra.transpilers.transpiler.js_nodes.condicional import visit_condicional as _visit_condicional
from cobra.transpilers.transpiler.js_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from cobra.transpilers.transpiler.js_nodes.funcion import visit_funcion as _visit_funcion
from cobra.transpilers.transpiler.js_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from cobra.transpilers.transpiler.js_nodes.hilo import visit_hilo as _visit_hilo
from cobra.transpilers.transpiler.js_nodes.llamada_metodo import visit_llamada_metodo as _visit_llamada_metodo
from cobra.transpilers.transpiler.js_nodes.imprimir import visit_imprimir as _visit_imprimir
from cobra.transpilers.transpiler.js_nodes.retorno import visit_retorno as _visit_retorno
from cobra.transpilers.transpiler.js_nodes.holobit import visit_holobit as _visit_holobit
from cobra.transpilers.transpiler.js_nodes.for_ import visit_for as _visit_for
from cobra.transpilers.transpiler.js_nodes.lista import visit_lista as _visit_lista
from cobra.transpilers.transpiler.js_nodes.diccionario import visit_diccionario as _visit_diccionario
from cobra.transpilers.transpiler.js_nodes.elemento import visit_elemento as _visit_elemento
from cobra.transpilers.transpiler.js_nodes.clase import visit_clase as _visit_clase
from cobra.transpilers.transpiler.js_nodes.metodo import visit_metodo as _visit_metodo
from cobra.transpilers.transpiler.js_nodes.try_catch import visit_try_catch as _visit_try_catch
from cobra.transpilers.transpiler.js_nodes.throw import visit_throw as _visit_throw
from cobra.transpilers.transpiler.js_nodes.importar import visit_import as _visit_import
from cobra.transpilers.transpiler.js_nodes.instancia import visit_instancia as _visit_instancia
from cobra.transpilers.transpiler.js_nodes.atributo import visit_atributo as _visit_atributo
from cobra.transpilers.transpiler.js_nodes.proyectar import visit_proyectar as _visit_proyectar
from cobra.transpilers.transpiler.js_nodes.transformar import visit_transformar as _visit_transformar
from cobra.transpilers.transpiler.js_nodes.graficar import visit_graficar as _visit_graficar
from cobra.transpilers.transpiler.js_nodes.operacion_binaria import (
    visit_operacion_binaria as _visit_operacion_binaria,
)
from cobra.transpilers.transpiler.js_nodes.operacion_unaria import visit_operacion_unaria as _visit_operacion_unaria
from cobra.transpilers.transpiler.js_nodes.valor import visit_valor as _visit_valor
from cobra.transpilers.transpiler.js_nodes.identificador import visit_identificador as _visit_identificador
from cobra.transpilers.transpiler.js_nodes.para import visit_para as _visit_para
from cobra.transpilers.transpiler.js_nodes.decorador import visit_decorador as _visit_decorador
from cobra.transpilers.transpiler.js_nodes.yield_ import visit_yield as _visit_yield
from cobra.transpilers.transpiler.js_nodes.esperar import visit_esperar as _visit_esperar
from cobra.transpilers.transpiler.js_nodes.romper import visit_romper as _visit_romper
from cobra.transpilers.transpiler.js_nodes.continuar import visit_continuar as _visit_continuar
from cobra.transpilers.transpiler.js_nodes.pasar import visit_pasar as _visit_pasar
from cobra.transpilers.transpiler.js_nodes.switch import visit_switch as _visit_switch
from cobra.transpilers.transpiler.js_nodes.exportar import visit_export as _visit_export
from cobra.transpilers.transpiler.js_nodes.option import visit_option as _visit_option
from cobra.transpilers.transpiler.js_nodes.pattern import visit_pattern as _visit_pattern
from cobra.transpilers.transpiler.js_nodes.enum import visit_enum as _visit_enum


def visit_interface(self, nodo):
    """Transpila una interfaz como una clase sin implementación."""
    metodos = getattr(nodo, "metodos", [])
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(m, "variable") for m in metodos)
    self.agregar_linea(f"class {nodo.nombre} {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for metodo in metodos:
        params = ", ".join(metodo.parametros)
        self.agregar_linea(f"{metodo.nombre}({params}) {{}}")
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")


def visit_assert(self, nodo):
    cond = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"console.assert({cond});")


def visit_del(self, nodo):
    nombre = self.obtener_valor(nodo.objetivo)
    self.agregar_linea(f"delete {nombre};")


def visit_global(self, nodo):
    nombres = ", ".join(nodo.nombres)
    self.agregar_linea(f"// global {nombres}")


def visit_nolocal(self, nodo):
    nombres = ", ".join(nodo.nombres)
    self.agregar_linea(f"// nonlocal {nombres}")


def visit_with(self, nodo):
    ctx = self.obtener_valor(nodo.contexto)
    self.agregar_linea(f"{{ /* with {ctx} */")
    if self.usa_indentacion:
        self.indentacion += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")


def visit_import_desde(self, nodo):
    alias = f" as {nodo.alias}" if nodo.alias else ""
    modulo = get_mapped_path(nodo.modulo, "js")
    self.agregar_linea(f"import {{ {nodo.nombre}{alias} }} from '{modulo}';")


def visit_lista_tipo(self, nodo):
    elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
    self.agregar_linea(f"let {nodo.nombre} = [{elems}];")


def visit_diccionario_tipo(self, nodo):
    pares = ", ".join(
        f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
    )
    self.agregar_linea(f"let {nodo.nombre} = {{{pares}}};")


def visit_lista_comprehension(self, nodo):
    self.agregar_linea(self.obtener_valor(nodo))


def visit_diccionario_comprehension(self, nodo):
    self.agregar_linea(self.obtener_valor(nodo))


class TranspiladorJavaScript(BaseTranspiler):
    def __init__(self):
        # Incluir importaciones de modulos nativos
        self.codigo = get_standard_imports("js")
        self.indentacion = 0
        self.usa_indentacion = None

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def agregar_linea(self, linea):
        if self.usa_indentacion:
            self.codigo.append("    " * self.indentacion + linea)
        else:
            self.codigo.append(linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor):
            return str(nodo.valor)
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}.{nodo.nombre}"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"new {nodo.nombre_clase}({args})"
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoLlamadaFuncion):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre}({args})"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            return f"{izq} {nodo.operador.valor} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            return (
                f"!{val}"
                if nodo.operador.tipo == TipoToken.NOT
                else f"{nodo.operador.valor}{val}"
            )
        elif isinstance(nodo, NodoEsperar):
            val = self.obtener_valor(nodo.expresion)
            return f"await {val}"
        elif isinstance(nodo, NodoLambda):
            params = ", ".join(nodo.parametros)
            cuerpo = self.obtener_valor(nodo.cuerpo)
            return f"({params}) => {cuerpo}"
        elif isinstance(nodo, NodoOption):
            if nodo.valor is None:
                return "null"
            return self.obtener_valor(nodo.valor)
        elif isinstance(nodo, NodoPattern):
            if isinstance(nodo.valor, list):
                elems = ", ".join(self.obtener_valor(e) for e in nodo.valor)
                return f"({elems})"
            return "_" if nodo.valor == "_" else self.obtener_valor(nodo.valor)
        elif isinstance(nodo, NodoListaComprehension):
            expr = self.obtener_valor(nodo.expresion)
            it = self.obtener_valor(nodo.iterable)
            cond = (
                f".filter({nodo.variable} => {self.obtener_valor(nodo.condicion)})"
                if nodo.condicion
                else ""
            )
            return f"Array.from({it}){cond}.map({nodo.variable} => {expr})"
        elif isinstance(nodo, NodoDiccionarioComprehension):
            key = self.obtener_valor(nodo.clave)
            val = self.obtener_valor(nodo.valor)
            it = self.obtener_valor(nodo.iterable)
            cond = (
                f".filter({nodo.variable} => {self.obtener_valor(nodo.condicion)})"
                if nodo.condicion
                else ""
            )
            return (
                f"Object.fromEntries(Array.from({it}){cond}.map({nodo.variable} => [ {key}, {val} ]))"
            )
        elif isinstance(nodo, NodoLista) or isinstance(nodo, NodoDiccionario):
            temp = []
            original = self.codigo
            self.codigo = temp
            if isinstance(nodo, NodoLista):
                self.visit_lista(nodo)
            else:
                self.visit_diccionario(nodo)
            self.codigo = original
            return "".join(temp)
        elif isinstance(nodo, NodoListaTipo):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"[{elems}]"
        elif isinstance(nodo, NodoDiccionarioTipo):
            pares = ", ".join(
                f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
        else:
            return str(nodo)

    def transpilar(self, ast_raiz):
        ast_raiz = expandir_macros(ast_raiz)
        ast_raiz = remove_dead_code(inline_functions(optimize_constants(ast_raiz)))
        for nodo in ast_raiz:
            if hasattr(nodo, "aceptar"):
                nodo.aceptar(self)
            else:
                nombre = nodo.__class__.__name__
                if nombre.startswith("Nodo"):
                    nombre = nombre[4:]
                metodo = getattr(self, f"visit_{nombre.lower()}", None)
                if metodo:
                    metodo(nodo)
                else:
                    raise AttributeError(f"Nodo sin método aceptar: {nodo}")
        return "\n".join(self.codigo)


# Asignar los visitantes externos a la clase
TranspiladorJavaScript.visit_asignacion = _visit_asignacion
TranspiladorJavaScript.visit_condicional = _visit_condicional
TranspiladorJavaScript.visit_bucle_mientras = _visit_bucle_mientras
TranspiladorJavaScript.visit_funcion = _visit_funcion
TranspiladorJavaScript.visit_llamada_funcion = _visit_llamada_funcion
TranspiladorJavaScript.visit_hilo = _visit_hilo
TranspiladorJavaScript.visit_llamada_metodo = _visit_llamada_metodo
TranspiladorJavaScript.visit_imprimir = _visit_imprimir
TranspiladorJavaScript.visit_retorno = _visit_retorno
TranspiladorJavaScript.visit_holobit = _visit_holobit
TranspiladorJavaScript.visit_for = _visit_for
TranspiladorJavaScript.visit_lista = _visit_lista
TranspiladorJavaScript.visit_diccionario = _visit_diccionario
TranspiladorJavaScript.visit_elemento = _visit_elemento
TranspiladorJavaScript.visit_clase = _visit_clase
TranspiladorJavaScript.visit_metodo = _visit_metodo
TranspiladorJavaScript.visit_try_catch = _visit_try_catch
TranspiladorJavaScript.visit_throw = _visit_throw
TranspiladorJavaScript.visit_import = _visit_import
TranspiladorJavaScript.visit_instancia = _visit_instancia
TranspiladorJavaScript.visit_atributo = _visit_atributo
TranspiladorJavaScript.visit_proyectar = _visit_proyectar
TranspiladorJavaScript.visit_transformar = _visit_transformar
TranspiladorJavaScript.visit_graficar = _visit_graficar
TranspiladorJavaScript.visit_operacion_binaria = _visit_operacion_binaria
TranspiladorJavaScript.visit_operacion_unaria = _visit_operacion_unaria
TranspiladorJavaScript.visit_valor = _visit_valor
TranspiladorJavaScript.visit_identificador = _visit_identificador
TranspiladorJavaScript.visit_para = _visit_para
TranspiladorJavaScript.visit_decorador = _visit_decorador
TranspiladorJavaScript.visit_yield = _visit_yield
TranspiladorJavaScript.visit_romper = _visit_romper
TranspiladorJavaScript.visit_continuar = _visit_continuar
TranspiladorJavaScript.visit_pasar = _visit_pasar
TranspiladorJavaScript.visit_esperar = _visit_esperar
TranspiladorJavaScript.visit_switch = _visit_switch
TranspiladorJavaScript.visit_export = _visit_export
TranspiladorJavaScript.visit_assert = visit_assert
TranspiladorJavaScript.visit_del = visit_del
TranspiladorJavaScript.visit_global = visit_global
TranspiladorJavaScript.visit_nolocal = visit_nolocal
TranspiladorJavaScript.visit_no_local = visit_nolocal
TranspiladorJavaScript.visit_with = visit_with
TranspiladorJavaScript.visit_import_desde = visit_import_desde
TranspiladorJavaScript.visit_lista_tipo = visit_lista_tipo
TranspiladorJavaScript.visit_diccionario_tipo = visit_diccionario_tipo
TranspiladorJavaScript.visit_lista_comprehension = visit_lista_comprehension
TranspiladorJavaScript.visit_diccionario_comprehension = visit_diccionario_comprehension
TranspiladorJavaScript.visit_option = _visit_option
TranspiladorJavaScript.visit_pattern = _visit_pattern
TranspiladorJavaScript.visit_enum = _visit_enum
TranspiladorJavaScript.visit_interface = visit_interface

# Métodos de transpilación para tipos de nodos básicos
