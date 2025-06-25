"""Transpilador que genera código ensamblador simple desde Cobra."""

from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoFor,
    NodoLista,
    NodoDiccionario,
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
    NodoImprimir,
    NodoPara,
    NodoUsar,
)
from src.cobra.lexico.lexer import TipoToken, Lexer
from src.cobra.parser.parser import Parser
from src.core.visitor import NodeVisitor
from src.core.optimizations import optimize_constants, remove_dead_code
from src.cobra.macro import expandir_macros

from .asm_nodes.asignacion import visit_asignacion as _visit_asignacion
from .asm_nodes.condicional import visit_condicional as _visit_condicional
from .asm_nodes.bucle_mientras import visit_bucle_mientras as _visit_bucle_mientras
from .asm_nodes.funcion import visit_funcion as _visit_funcion
from .asm_nodes.llamada_funcion import visit_llamada_funcion as _visit_llamada_funcion
from .asm_nodes.llamada_metodo import visit_llamada_metodo as _visit_llamada_metodo
from .asm_nodes.hilo import visit_hilo as _visit_hilo
from .asm_nodes.imprimir import visit_imprimir as _visit_imprimir
from .asm_nodes.retorno import visit_retorno as _visit_retorno
from .asm_nodes.holobit import visit_holobit as _visit_holobit
from .asm_nodes.for_ import visit_for as _visit_for
from .asm_nodes.para import visit_para as _visit_para
from .asm_nodes.lista import visit_lista as _visit_lista
from .asm_nodes.diccionario import visit_diccionario as _visit_diccionario
from .asm_nodes.clase import visit_clase as _visit_clase
from .asm_nodes.metodo import visit_metodo as _visit_metodo
from .asm_nodes.try_catch import visit_try_catch as _visit_try_catch
from .asm_nodes.throw import visit_throw as _visit_throw
from .asm_nodes.importar import visit_import as _visit_import
from .asm_nodes.instancia import visit_instancia as _visit_instancia
from .asm_nodes.atributo import visit_atributo as _visit_atributo
from .asm_nodes.operacion_binaria import visit_operacion_binaria as _visit_operacion_binaria
from .asm_nodes.operacion_unaria import visit_operacion_unaria as _visit_operacion_unaria
from .asm_nodes.valor import visit_valor as _visit_valor
from .asm_nodes.identificador import visit_identificador as _visit_identificador
from .asm_nodes.usar import visit_usar as _visit_usar
from .asm_nodes.romper import visit_romper as _visit_romper
from .asm_nodes.continuar import visit_continuar as _visit_continuar


class TranspiladorASM(NodeVisitor):
    """Transpila el AST de Cobra a instrucciones de ensamblador simplificado."""

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
            return f"NEW {nodo.nombre_clase}({args})"
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "AND", TipoToken.OR: "OR"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            op = "NOT" if nodo.operador.tipo == TipoToken.NOT else nodo.operador.valor
            return f"{op} {val}" if op == "NOT" else f"{op}{val}"
        elif isinstance(nodo, NodoLista):
            elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
            return f"[{elems}]"
        elif isinstance(nodo, NodoDiccionario):
            pares = ", ".join(
                f"{self.obtener_valor(k)}:{self.obtener_valor(v)}" for k, v in nodo.elementos
            )
            return f"{{{pares}}}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        nodos = remove_dead_code(optimize_constants(nodos))
        for nodo in nodos:
            nodo.aceptar(self)
        return "\n".join(self.codigo)


# Asignar los visitantes externos a la clase
TranspiladorASM.visit_asignacion = _visit_asignacion
TranspiladorASM.visit_condicional = _visit_condicional
TranspiladorASM.visit_bucle_mientras = _visit_bucle_mientras
TranspiladorASM.visit_funcion = _visit_funcion
TranspiladorASM.visit_llamada_funcion = _visit_llamada_funcion
TranspiladorASM.visit_llamada_metodo = _visit_llamada_metodo
TranspiladorASM.visit_hilo = _visit_hilo
TranspiladorASM.visit_imprimir = _visit_imprimir
TranspiladorASM.visit_retorno = _visit_retorno
TranspiladorASM.visit_holobit = _visit_holobit
TranspiladorASM.visit_for = _visit_for
TranspiladorASM.visit_para = _visit_para
TranspiladorASM.visit_lista = _visit_lista
TranspiladorASM.visit_diccionario = _visit_diccionario
TranspiladorASM.visit_clase = _visit_clase
TranspiladorASM.visit_metodo = _visit_metodo
TranspiladorASM.visit_try_catch = _visit_try_catch
TranspiladorASM.visit_throw = _visit_throw
TranspiladorASM.visit_import = _visit_import
TranspiladorASM.visit_instancia = _visit_instancia
TranspiladorASM.visit_atributo = _visit_atributo
TranspiladorASM.visit_operacion_binaria = _visit_operacion_binaria
TranspiladorASM.visit_operacion_unaria = _visit_operacion_unaria
TranspiladorASM.visit_valor = _visit_valor
TranspiladorASM.visit_identificador = _visit_identificador
TranspiladorASM.visit_usar = _visit_usar
TranspiladorASM.visit_romper = _visit_romper
TranspiladorASM.visit_continuar = _visit_continuar
