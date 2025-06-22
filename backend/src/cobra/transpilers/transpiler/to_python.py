"""Transpilador que convierte código Cobra en código Python."""

from src.core.ast_nodes import (
    NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion,
    NodoLlamadaFuncion, NodoHolobit, NodoFor, NodoLista, NodoDiccionario,
    NodoClase,
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
    NodoImprimir
)
from src.cobra.parser.parser import Parser
from src.cobra.lexico.lexer import TipoToken, Lexer
from src.core.visitor import NodeVisitor
from src.core.optimizations import optimize_constants, remove_dead_code

from .python_nodes.asignacion import visit_asignacion as _visit_asignacion
from .python_nodes.condicional import visit_condicional as _visit_condicional
from .python_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from .python_nodes.for_ import visit_for as _visit_for
from .python_nodes.funcion import visit_funcion as _visit_funcion
from .python_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from .python_nodes.llamada_metodo import visit_llamada_metodo as _visit_llamada_metodo
from .python_nodes.imprimir import visit_imprimir as _visit_imprimir
from .python_nodes.retorno import visit_retorno as _visit_retorno
from .python_nodes.holobit import visit_holobit as _visit_holobit
from .python_nodes.lista import visit_lista as _visit_lista
from .python_nodes.diccionario import visit_diccionario as _visit_diccionario
from .python_nodes.clase import visit_clase as _visit_clase
from .python_nodes.metodo import visit_metodo as _visit_metodo
from .python_nodes.try_catch import visit_try_catch as _visit_try_catch
from .python_nodes.throw import visit_throw as _visit_throw
from .python_nodes.importar import visit_import as _visit_import
from .python_nodes.hilo import visit_hilo as _visit_hilo
from .python_nodes.instancia import visit_instancia as _visit_instancia
from .python_nodes.atributo import visit_atributo as _visit_atributo
from .python_nodes.operacion_binaria import visit_operacion_binaria as _visit_operacion_binaria
from .python_nodes.operacion_unaria import visit_operacion_unaria as _visit_operacion_unaria
from .python_nodes.valor import visit_valor as _visit_valor
from .python_nodes.identificador import visit_identificador as _visit_identificador
from .python_nodes.para import visit_para as _visit_para


class TranspiladorPython(NodeVisitor):
    def __init__(self):
        # Incluir los modulos nativos al inicio del codigo generado
        self.codigo = "from src.core.nativos import *\n"
        self.usa_asyncio = False
        self.nivel_indentacion = 0

    def obtener_indentacion(self):
        return "    " * self.nivel_indentacion

    def transpilar(self, nodos):
        nodos = remove_dead_code(optimize_constants(nodos))
        for nodo in nodos:
            nodo.aceptar(self)
        if nodos and all(
            n.__class__.__module__.startswith("src.cobra.parser.parser") for n in nodos
        ) and not any(self._contiene_nodo_valor(n) for n in nodos):
            solo_llamadas = all(
                hasattr(n, "argumentos") and not hasattr(n, "parametros")
                for n in nodos
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
                            if hasattr(sub, "__dict__") and self._contiene_nodo_valor(sub):
                                return True
                    elif hasattr(elem, "__dict__") and self._contiene_nodo_valor(elem):
                        return True
            elif hasattr(atributo, "__dict__") and self._contiene_nodo_valor(atributo):
                return True
        return False



    def obtener_valor(self, nodo):
        from src.cobra.parser.parser import (
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
TranspiladorPython.visit_hilo = _visit_hilo
TranspiladorPython.visit_instancia = _visit_instancia
TranspiladorPython.visit_atributo = _visit_atributo
TranspiladorPython.visit_operacion_binaria = _visit_operacion_binaria
TranspiladorPython.visit_operacion_unaria = _visit_operacion_unaria
TranspiladorPython.visit_valor = _visit_valor
TranspiladorPython.visit_identificador = _visit_identificador
TranspiladorPython.visit_para = _visit_para

