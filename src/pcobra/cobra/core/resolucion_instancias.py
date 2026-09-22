"""Resolución neutral de llamadas que designan clases Cobra declaradas."""

from __future__ import annotations

from typing import Any, Iterable

from pcobra.cobra.core.ast_nodes import (
    NodoAST,
    NodoAsignacion,
    NodoBloque,
    NodoClase,
    NodoFuncion,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoMetodo,
    NodoPara,
)

_CLASE = "clase"
_OTRO = "otro"
Bindings = dict[str, str]
Memo = dict[int, Any]


def resolver_instanciaciones(ast: list[NodoAST]) -> list[NodoAST]:
    """Convierte llamadas a clases ya declaradas en ``NodoInstancia``.

    La resolución respeta el orden de declaración. Si un ámbito declara una
    clase y una función con el mismo nombre, conserva la llamada neutral sin
    elegir arbitrariamente entre ambos símbolos; el analizador semántico es
    quien informa después de la colisión de declaraciones.
    """

    _resolver_bloque(ast, {}, {})
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


def _resolver_bloque(nodos: Any, bindings: Bindings, memo: Memo) -> None:
    instrucciones = nodos.instrucciones if isinstance(nodos, NodoBloque) else nodos
    ambiguos = _nombres_ambiguos(instrucciones)

    for indice, nodo in enumerate(instrucciones):
        if isinstance(nodo, NodoClase):
            clase_actual = {nodo.nombre} if nodo.nombre not in ambiguos else set()
            bindings_de_metodos = bindings.copy()
            bindings_de_metodos.update(
                (nombre, _CLASE) for nombre in clase_actual
            )
            for metodo in nodo.metodos:
                _resolver_nodo(metodo, bindings_de_metodos, ambiguos, memo)
            bindings[nodo.nombre] = (
                _OTRO if nodo.nombre in ambiguos else _CLASE
            )
            continue

        instrucciones[indice] = _resolver_nodo(nodo, bindings, ambiguos, memo)
        if isinstance(nodo, (NodoFuncion, NodoAsignacion)):
            nombre = nodo.nombre if isinstance(nodo, NodoFuncion) else nodo.variable
            if isinstance(nombre, str):
                bindings[nombre] = _OTRO


def _resolver_nodo(
    nodo: Any,
    bindings: Bindings,
    ambiguos: set[str],
    memo: Memo,
) -> Any:
    identidad = id(nodo)
    if identidad in memo:
        return memo[identidad]

    if isinstance(nodo, NodoLlamadaFuncion):
        argumentos = [
            _resolver_nodo(argumento, bindings, ambiguos, memo)
            for argumento in nodo.argumentos
        ]
        if bindings.get(nodo.nombre) == _CLASE and nodo.nombre not in ambiguos:
            instancia = NodoInstancia(nodo.nombre, argumentos)
            memo[identidad] = instancia
            return instancia
        nodo.argumentos = argumentos
        memo[identidad] = nodo
        return nodo

    if isinstance(nodo, (NodoFuncion, NodoMetodo)):
        memo[identidad] = nodo
        bindings_locales = bindings.copy()
        bindings_locales.update((parametro, _OTRO) for parametro in nodo.parametros)
        _resolver_bloque(nodo.cuerpo, bindings_locales, memo)
        return nodo

    if isinstance(nodo, NodoPara):
        memo[identidad] = nodo
        nodo.iterable = _resolver_nodo(nodo.iterable, bindings, ambiguos, memo)
        if isinstance(nodo.variable, str):
            bindings[nodo.variable] = _OTRO
        _resolver_bloque(nodo.cuerpo, bindings, memo)
        return nodo

    if isinstance(nodo, NodoBloque):
        memo[identidad] = nodo
        _resolver_bloque(nodo, bindings, memo)
        return nodo

    if isinstance(nodo, NodoAST):
        memo[identidad] = nodo
        for nombre, valor in vars(nodo).items():
            if isinstance(valor, NodoAST):
                setattr(
                    nodo,
                    nombre,
                    _resolver_nodo(valor, bindings, ambiguos, memo),
                )
            elif isinstance(valor, list):
                for indice, elemento in enumerate(valor):
                    if isinstance(elemento, NodoAST):
                        valor[indice] = _resolver_nodo(elemento, bindings, ambiguos, memo)
        return nodo

    return nodo
