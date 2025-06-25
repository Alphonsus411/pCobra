"""Transpilador que genera código JavaScript a partir de Cobra."""

from src.core.ast_nodes import (
    NodoLista,
    NodoDiccionario,
    NodoValor,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoAtributo,
    NodoInstancia,
)
from src.cobra.lexico.lexer import TipoToken
from src.core.visitor import NodeVisitor
from src.core.optimizations import optimize_constants, remove_dead_code
from src.cobra.macro import expandir_macros

from .js_nodes.asignacion import visit_asignacion as _visit_asignacion
from .js_nodes.condicional import visit_condicional as _visit_condicional
from .js_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from .js_nodes.funcion import visit_funcion as _visit_funcion
from .js_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from .js_nodes.hilo import visit_hilo as _visit_hilo
from .js_nodes.llamada_metodo import visit_llamada_metodo as _visit_llamada_metodo
from .js_nodes.imprimir import visit_imprimir as _visit_imprimir
from .js_nodes.retorno import visit_retorno as _visit_retorno
from .js_nodes.holobit import visit_holobit as _visit_holobit
from .js_nodes.for_ import visit_for as _visit_for
from .js_nodes.lista import visit_lista as _visit_lista
from .js_nodes.diccionario import visit_diccionario as _visit_diccionario
from .js_nodes.elemento import visit_elemento as _visit_elemento
from .js_nodes.clase import visit_clase as _visit_clase
from .js_nodes.metodo import visit_metodo as _visit_metodo
from .js_nodes.try_catch import visit_try_catch as _visit_try_catch
from .js_nodes.throw import visit_throw as _visit_throw
from .js_nodes.importar import visit_import as _visit_import
from .js_nodes.instancia import visit_instancia as _visit_instancia
from .js_nodes.atributo import visit_atributo as _visit_atributo
from .js_nodes.operacion_binaria import visit_operacion_binaria as _visit_operacion_binaria
from .js_nodes.operacion_unaria import visit_operacion_unaria as _visit_operacion_unaria
from .js_nodes.valor import visit_valor as _visit_valor
from .js_nodes.identificador import visit_identificador as _visit_identificador
from .js_nodes.para import visit_para as _visit_para
from .js_nodes.decorador import visit_decorador as _visit_decorador


class TranspiladorJavaScript(NodeVisitor):
    def __init__(self):
        # Incluir importaciones de modulos nativos
        self.codigo = [
            "import * as io from './nativos/io.js';",
            "import * as net from './nativos/io.js';",
            "import * as matematicas from './nativos/matematicas.js';",
            "import { Pila, Cola } from './nativos/estructuras.js';",
        ]
        self.indentacion = 0
        self.usa_indentacion = None

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
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            return f"{izq} {nodo.operador.valor} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            return f"!{val}" if nodo.operador.tipo == TipoToken.NOT else f"{nodo.operador.valor}{val}"
        elif isinstance(nodo, NodoLista) or isinstance(nodo, NodoDiccionario):
            temp = []
            original = self.codigo
            self.codigo = temp
            if isinstance(nodo, NodoLista):
                self.visit_lista(nodo)
            else:
                self.visit_diccionario(nodo)
            self.codigo = original
            return ''.join(temp)
        else:
            return str(nodo)

    def transpilar(self, ast_raiz):
        ast_raiz = expandir_macros(ast_raiz)
        ast_raiz = remove_dead_code(optimize_constants(ast_raiz))
        for nodo in ast_raiz:
            if hasattr(nodo, 'aceptar'):
                nodo.aceptar(self)
            else:
                nombre = nodo.__class__.__name__
                if nombre.startswith('Nodo'):
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
TranspiladorJavaScript.visit_operacion_binaria = _visit_operacion_binaria
TranspiladorJavaScript.visit_operacion_unaria = _visit_operacion_unaria
TranspiladorJavaScript.visit_valor = _visit_valor
TranspiladorJavaScript.visit_identificador = _visit_identificador
TranspiladorJavaScript.visit_para = _visit_para
TranspiladorJavaScript.visit_decorador = _visit_decorador

    # Métodos de transpilación para tipos de nodos básicos

