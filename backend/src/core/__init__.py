"""Facilita el acceso a los nodos y utilidades principales del backend.

Al importar :mod:`src.core` se exponen todas las clases que componen el
árbol de sintaxis abstracta junto con el visitante base ``NodeVisitor``.
Esto simplifica el uso de la biblioteca desde otros módulos.
"""

from .ast_nodes import *
from .visitor import NodeVisitor

__all__ = [
    'NodoAST',
    'NodoAsignacion',
    'NodoHolobit',
    'NodoCondicional',
    'NodoBucleMientras',
    'NodoFor',
    'NodoLista',
    'NodoDiccionario',
    'NodoFuncion',
    'NodoClase',
    'NodoMetodo',
    'NodoInstancia',
    'NodoAtributo',
    'NodoLlamadaMetodo',
    'NodoOperacionBinaria',
    'NodoOperacionUnaria',
    'NodoValor',
    'NodoIdentificador',
    'NodoLlamadaFuncion',
    'NodoHilo',
    'NodoRetorno',
    'NodoThrow',
    'NodoTryCatch',
    'NodoImport',
    'NodoUsar',
    'NodoRomper',
    'NodoContinuar',
    'NodoPasar',
    'NodoPara',
    'NodoImprimir',
    'NodeVisitor',
]
