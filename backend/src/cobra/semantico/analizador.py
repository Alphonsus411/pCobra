from typing import List

from core.visitor import NodeVisitor
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoClase,
    NodoMetodo,
    NodoIdentificador,
)

from .tabla import Ambito


class AnalizadorSemantico(NodeVisitor):
    """Analiza el AST para construir y validar la tabla de símbolos."""

    def __init__(self):
        self.global_scope = Ambito()
        self.current_scope = self.global_scope

    def analizar(self, ast: List):
        for nodo in ast:
            nodo.aceptar(self)

    # Utilidades ---------------------------------------------------------
    def _con_nuevo_ambito(self):
        nuevo = Ambito(self.current_scope)
        self.current_scope = nuevo
        return nuevo

    def _salir_ambito(self):
        if self.current_scope.padre is not None:
            self.current_scope = self.current_scope.padre

    # Visitas ------------------------------------------------------------
    def visit_asignacion(self, nodo: NodoAsignacion):
        nombre = nodo.variable
        if not self.current_scope.resolver_local(nombre):
            self.current_scope.declarar(nombre, "variable")
        nodo.expresion.aceptar(self) if hasattr(nodo.expresion, "aceptar") else None

    def visit_identificador(self, nodo: NodoIdentificador):
        if not self.current_scope.resolver(nodo.nombre):
            raise NameError(f"Variable no declarada: {nodo.nombre}")

    def visit_funcion(self, nodo: NodoFuncion):
        if self.current_scope.resolver_local(nodo.nombre):
            raise ValueError(f"Símbolo ya declarado: {nodo.nombre}")
        self.current_scope.declarar(nodo.nombre, "funcion")
        self._con_nuevo_ambito()
        for param in nodo.parametros:
            self.current_scope.declarar(param, "variable")
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self._salir_ambito()

    def visit_metodo(self, nodo: NodoMetodo):
        if self.current_scope.resolver_local(nodo.nombre):
            raise ValueError(f"Símbolo ya declarado: {nodo.nombre}")
        self.current_scope.declarar(nodo.nombre, "funcion")
        self._con_nuevo_ambito()
        for param in nodo.parametros:
            self.current_scope.declarar(param, "variable")
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self._salir_ambito()

    def visit_clase(self, nodo: NodoClase):
        if self.current_scope.resolver_local(nodo.nombre):
            raise ValueError(f"Símbolo ya declarado: {nodo.nombre}")
        self.current_scope.declarar(nodo.nombre, "clase")
        self._con_nuevo_ambito()
        for metodo in nodo.metodos:
            metodo.aceptar(self)
        self._salir_ambito()

    def generic_visit(self, nodo):
        for valor in getattr(nodo, "__dict__", {}).values():
            if isinstance(valor, list):
                for elem in valor:
                    if hasattr(elem, "aceptar"):
                        elem.aceptar(self)
            elif hasattr(valor, "aceptar"):
                valor.aceptar(self)
