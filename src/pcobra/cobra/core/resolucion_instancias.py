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
    NodoNoLocal,
    NodoPara,
    NodoWith,
)

_CLASE = "clase"
_OTRO = "otro"
_AMBIGUO = "ambiguo"
_GLOBAL = "global"
_LOCAL = "local"
_NONLOCAL = "nolocal"
_ALCANCE_AMBIGUO = "alcance_ambiguo"
Bindings = dict[str, str]
Alcances = dict[str, str]
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


def _fusionar_alcances(alcances: Alcances, caminos: Iterable[Alcances]) -> None:
    """Fusiona si cada nombre es global, local o dependiente del camino."""

    estados = list(caminos)
    nombres = set().union(alcances, *(estado.keys() for estado in estados))
    for nombre in nombres:
        valores = {estado.get(nombre, _LOCAL) for estado in estados}
        if len(valores) == 1:
            alcances[nombre] = valores.pop()
        else:
            alcances[nombre] = _ALCANCE_AMBIGUO


def resolver_instanciaciones(ast: list[NodoAST]) -> list[NodoAST]:
    """Convierte llamadas a clases ya declaradas en ``NodoInstancia``.

    La resolución respeta el orden de declaración. Si un ámbito declara una
    clase y una función con el mismo nombre, conserva la llamada neutral sin
    elegir arbitrariamente entre ambos símbolos; el analizador semántico es
    quien informa después de la colisión de declaraciones.
    """

    _resolver_bloque(ast, {}, {}, globales={}, scope_global=True)
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


