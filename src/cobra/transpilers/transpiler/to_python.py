"""Transpilador que convierte código Cobra en código Python."""

from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoFor,
    NodoLista,
    NodoDiccionario,
    NodoListaComprehension,
    NodoDiccionarioComprehension,
    NodoListaTipo,
    NodoDiccionarioTipo,
    NodoClase,
    NodoMetodo,
    NodoValor,
    NodoRetorno,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoInstancia,
    NodoLlamadaMetodo,
    NodoLlamadaFuncion,
    NodoAtributo,
    NodoHilo,
    NodoTryCatch,
    NodoThrow,
    NodoImport,
    NodoExport,
    NodoImprimir,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoLambda,
    NodoWith,
    NodoImportDesde,
    NodoEsperar,
    NodoPattern,
    NodoGuard,
)
from cobra.parser.parser import Parser
from cobra.lexico.lexer import TipoToken, Lexer
from core.visitor import NodeVisitor
from cobra.transpilers.base import BaseTranspiler
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros
from cobra.transpilers.import_helper import get_standard_imports

from cobra.transpilers.transpiler.python_nodes.asignacion import visit_asignacion as _visit_asignacion
from cobra.transpilers.transpiler.python_nodes.condicional import visit_condicional as _visit_condicional
from cobra.transpilers.transpiler.python_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from cobra.transpilers.transpiler.python_nodes.for_ import visit_for as _visit_for
from cobra.transpilers.transpiler.python_nodes.funcion import visit_funcion as _visit_funcion
from cobra.transpilers.transpiler.python_nodes.llamada_funcion import (
    visit_llamada_funcion as _visit_llamada_funcion,
)
from cobra.transpilers.transpiler.python_nodes.llamada_metodo import visit_llamada_metodo as _visit_llamada_metodo
from cobra.transpilers.transpiler.python_nodes.imprimir import visit_imprimir as _visit_imprimir
from cobra.transpilers.transpiler.python_nodes.retorno import visit_retorno as _visit_retorno
from cobra.transpilers.transpiler.python_nodes.holobit import visit_holobit as _visit_holobit
from cobra.transpilers.transpiler.python_nodes.lista import visit_lista as _visit_lista
from cobra.transpilers.transpiler.python_nodes.diccionario import visit_diccionario as _visit_diccionario
from cobra.transpilers.transpiler.python_nodes.clase import visit_clase as _visit_clase
from cobra.transpilers.transpiler.python_nodes.metodo import visit_metodo as _visit_metodo
from cobra.transpilers.transpiler.python_nodes.try_catch import visit_try_catch as _visit_try_catch
from cobra.transpilers.transpiler.python_nodes.throw import visit_throw as _visit_throw
from cobra.transpilers.transpiler.python_nodes.importar import visit_import as _visit_import
from cobra.transpilers.transpiler.python_nodes.usar import visit_usar as _visit_usar
from cobra.transpilers.transpiler.python_nodes.hilo import visit_hilo as _visit_hilo
from cobra.transpilers.transpiler.python_nodes.instancia import visit_instancia as _visit_instancia
from cobra.transpilers.transpiler.python_nodes.atributo import visit_atributo as _visit_atributo
from cobra.transpilers.transpiler.python_nodes.proyectar import visit_proyectar as _visit_proyectar
from cobra.transpilers.transpiler.python_nodes.transformar import visit_transformar as _visit_transformar
from cobra.transpilers.transpiler.python_nodes.graficar import visit_graficar as _visit_graficar
from cobra.transpilers.transpiler.python_nodes.operacion_binaria import (
    visit_operacion_binaria as _visit_operacion_binaria,
)
from cobra.transpilers.transpiler.python_nodes.operacion_unaria import (
    visit_operacion_unaria as _visit_operacion_unaria,
)
from cobra.transpilers.transpiler.python_nodes.valor import visit_valor as _visit_valor
from cobra.transpilers.transpiler.python_nodes.identificador import visit_identificador as _visit_identificador
from cobra.transpilers.transpiler.python_nodes.para import visit_para as _visit_para
from cobra.transpilers.transpiler.python_nodes.decorador import visit_decorador as _visit_decorador
from cobra.transpilers.transpiler.python_nodes.yield_ import visit_yield as _visit_yield
from cobra.transpilers.transpiler.python_nodes.esperar import visit_esperar as _visit_esperar
from cobra.transpilers.transpiler.python_nodes.romper import visit_romper as _visit_romper
from cobra.transpilers.transpiler.python_nodes.continuar import visit_continuar as _visit_continuar
from cobra.transpilers.transpiler.python_nodes.pasar import visit_pasar as _visit_pasar
from cobra.transpilers.transpiler.python_nodes.switch import visit_switch as _visit_switch
from cobra.transpilers.transpiler.python_nodes.exportar import visit_export as _visit_export


