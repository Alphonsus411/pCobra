"""Transpilador que convierte código Cobra a Hololang."""

from __future__ import annotations

from typing import Iterable

from cobra.core.ast_nodes import (
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
    NodoEnum,
    NodoInterface,
    NodoMetodo,
    NodoValor,
    NodoRetorno,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoInstancia,
    NodoLlamadaMetodo,
    NodoAtributo,
    NodoHilo,
    NodoTryCatch,
    NodoThrow,
    NodoImport,
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
    NodoOption,
    NodoPattern,
    NodoGuard,
    NodoPara,
)
from cobra.core import TipoToken
from cobra.transpilers.common.utils import BaseTranspiler, get_standard_imports
from core.optimizations import optimize_constants, remove_dead_code, inline_functions
from cobra.macro import expandir_macros

from cobra.transpilers.transpiler.hololang_nodes.asignacion import (
    visit_asignacion as _visit_asignacion,
)
from cobra.transpilers.transpiler.hololang_nodes.condicional import (
    visit_condicional as _visit_condicional,
)
from cobra.transpilers.transpiler.hololang_nodes.bucle_mientras import (
    visit_bucle_mientras as _visit_bucle_mientras,
)
from cobra.transpilers.transpiler.hololang_nodes.for_ import visit_for as _visit_for
from cobra.transpilers.transpiler.hololang_nodes.funcion import (
    visit_funcion as _visit_funcion,
)
from cobra.transpilers.transpiler.hololang_nodes.llamada_funcion import (
    visit_llamada_funcion as _visit_llamada_funcion,
)
from cobra.transpilers.transpiler.hololang_nodes.llamada_metodo import (
    visit_llamada_metodo as _visit_llamada_metodo,
)
from cobra.transpilers.transpiler.hololang_nodes.imprimir import (
    visit_imprimir as _visit_imprimir,
)
from cobra.transpilers.transpiler.hololang_nodes.retorno import (
    visit_retorno as _visit_retorno,
)
from cobra.transpilers.transpiler.hololang_nodes.holobit import (
    visit_holobit as _visit_holobit,
)
from cobra.transpilers.transpiler.hololang_nodes.lista import visit_lista as _visit_lista
from cobra.transpilers.transpiler.hololang_nodes.diccionario import (
    visit_diccionario as _visit_diccionario,
)
from cobra.transpilers.transpiler.hololang_nodes.clase import visit_clase as _visit_clase
from cobra.transpilers.transpiler.hololang_nodes.metodo import (
    visit_metodo as _visit_metodo,
)
from cobra.transpilers.transpiler.hololang_nodes.try_catch import (
    visit_try_catch as _visit_try_catch,
)
from cobra.transpilers.transpiler.hololang_nodes.throw import visit_throw as _visit_throw
from cobra.transpilers.transpiler.hololang_nodes.importar import (
    visit_import as _visit_import,
)
from cobra.transpilers.transpiler.hololang_nodes.usar import visit_usar as _visit_usar
from cobra.transpilers.transpiler.hololang_nodes.hilo import visit_hilo as _visit_hilo
from cobra.transpilers.transpiler.hololang_nodes.instancia import (
    visit_instancia as _visit_instancia,
)
from cobra.transpilers.transpiler.hololang_nodes.atributo import (
    visit_atributo as _visit_atributo,
)
from cobra.transpilers.transpiler.hololang_nodes.proyectar import (
    visit_proyectar as _visit_proyectar,
)
from cobra.transpilers.transpiler.hololang_nodes.transformar import (
    visit_transformar as _visit_transformar,
)
from cobra.transpilers.transpiler.hololang_nodes.graficar import (
    visit_graficar as _visit_graficar,
)
from cobra.transpilers.transpiler.hololang_nodes.operacion_binaria import (
    visit_operacion_binaria as _visit_operacion_binaria,
)
from cobra.transpilers.transpiler.hololang_nodes.operacion_unaria import (
    visit_operacion_unaria as _visit_operacion_unaria,
)
from cobra.transpilers.transpiler.hololang_nodes.valor import visit_valor as _visit_valor
from cobra.transpilers.transpiler.hololang_nodes.identificador import (
    visit_identificador as _visit_identificador,
)
from cobra.transpilers.transpiler.hololang_nodes.para import visit_para as _visit_para
from cobra.transpilers.transpiler.hololang_nodes.decorador import (
    visit_decorador as _visit_decorador,
)
from cobra.transpilers.transpiler.hololang_nodes.yield_ import (
    visit_yield as _visit_yield,
)
from cobra.transpilers.transpiler.hololang_nodes.esperar import (
    visit_esperar as _visit_esperar,
)
from cobra.transpilers.transpiler.hololang_nodes.romper import (
    visit_romper as _visit_romper,
)
from cobra.transpilers.transpiler.hololang_nodes.continuar import (
    visit_continuar as _visit_continuar,
)
from cobra.transpilers.transpiler.hololang_nodes.pasar import visit_pasar as _visit_pasar
from cobra.transpilers.transpiler.hololang_nodes.switch import (
    visit_switch as _visit_switch,
)
from cobra.transpilers.transpiler.hololang_nodes.option import (
    visit_option as _visit_option,
)
from cobra.transpilers.transpiler.hololang_nodes.enum import visit_enum as _visit_enum


