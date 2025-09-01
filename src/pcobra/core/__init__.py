"""Facilita el acceso a los nodos y utilidades principales del backend.

Al importar :mod:`pcobra.core` se exponen todas las clases que componen el
árbol de sintaxis abstracta junto con el visitante base ``NodeVisitor``.
Esto simplifica el uso de la biblioteca desde otros módulos.

Las funciones para limitar recursos ``limitar_memoria_mb`` y
``limitar_cpu_segundos`` también se exponen aquí y deben usarse en lugar
de implementaciones manuales.
"""

from .ast_nodes import *
from .ast_nodes import NodoListaComprehension, NodoDiccionarioComprehension, NodoEnum
from .visitor import NodeVisitor
from .performance import optimizar, perfilar, smart_perfilar, optimizar_bucle
from .resource_limits import limitar_memoria_mb, limitar_cpu_segundos

__all__ = [
    "NodoAST",
    "NodoAsignacion",
    "NodoHolobit",
    "NodoCondicional",
    "NodoBucleMientras",
    "NodoFor",
    "NodoLista",
    "NodoDiccionario",
    "NodoListaComprehension",
    "NodoDiccionarioComprehension",
    "NodoFuncion",
    "NodoClase",
    "NodoEnum",
    "NodoMetodo",
    "NodoInstancia",
    "NodoAtributo",
    "NodoLlamadaMetodo",
    "NodoOperacionBinaria",
    "NodoOperacionUnaria",
    "NodoValor",
    "NodoIdentificador",
    "NodoLlamadaFuncion",
    "NodoHilo",
    "NodoRetorno",
    "NodoThrow",
    "NodoTryCatch",
    "NodoImport",
    "NodoUsar",
    "NodoRomper",
    "NodoContinuar",
    "NodoPasar",
    "NodoAssert",
    "NodoDel",
    "NodoGlobal",
    "NodoNoLocal",
    "NodoLambda",
    "NodoWith",
    "NodoImportDesde",
    "NodoPara",
    "NodoImprimir",
    "NodeVisitor",
    "optimizar",
    "perfilar",
    "smart_perfilar",
    "optimizar_bucle",
    "limitar_memoria_mb",
    "limitar_cpu_segundos",
]