def visit_assert(self, nodo):
    expr = self.obtener_valor(nodo.condicion)
    msg = f", {self.obtener_valor(nodo.mensaje)}" if nodo.mensaje else ""
    self.codigo += f"{self.obtener_indentacion()}assert {expr}{msg}\n"


def visit_del(self, nodo):
    objetivo = self.obtener_valor(nodo.objetivo)
    self.codigo += f"{self.obtener_indentacion()}del {objetivo}\n"


def visit_global(self, nodo):
    nombres = ", ".join(nodo.nombres)
    self.codigo += f"{self.obtener_indentacion()}global {nombres}\n"


def visit_nolocal(self, nodo):
    nombres = ", ".join(nodo.nombres)
    self.codigo += f"{self.obtener_indentacion()}nonlocal {nombres}\n"


def visit_with(self, nodo):
    ctx = self.obtener_valor(nodo.contexto)
    alias = f" as {nodo.alias}" if nodo.alias else ""
    self.codigo += f"{self.obtener_indentacion()}with {ctx}{alias}:\n"
    self.nivel_indentacion += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.nivel_indentacion -= 1


def visit_import_desde(self, nodo):
    alias = f" as {nodo.alias}" if nodo.alias else ""
    self.codigo += f"from {nodo.modulo} import {nodo.nombre}{alias}\n"


def visit_lista_tipo(self, nodo):
    elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
    anot = f": list[{nodo.tipo}]" if nodo.tipo else ""
    self.codigo += f"{self.obtener_indentacion()}{nodo.nombre}{anot} = [{elems}]\n"


def visit_diccionario_tipo(self, nodo):
    pares = ", ".join(
        f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
    )
    anot = (
        f": dict[{nodo.tipo_clave}, {nodo.tipo_valor}]"
        if nodo.tipo_clave or nodo.tipo_valor
        else ""
    )
    self.codigo += f"{self.obtener_indentacion()}{nodo.nombre}{anot} = {{{pares}}}\n"


def visit_lista_comprehension(self, nodo):
    self.codigo += f"{self.obtener_valor(nodo)}\n"


def visit_diccionario_comprehension(self, nodo):
    self.codigo += f"{self.obtener_valor(nodo)}\n"