ASYNC_IMPORT = "use holo.async::*;"


def _extraer_lineas(imports: str | Iterable[str]) -> list[str]:
    if isinstance(imports, str):
        return [line for line in imports.splitlines() if line]
    return list(imports)


class TranspiladorHololang(BaseTranspiler):
    """Genera código Hololang a partir de un AST de Cobra."""

    def __init__(self):
        self.codigo: list[str] = []
        self.indentacion = 0
        self.requiere_async = False

    def _reiniciar_codigo(self) -> None:
        base_imports = get_standard_imports("hololang")
        self.codigo = _extraer_lineas(base_imports)
        self.indentacion = 0
        self.requiere_async = False

    def generate_code(self, ast):
        self._reiniciar_codigo()
        codigo = self.transpilar(ast)
        return codigo

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indentacion + linea)

    def obtener_indentacion(self) -> str:
        return "    " * self.indentacion

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(inline_functions(optimize_constants(nodos)))
        for nodo in nodos:
            nodo.aceptar(self)
        if self.requiere_async and ASYNC_IMPORT not in self.codigo:
            self.codigo.insert(0, ASYNC_IMPORT)
        texto = "\n".join(self.codigo)
        if texto and not texto.endswith("\n"):
            texto += "\n"
        return texto

    def obtener_valor(self, nodo):  # noqa: C901 - requiere múltiples casos
        if isinstance(nodo, NodoValor):
            valor = nodo.valor
            if isinstance(valor, bool):
                return "true" if valor else "false"
            if valor is None:
                return "null"
            if isinstance(valor, str):
                return valor
            return str(valor)
        if isinstance(nodo, NodoAtributo):
            obj = self.obtener_valor(nodo.objeto)
            return f"{obj}.{nodo.nombre}"
        if isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"new {nodo.nombre_clase}({args})"
        if isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        if isinstance(nodo, NodoLlamadaFuncion):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre}({args})"
        if isinstance(nodo, NodoLlamadaMetodo):
            obj = self.obtener_valor(nodo.objeto)
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{obj}.{nodo.nombre_metodo}({args})"
        if isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "&&", TipoToken.OR: "||"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        if isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            if nodo.operador.tipo == TipoToken.NOT:
                return f"!{val}"
            return f"{nodo.operador.valor}{val}"
        if isinstance(nodo, NodoEsperar):
            self.requiere_async = True
            val = self.obtener_valor(nodo.expresion)
            return f"await {val}"
        if isinstance(nodo, NodoLambda):
            params = ", ".join(nodo.parametros)
            cuerpo = self.obtener_valor(nodo.cuerpo)
            return f"|{params}| -> {cuerpo}"
        if isinstance(nodo, NodoOption):
            if nodo.valor is None:
                return "Option::None"
            return f"Option::Some({self.obtener_valor(nodo.valor)})"
        if isinstance(nodo, NodoPattern):
            if isinstance(nodo.valor, list):
                elems = ", ".join(self.obtener_valor(v) for v in nodo.valor)
                return f"({elems})"
            if nodo.valor == "_":
                return "_"
            return self.obtener_valor(nodo.valor)
        if isinstance(nodo, NodoGuard):
            patron = self.obtener_valor(nodo.patron)
            condicion = self.obtener_valor(nodo.condicion)
            return f"{patron} if {condicion}"
        if isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"[{elems}]"
        if isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
        if isinstance(nodo, NodoListaTipo):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"[{elems}]"
        if isinstance(nodo, NodoDiccionarioTipo):
            pares = ", ".join(
                f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
        if isinstance(nodo, NodoListaComprehension):
            expresion = self.obtener_valor(nodo.expresion)
            iterable = self.obtener_valor(nodo.iterable)
            condicion = (
                f" if {self.obtener_valor(nodo.condicion)}" if nodo.condicion else ""
            )
            return f"[{expresion} for {nodo.variable} in {iterable}{condicion}]"
        if isinstance(nodo, NodoDiccionarioComprehension):
            clave = self.obtener_valor(nodo.clave)
            valor = self.obtener_valor(nodo.valor)
            iterable = self.obtener_valor(nodo.iterable)
            condicion = (
                f" if {self.obtener_valor(nodo.condicion)}" if nodo.condicion else ""
            )
            return f"{{{clave}: {valor} for {nodo.variable} in {iterable}{condicion}}}"
        if isinstance(nodo, NodoHolobit):
            valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
            return f"Holobit::new([{valores}])"
        return str(getattr(nodo, "valor", nodo))

    # Implementaciones particulares no cubiertas por nodos externos
    def visit_interface(self, nodo: NodoInterface):
        self.agregar_linea(f"trait {nodo.nombre} {{")
        self.indentacion += 1
        for metodo in nodo.metodos:
            params = ", ".join(metodo.parametros)
            self.agregar_linea(f"fn {metodo.nombre}({params});")
        self.indentacion -= 1
        self.agregar_linea("}")

    def visit_assert(self, nodo: NodoAssert):
        condicion = self.obtener_valor(nodo.condicion)
        mensaje = f", {self.obtener_valor(nodo.mensaje)}" if getattr(nodo, "mensaje", None) else ""
        self.agregar_linea(f"assert {condicion}{mensaje};")

    def visit_del(self, nodo: NodoDel):
        objetivo = self.obtener_valor(nodo.objetivo)
        self.agregar_linea(f"drop {objetivo};")

    def visit_global(self, nodo: NodoGlobal):
        nombres = ", ".join(nodo.nombres)
        self.agregar_linea(f"// global {nombres}")

    def visit_nolocal(self, nodo: NodoNoLocal):
        nombres = ", ".join(nodo.nombres)
        self.agregar_linea(f"// nonlocal {nombres}")

    visit_no_local = visit_nolocal

    def visit_with(self, nodo: NodoWith):
        contexto = self.obtener_valor(nodo.contexto)
        alias = f" as {nodo.alias}" if nodo.alias else ""
        self.agregar_linea(f"with ({contexto}{alias}) {{")
        self.indentacion += 1
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self.indentacion -= 1
        self.agregar_linea("}")

    def visit_import_desde(self, nodo: NodoImportDesde):
        alias = f" as {nodo.alias}" if nodo.alias else ""
        self.agregar_linea(f"use {nodo.modulo}::{nodo.nombre}{alias};")

    def visit_lista_tipo(self, nodo: NodoListaTipo):
        elementos = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
        self.agregar_linea(
            f"let {nodo.nombre}: list<{nodo.tipo}> = [{elementos}];"
        )

    def visit_diccionario_tipo(self, nodo: NodoDiccionarioTipo):
        pares = ", ".join(
            f"{self.obtener_valor(k)}: {self.obtener_valor(v)}" for k, v in nodo.elementos
        )
        self.agregar_linea(
            "let {nombre}: map<{tk}, {tv}> = {{{pares}}};".format(
                nombre=nodo.nombre,
                tk=nodo.tipo_clave,
                tv=nodo.tipo_valor,
                pares=pares,
            )
        )

    def visit_lista_comprehension(self, nodo: NodoListaComprehension):
        self.agregar_linea(f"{self.obtener_valor(nodo)};")

    def visit_diccionario_comprehension(self, nodo: NodoDiccionarioComprehension):
        self.agregar_linea(f"{self.obtener_valor(nodo)};")


# Asignar los visitantes externos a la clase
TranspiladorHololang.visit_asignacion = _visit_asignacion
TranspiladorHololang.visit_condicional = _visit_condicional
TranspiladorHololang.visit_bucle_mientras = _visit_bucle_mientras
TranspiladorHololang.visit_for = _visit_for
TranspiladorHololang.visit_funcion = _visit_funcion
TranspiladorHololang.visit_llamada_funcion = _visit_llamada_funcion
TranspiladorHololang.visit_llamada_metodo = _visit_llamada_metodo
TranspiladorHololang.visit_imprimir = _visit_imprimir
TranspiladorHololang.visit_retorno = _visit_retorno
TranspiladorHololang.visit_holobit = _visit_holobit
TranspiladorHololang.visit_lista = _visit_lista
TranspiladorHololang.visit_diccionario = _visit_diccionario
TranspiladorHololang.visit_clase = _visit_clase
TranspiladorHololang.visit_metodo = _visit_metodo
TranspiladorHololang.visit_try_catch = _visit_try_catch
TranspiladorHololang.visit_throw = _visit_throw
TranspiladorHololang.visit_import = _visit_import
TranspiladorHololang.visit_usar = _visit_usar
TranspiladorHololang.visit_hilo = _visit_hilo
TranspiladorHololang.visit_instancia = _visit_instancia
TranspiladorHololang.visit_atributo = _visit_atributo
TranspiladorHololang.visit_proyectar = _visit_proyectar
TranspiladorHololang.visit_transformar = _visit_transformar
TranspiladorHololang.visit_graficar = _visit_graficar
TranspiladorHololang.visit_operacion_binaria = _visit_operacion_binaria
TranspiladorHololang.visit_operacion_unaria = _visit_operacion_unaria
TranspiladorHololang.visit_valor = _visit_valor
TranspiladorHololang.visit_identificador = _visit_identificador
TranspiladorHololang.visit_para = _visit_para
TranspiladorHololang.visit_decorador = _visit_decorador
TranspiladorHololang.visit_yield = _visit_yield
TranspiladorHololang.visit_esperar = _visit_esperar
TranspiladorHololang.visit_romper = _visit_romper
TranspiladorHololang.visit_continuar = _visit_continuar
TranspiladorHololang.visit_pasar = _visit_pasar
TranspiladorHololang.visit_switch = _visit_switch
TranspiladorHololang.visit_option = _visit_option
TranspiladorHololang.visit_enum = _visit_enum
