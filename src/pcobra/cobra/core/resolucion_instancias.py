"""Resolución neutral de llamadas que designan clases Cobra declaradas."""

from __future__ import annotations

from typing import Any, Iterable

from pcobra.cobra.core.ast_nodes import (
    NodoAST,
    NodoAsignacion,
    NodoBloque,
    NodoBucleMientras,
    NodoClase,
    NodoCondicional,
    NodoFuncion,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoMetodo,
    NodoPara,
    NodoWith,
)

_CLASE = "clase"
_OTRO = "otro"
_AMBIGUO = "ambiguo"
Bindings = dict[str, str]
Memo = dict[int, Any]


def _fusionar_bindings(bindings: Bindings, caminos: Iterable[Bindings]) -> None:
    """Conserva sólo la información coincidente en todos los caminos posibles."""

    estados = list(caminos)
    nombres = set().union(bindings, *(estado.keys() for estado in estados))
    ausente = object()
    for nombre in nombres:
        valores = {estado.get(nombre, ausente) for estado in estados}
        if len(valores) == 1:
            valor = valores.pop()
            if valor is ausente:
                bindings.pop(nombre, None)
            else:
                bindings[nombre] = valor
        else:
            bindings[nombre] = _AMBIGUO


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


def _resolver_bloque_con(
    nodos: Any,
    bindings: Bindings,
    bindings_padre: Bindings,
    memo: Memo,
    declarados_locales: set[str],
) -> None:
    """Resuelve el entorno hijo de ``con`` y propaga sus escrituras externas."""

    instrucciones = nodos.instrucciones if isinstance(nodos, NodoBloque) else nodos
    ambiguos = _nombres_ambiguos(instrucciones)

    for indice, nodo in enumerate(instrucciones):
        if isinstance(nodo, NodoClase):
            declarados_locales.add(nodo.nombre)
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
        if isinstance(nodo, NodoFuncion):
            if isinstance(nodo.nombre, str):
                declarados_locales.add(nodo.nombre)
                bindings[nodo.nombre] = _OTRO
        elif isinstance(nodo, NodoAsignacion) and isinstance(nodo.variable, str):
            nombre = nodo.variable
            es_declaracion = nodo.declaracion or nodo.inferencia
            if es_declaracion:
                declarados_locales.add(nombre)
            if (
                not es_declaracion
                and nombre not in declarados_locales
                and nombre in bindings_padre
            ):
                bindings_padre[nombre] = _OTRO
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

    if isinstance(nodo, NodoCondicional):
        memo[identidad] = nodo
        nodo.condicion = _resolver_nodo(nodo.condicion, bindings, ambiguos, memo)
        bindings_si = bindings.copy()
        _resolver_bloque(nodo.bloque_si, bindings_si, memo)
        bindings_sino = bindings.copy()
        _resolver_bloque(nodo.bloque_sino, bindings_sino, memo)
        _fusionar_bindings(bindings, (bindings_si, bindings_sino))
        return nodo

    if isinstance(nodo, NodoBucleMientras):
        memo[identidad] = nodo
        nodo.condicion = _resolver_nodo(nodo.condicion, bindings, ambiguos, memo)
        bindings_iteracion = bindings.copy()
        _resolver_bloque(nodo.cuerpo, bindings_iteracion, memo)
        _fusionar_bindings(bindings, (bindings.copy(), bindings_iteracion))
        return nodo

    if isinstance(nodo, NodoPara):
        memo[identidad] = nodo
        nodo.iterable = _resolver_nodo(nodo.iterable, bindings, ambiguos, memo)
        bindings_iteracion = bindings.copy()
        if isinstance(nodo.variable, str):
            bindings_iteracion[nodo.variable] = _OTRO
        _resolver_bloque(nodo.cuerpo, bindings_iteracion, memo)
        _fusionar_bindings(bindings, (bindings.copy(), bindings_iteracion))
        return nodo

    if isinstance(nodo, NodoWith):
        memo[identidad] = nodo
        nodo.contexto = _resolver_nodo(nodo.contexto, bindings, ambiguos, memo)
        bindings_locales = bindings.copy()
        declarados_locales: set[str] = set()
        if isinstance(nodo.alias, str):
            bindings_locales[nodo.alias] = _OTRO
            declarados_locales.add(nodo.alias)
        _resolver_bloque_con(
            nodo.cuerpo, bindings_locales, bindings, memo, declarados_locales
        )
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