class TranspiladorPython(BaseTranspiler):
    def __init__(self):
        # Incluir los modulos nativos al inicio del codigo generado
        self.codigo = get_standard_imports("python")
        self.usa_asyncio = False
        self.usa_typing = False
        self.nivel_indentacion = 0
        self.exportados: list[str] = []

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def obtener_indentacion(self):
        return "    " * self.nivel_indentacion

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            nodo.aceptar(self)
        if self.exportados:
            exports = ", ".join(f"'{n}'" for n in self.exportados)
            self.codigo += f"__all__ = [{exports}]\n"
        if (
            nodos
            and all(
            n.__class__.__module__.startswith("cobra.parser.parser")
                for n in nodos
            )
            and not any(self._contiene_nodo_valor(n) for n in nodos)
        ):
            solo_llamadas = all(
                hasattr(n, "argumentos") and not hasattr(n, "parametros") for n in nodos
            )
            if solo_llamadas:
                solo_numeros = all(
                    all(str(a).isdigit() for a in n.argumentos) for n in nodos
                )
                if not solo_numeros:
                    codigo = self.codigo.rstrip("\n")
                else:
                    codigo = self.codigo
            else:
                codigo = self.codigo.rstrip("\n")
        else:
            codigo = self.codigo
        if self.usa_typing:
            codigo = "from typing import TypeVar, Generic\n" + codigo
        if self.usa_asyncio:
            codigo = "import asyncio\n" + codigo
        return codigo

    def _contiene_nodo_valor(self, nodo):
        if hasattr(nodo, "valor") and len(getattr(nodo, "__dict__", {})) == 1:
            return True
        for atributo in getattr(nodo, "__dict__", {}).values():
            if isinstance(atributo, (list, tuple)):
                for elem in atributo:
                    if isinstance(elem, (list, tuple)):
                        for sub in elem:
                            if hasattr(sub, "__dict__") and self._contiene_nodo_valor(
                                sub
                            ):
                                return True
                    elif hasattr(elem, "__dict__") and self._contiene_nodo_valor(elem):
                        return True
            elif hasattr(atributo, "__dict__") and self._contiene_nodo_valor(atributo):
                return True
        return False

    def obtener_valor(self, nodo):
        from cobra.parser.parser import (
            NodoOperacionBinaria,
            NodoOperacionUnaria,
            NodoIdentificador,
        )

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
        elif isinstance(nodo, NodoLlamadaFuncion):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre}({args})"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "and", TipoToken.OR: "or"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            if nodo.operador.tipo == TipoToken.NOT:
                op = "not"
            else:
                op = nodo.operador.valor
            return f"{op} {val}" if op == "not" else f"{op}{val}"
        elif isinstance(nodo, NodoEsperar):
            self.usa_asyncio = True
            val = self.obtener_valor(nodo.expresion)
            return f"await {val}"
        elif isinstance(nodo, NodoLambda):
            params = ", ".join(nodo.parametros)
            cuerpo = self.obtener_valor(nodo.cuerpo)
            return f"lambda {params}: {cuerpo}"
        elif isinstance(nodo, NodoPattern):
            if isinstance(nodo.valor, list):
                elems = ", ".join(self.obtener_valor(p) for p in nodo.valor)
                return f"({elems})"
            elif nodo.valor == "_":
                return "_"
            else:
                return self.obtener_valor(nodo.valor)
        elif isinstance(nodo, NodoGuard):
            patron = self.obtener_valor(nodo.patron)
            guardia = self.obtener_valor(nodo.condicion)
            return f"{patron} if {guardia}"
        elif isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"[{elems}]"
        elif isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
        elif isinstance(nodo, NodoListaTipo):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"[{elems}]"
        elif isinstance(nodo, NodoDiccionarioTipo):
            pares = ", ".join(
                f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
        elif isinstance(nodo, NodoListaComprehension):
            expr = self.obtener_valor(nodo.expresion)
            it = self.obtener_valor(nodo.iterable)
            cond = (
                f" if {self.obtener_valor(nodo.condicion)}" if nodo.condicion else ""
            )
            return f"[{expr} for {nodo.variable} in {it}{cond}]"
        elif isinstance(nodo, NodoDiccionarioComprehension):
            key = self.obtener_valor(nodo.clave)
            val = self.obtener_valor(nodo.valor)
            it = self.obtener_valor(nodo.iterable)
            cond = (
                f" if {self.obtener_valor(nodo.condicion)}" if nodo.condicion else ""
            )
            return f"{{{key}: {val} for {nodo.variable} in {it}{cond}}}"
        else:
            return str(getattr(nodo, "valor", nodo))


# Asignar los visitantes externos a la clase
TranspiladorPython.visit_asignacion = _visit_asignacion
TranspiladorPython.visit_condicional = _visit_condicional
TranspiladorPython.visit_bucle_mientras = _visit_bucle_mientras
TranspiladorPython.visit_for = _visit_for
TranspiladorPython.visit_funcion = _visit_funcion
TranspiladorPython.visit_llamada_funcion = _visit_llamada_funcion
TranspiladorPython.visit_llamada_metodo = _visit_llamada_metodo
TranspiladorPython.visit_imprimir = _visit_imprimir
TranspiladorPython.visit_retorno = _visit_retorno
TranspiladorPython.visit_holobit = _visit_holobit
TranspiladorPython.visit_lista = _visit_lista
TranspiladorPython.visit_diccionario = _visit_diccionario
TranspiladorPython.visit_clase = _visit_clase
TranspiladorPython.visit_metodo = _visit_metodo
TranspiladorPython.visit_try_catch = _visit_try_catch
TranspiladorPython.visit_throw = _visit_throw
TranspiladorPython.visit_import = _visit_import
TranspiladorPython.visit_usar = _visit_usar
TranspiladorPython.visit_hilo = _visit_hilo
TranspiladorPython.visit_instancia = _visit_instancia
TranspiladorPython.visit_atributo = _visit_atributo
TranspiladorPython.visit_proyectar = _visit_proyectar
TranspiladorPython.visit_transformar = _visit_transformar
TranspiladorPython.visit_graficar = _visit_graficar
TranspiladorPython.visit_operacion_binaria = _visit_operacion_binaria
TranspiladorPython.visit_operacion_unaria = _visit_operacion_unaria
TranspiladorPython.visit_valor = _visit_valor
TranspiladorPython.visit_identificador = _visit_identificador
TranspiladorPython.visit_para = _visit_para
TranspiladorPython.visit_decorador = _visit_decorador
TranspiladorPython.visit_yield = _visit_yield
TranspiladorPython.visit_romper = _visit_romper
TranspiladorPython.visit_continuar = _visit_continuar
TranspiladorPython.visit_pasar = _visit_pasar
TranspiladorPython.visit_esperar = _visit_esperar
TranspiladorPython.visit_switch = _visit_switch
TranspiladorPython.visit_export = _visit_export
TranspiladorPython.visit_assert = visit_assert
TranspiladorPython.visit_del = visit_del
TranspiladorPython.visit_global = visit_global
TranspiladorPython.visit_nolocal = visit_nolocal
TranspiladorPython.visit_no_local = visit_nolocal
TranspiladorPython.visit_with = visit_with
TranspiladorPython.visit_import_desde = visit_import_desde
TranspiladorPython.visit_lista_tipo = visit_lista_tipo
TranspiladorPython.visit_diccionario_tipo = visit_diccionario_tipo
TranspiladorPython.visit_lista_comprehension = visit_lista_comprehension
TranspiladorPython.visit_diccionario_comprehension = visit_diccionario_comprehension
