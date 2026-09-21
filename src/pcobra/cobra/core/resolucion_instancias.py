"""Resolución neutral de llamadas que designan clases Cobra declaradas."""

from __future__ import annotations

from typing import Any, Iterable

from pcobra.cobra.core.ast_nodes import (
    NodoAST,
    NodoBloque,
    NodoClase,
    NodoFuncion,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoMetodo,
)


def resolver_instanciaciones(ast: list[NodoAST]) -> list[NodoAST]:
    """Convierte llamadas a clases ya declaradas en ``NodoInstancia``.

    La resolución respeta el orden de declaración. Si un ámbito declara una
    clase y una función con el mismo nombre, conserva la llamada neutral sin
    elegir arbitrariamente entre ambos símbolos; el analizador semántico es
    quien informa después de la colisión de declaraciones.
    """

    _resolver_bloque(ast, set())
    return ast


def _nombres_ambiguos(nodos: Iterable[Any]) -> set[str]:
    clases: set[str] = set()
    funciones: set[str] = set()
    for nodo in nodos:
        if isinstance(nodo, NodoClase):
            clases.add(nodo.nombre)
        elif isinstance(nodo, NodoFuncion):
            funciones.add(nodo.nombre)
    return clases & funciones


def _resolver_bloque(nodos: Any, clases_visibles: set[str]) -> None:
    instrucciones = nodos.instrucciones if isinstance(nodos, NodoBloque) else nodos
    visibles = set(clases_visibles)
    ambiguos = _nombres_ambiguos(instrucciones)

    for indice, nodo in enumerate(instrucciones):
        if isinstance(nodo, NodoClase):
            clase_actual = {nodo.nombre} if nodo.nombre not in ambiguos else set()
            clases_de_metodos = visibles | clase_actual
            for metodo in nodo.metodos:
                _resolver_nodo(metodo, clases_de_metodos, ambiguos)
            if nodo.nombre not in ambiguos:
                visibles.add(nodo.nombre)
            continue

        instrucciones[indice] = _resolver_nodo(nodo, visibles, ambiguos)


def _resolver_nodo(nodo: Any, clases_visibles: set[str], ambiguos: set[str]) -> Any:
    if isinstance(nodo, NodoLlamadaFuncion):
        argumentos = [
            _resolver_nodo(argumento, clases_visibles, ambiguos)
            for argumento in nodo.argumentos
        ]
        if nodo.nombre in clases_visibles and nodo.nombre not in ambiguos:
            return NodoInstancia(nodo.nombre, argumentos)
        nodo.argumentos = argumentos
        return nodo

    if isinstance(nodo, (NodoFuncion, NodoMetodo)):
        visibles = clases_visibles - set(nodo.parametros)
        _resolver_bloque(nodo.cuerpo, visibles)
        return nodo

    if isinstance(nodo, NodoBloque):
        _resolver_bloque(nodo, clases_visibles)
        return nodo

    if isinstance(nodo, NodoAST):
        for nombre, valor in vars(nodo).items():
            if isinstance(valor, NodoAST):
                setattr(
                    nodo,
                    nombre,
                    _resolver_nodo(valor, clases_visibles, ambiguos),
                )
            elif isinstance(valor, list):
                for indice, elemento in enumerate(valor):
                    if isinstance(elemento, NodoAST):
                        valor[indice] = _resolver_nodo(
                            elemento, clases_visibles, ambiguos
                        )
        return nodo

    return nodo