def _resolver_bloque(
    nodos: Any,
    bindings: Bindings,
    memo: Memo,
    *,
    globales: Alcances,
    scope_global: bool = False,
    escrituras_externas: Bindings | None = None,
    nombres_externos: set[str] | None = None,
) -> None:
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
                _resolver_nodo(
                    metodo,
                    bindings_de_metodos,
                    ambiguos,
                    memo,
                    globales=globales,
                    scope_global=False,
                )
            bindings[nodo.nombre] = (
                _OTRO if nodo.nombre in ambiguos else _CLASE
            )
            if scope_global:
                globales[nodo.nombre] = _GLOBAL
            else:
                globales[nodo.nombre] = _LOCAL
            if nombres_externos is not None:
                nombres_externos.discard(nodo.nombre)
            continue

        instrucciones[indice] = _resolver_nodo(
            nodo,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        if isinstance(nodo, (NodoFuncion, NodoAsignacion)):
            nombre = nodo.nombre if isinstance(nodo, NodoFuncion) else nodo.variable
            if isinstance(nombre, str):
                bindings[nombre] = _OTRO
                es_declaracion = isinstance(nodo, NodoFuncion) or (
                    nodo.declaracion or nodo.inferencia
                )
                if es_declaracion:
                    if nombres_externos is not None:
                        nombres_externos.discard(nombre)
                    if scope_global:
                        globales[nombre] = _GLOBAL
                    else:
                        globales[nombre] = _LOCAL
                elif escrituras_externas is not None:
                    alcance = globales.get(nombre, _LOCAL)
                    if nombre not in (nombres_externos or set()):
                        continue
                    if alcance in (_GLOBAL, _NONLOCAL):
                        escrituras_externas[nombre] = _OTRO
                    elif alcance == _ALCANCE_AMBIGUO:
                        escrituras_externas[nombre] = _AMBIGUO


def _resolver_bloque_con(
    nodos: Any,
    bindings: Bindings,
    bindings_padre: Bindings,
    memo: Memo,
    declarados_locales: set[str],
    globales: Alcances,
    escrituras_padre: Bindings | None,
    nombres_externos_padre: set[str] | None,
) -> None:
    """Resuelve ``con`` y compone escrituras a bindings léxicos exteriores."""

    escrituras: Bindings = {}
    nombres_externos = set(bindings_padre)
    _resolver_bloque(
        nodos,
        bindings,
        memo,
        globales=globales,
        escrituras_externas=escrituras,
        nombres_externos=nombres_externos,
    )
    for nombre, estado in escrituras.items():
        if nombre not in declarados_locales:
            bindings_padre[nombre] = estado
            if (
                escrituras_padre is not None
                and nombre in (nombres_externos_padre or set())
            ):
                escrituras_padre[nombre] = estado


def _resolver_nodo(
    nodo: Any,
    bindings: Bindings,
    ambiguos: set[str],
    memo: Memo,
    *,
    globales: Alcances,
    scope_global: bool,
    escrituras_externas: Bindings | None = None,
    nombres_externos: set[str] | None = None,
) -> Any:
    identidad = id(nodo)
    if identidad in memo:
        return memo[identidad]

    if isinstance(nodo, NodoLlamadaFuncion):
        argumentos = [
            _resolver_nodo(
                argumento,
                bindings,
                ambiguos,
                memo,
                globales=globales,
                scope_global=scope_global,
                escrituras_externas=escrituras_externas,
                nombres_externos=nombres_externos,
            )
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
        globales_locales = globales.copy()
        globales_locales.update((parametro, _LOCAL) for parametro in nodo.parametros)
        _resolver_bloque(
            nodo.cuerpo,
            bindings_locales,
            memo,
            globales=globales_locales,
            scope_global=False,
        )
        return nodo

    if isinstance(nodo, NodoNoLocal):
        memo[identidad] = nodo
        for nombre in nodo.nombres:
            if globales.get(nombre) in (_LOCAL, _NONLOCAL):
                globales[nombre] = _NONLOCAL
        return nodo

    if isinstance(nodo, NodoCondicional):
        memo[identidad] = nodo
        nodo.condicion = _resolver_nodo(
            nodo.condicion,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        bindings_si = bindings.copy()
        globales_si = globales.copy()
        nombres_externos_si = (
            nombres_externos.copy() if nombres_externos is not None else None
        )
        escrituras_si = (
            escrituras_externas.copy()
            if escrituras_externas is not None
            else None
        )
        _resolver_bloque(
            nodo.bloque_si,
            bindings_si,
            memo,
            globales=globales_si,
            scope_global=scope_global,
            escrituras_externas=escrituras_si,
            nombres_externos=nombres_externos_si,
        )
        bindings_sino = bindings.copy()
        globales_sino = globales.copy()
        nombres_externos_sino = (
            nombres_externos.copy() if nombres_externos is not None else None
        )
        escrituras_sino = (
            escrituras_externas.copy()
            if escrituras_externas is not None
            else None
        )
        _resolver_bloque(
            nodo.bloque_sino,
            bindings_sino,
            memo,
            globales=globales_sino,
            scope_global=scope_global,
            escrituras_externas=escrituras_sino,
            nombres_externos=nombres_externos_sino,
        )
        _fusionar_bindings(bindings, (bindings_si, bindings_sino))
        _fusionar_alcances(globales, (globales_si, globales_sino))
        if nombres_externos is not None:
            nombres_externos.clear()
            nombres_externos.update(
                (nombres_externos_si or set()) | (nombres_externos_sino or set())
            )
        if escrituras_externas is not None:
            _fusionar_bindings(
                escrituras_externas, (escrituras_si or {}, escrituras_sino or {})
            )
        return nodo

    if isinstance(nodo, NodoBucleMientras):
        memo[identidad] = nodo
        nodo.condicion = _resolver_nodo(
            nodo.condicion,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        bindings_iteracion = bindings.copy()
        globales_iteracion = globales.copy()
        nombres_externos_iteracion = (
            nombres_externos.copy() if nombres_externos is not None else None
        )
        escrituras_antes = (
            escrituras_externas.copy()
            if escrituras_externas is not None
            else None
        )
        escrituras_iteracion = (
            escrituras_externas.copy()
            if escrituras_externas is not None
            else None
        )
        _resolver_bloque(
            nodo.cuerpo,
            bindings_iteracion,
            memo,
            globales=globales_iteracion,
            scope_global=scope_global,
            escrituras_externas=escrituras_iteracion,
            nombres_externos=nombres_externos_iteracion,
        )
        _fusionar_bindings(bindings, (bindings.copy(), bindings_iteracion))
        _fusionar_alcances(globales, (globales.copy(), globales_iteracion))
        if nombres_externos is not None:
            nombres_externos.update(nombres_externos_iteracion or set())
        if escrituras_externas is not None:
            _fusionar_bindings(
                escrituras_externas,
                (escrituras_antes or {}, escrituras_iteracion or {}),
            )
        return nodo

    if isinstance(nodo, NodoPara):
        memo[identidad] = nodo
        nodo.iterable = _resolver_nodo(
            nodo.iterable,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        bindings_iteracion = bindings.copy()
        globales_iteracion = globales.copy()
        nombres_externos_iteracion = (
            nombres_externos.copy() if nombres_externos is not None else None
        )
        if isinstance(nodo.variable, str):
            bindings_iteracion[nodo.variable] = _OTRO
            globales_iteracion[nodo.variable] = _LOCAL
            if nombres_externos_iteracion is not None:
                nombres_externos_iteracion.discard(nodo.variable)
        escrituras_antes = (
            escrituras_externas.copy()
            if escrituras_externas is not None
            else None
        )
        escrituras_iteracion = (
            escrituras_externas.copy()
            if escrituras_externas is not None
            else None
        )
        _resolver_bloque(
            nodo.cuerpo,
            bindings_iteracion,
            memo,
            globales=globales_iteracion,
            scope_global=scope_global,
            escrituras_externas=escrituras_iteracion,
            nombres_externos=nombres_externos_iteracion,
        )
        _fusionar_bindings(bindings, (bindings.copy(), bindings_iteracion))
        _fusionar_alcances(globales, (globales.copy(), globales_iteracion))
        if nombres_externos is not None:
            nombres_externos.update(nombres_externos_iteracion or set())
        if escrituras_externas is not None:
            _fusionar_bindings(
                escrituras_externas,
                (escrituras_antes or {}, escrituras_iteracion or {}),
            )
        return nodo

    if isinstance(nodo, NodoWith):
        memo[identidad] = nodo
        nodo.contexto = _resolver_nodo(
            nodo.contexto,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        bindings_locales = bindings.copy()
        globales_locales = globales.copy()
        declarados_locales: set[str] = set()
        if isinstance(nodo.alias, str):
            bindings_locales[nodo.alias] = _OTRO
            globales_locales[nodo.alias] = _LOCAL
            declarados_locales.add(nodo.alias)
        _resolver_bloque_con(
            nodo.cuerpo,
            bindings_locales,
            bindings,
            memo,
            declarados_locales,
            globales_locales,
            escrituras_externas,
            nombres_externos,
        )
        return nodo

    if isinstance(nodo, NodoBloque):
        memo[identidad] = nodo
        _resolver_bloque(
            nodo,
            bindings,
            memo,
            globales=globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        return nodo

    if isinstance(nodo, NodoAST):
        memo[identidad] = nodo
        for nombre, valor in vars(nodo).items():
            if isinstance(valor, NodoAST):
                setattr(
                    nodo,
                    nombre,
                    _resolver_nodo(
                        valor,
                        bindings,
                        ambiguos,
                        memo,
                        globales=globales,
                        scope_global=scope_global,
                        escrituras_externas=escrituras_externas,
                        nombres_externos=nombres_externos,
                    ),
                )
            elif isinstance(valor, list):
                for indice, elemento in enumerate(valor):
                    if isinstance(elemento, NodoAST):
                        valor[indice] = _resolver_nodo(
                            elemento,
                            bindings,
                            ambiguos,
                            memo,
                            globales=globales,
                            scope_global=scope_global,
                            escrituras_externas=escrituras_externas,
                            nombres_externos=nombres_externos,
                        )
        return nodo

    return nodo
