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
    NodoDel,
    NodoFuncion,
    NodoGlobal,
    NodoInstancia,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoMetodo,
    NodoNoLocal,
    NodoPara,
    NodoWith,
)

_CLASE = "clase"
_OTRO = "otro"
_AMBIGUO = "ambiguo"
_ELIMINADO = "eliminado"
_GLOBAL = "global"
_LOCAL = "local"
_LOCAL_PROPIO = "local_propio"
_NONLOCAL = "nolocal"
_ALCANCE_AMBIGUO = "alcance_ambiguo"
Bindings = dict[str, str]
Alcances = dict[str, str]
CadenaExterior = tuple[tuple[str, str], ...]
BindingsExteriores = dict[str, CadenaExterior]
Procedencias = dict[str, str]
Memo = dict[int, Any]
_CADENA_EXTERIOR_AMBIGUA: CadenaExterior = ((_AMBIGUO, _ALCANCE_AMBIGUO),)
_PROCEDENCIA_LOCAL = "local"
_PROCEDENCIA_EXTERIOR = "exterior"
_PROCEDENCIA_MIXTA = "mixta"


def _anteponer_binding_exterior(
    bindings_exteriores: BindingsExteriores,
    nombre: str,
    estado: str,
    alcance: str,
) -> None:
    """Conserva una capa conocida aun si precede a una cola ambigua."""

    bindings_exteriores[nombre] = (
        (estado, alcance),
        *bindings_exteriores.get(nombre, ()),
    )


def _es_binding_exterior_recuperable(
    nombre: str,
    procedencias: Procedencias | None,
) -> bool:
    """Indica si el estado visible es recuperable tras una declaración local."""

    procedencia = (procedencias or {}).get(nombre, _PROCEDENCIA_LOCAL)
    return procedencia == _PROCEDENCIA_EXTERIOR


def _fusionar_procedencias(
    procedencias: Procedencias | None,
    caminos: Iterable[Procedencias],
) -> None:
    """Conserva si el binding es local, exterior o depende del camino."""

    if procedencias is None:
        return
    estados = list(caminos)
    nombres = set().union(procedencias, *(estado.keys() for estado in estados))
    for nombre in nombres:
        valores = {
            estado.get(nombre, _PROCEDENCIA_LOCAL) for estado in estados
        }
        procedencias[nombre] = (
            valores.pop() if len(valores) == 1 else _PROCEDENCIA_MIXTA
        )


def _alcance_desde_funcion_hija(alcance: str) -> str:
    """Hace relativo al scope hijo el ownership recibido de su padre."""

    if alcance == _LOCAL_PROPIO:
        return _LOCAL
    return alcance


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


def _fusionar_bindings_exteriores(
    bindings_exteriores: BindingsExteriores | None,
    caminos: Iterable[BindingsExteriores],
    *,
    bindings_caminos: Iterable[Bindings] | None = None,
    alcances_caminos: Iterable[Alcances] | None = None,
    procedencias_caminos: Iterable[Procedencias] | None = None,
) -> None:
    """Conserva una cadena exterior sólo si coincide en todos los caminos."""

    if bindings_exteriores is None:
        return
    estados = list(caminos)
    if (
        bindings_caminos is not None
        and alcances_caminos is not None
        and procedencias_caminos is not None
    ):
        bindings_por_camino = list(bindings_caminos)
        alcances_por_camino = list(alcances_caminos)
        procedencias_por_camino = list(procedencias_caminos)
        estados = [dict(estado) for estado in estados]
        nombres = set().union(*(estado.keys() for estado in procedencias_por_camino))
        for nombre in nombres:
            procedencias_nombre = {
                estado.get(nombre, _PROCEDENCIA_LOCAL)
                for estado in procedencias_por_camino
            }
            estados_visibles = {
                estado.get(nombre, _AMBIGUO) for estado in bindings_por_camino
            }
            if len(procedencias_nombre) == 1 or len(estados_visibles) != 1:
                continue
            for indice, procedencias in enumerate(procedencias_por_camino):
                if (
                    procedencias.get(nombre, _PROCEDENCIA_LOCAL)
                    == _PROCEDENCIA_EXTERIOR
                    and nombre in bindings_por_camino[indice]
                ):
                    estados[indice][nombre] = (
                        (
                            bindings_por_camino[indice][nombre],
                            alcances_por_camino[indice].get(nombre, _LOCAL),
                        ),
                        *estados[indice].get(nombre, ()),
                    )
            cadenas = [estado.get(nombre, ()) for estado in estados]
            if cadenas and all(cadena == cadenas[0] for cadena in cadenas):
                cadena = cadenas[0]
                if cadena:
                    estados[0][nombre] = (
                        (cadena[0][0], _ALCANCE_AMBIGUO), *cadena[1:]
                    )
                    for indice in range(1, len(estados)):
                        estados[indice][nombre] = estados[0][nombre]
    nombres = set().union(
        bindings_exteriores, *(estado.keys() for estado in estados)
    )
    ausente = object()
    for nombre in nombres:
        valores = set()
        for estado in estados:
            valor = estado.get(nombre, ausente)
            valores.add(ausente if valor == () else valor)
        if len(valores) == 1:
            valor = valores.pop()
            if valor is ausente:
                bindings_exteriores.pop(nombre, None)
            else:
                bindings_exteriores[nombre] = valor
        else:
            bindings_exteriores[nombre] = _CADENA_EXTERIOR_AMBIGUA


def resolver_instanciaciones(ast: list[NodoAST]) -> list[NodoAST]:
    """Convierte llamadas a clases ya declaradas en ``NodoInstancia``.

    La resolución respeta el orden de declaración. Si un ámbito declara una
    clase y una función con el mismo nombre, conserva la llamada neutral sin
    elegir arbitrariamente entre ambos símbolos; el analizador semántico es
    quien informa después de la colisión de declaraciones.
    """

    _resolver_bloque(
        ast, {}, {}, globales={}, bindings_globales={}, scope_global=True
    )
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
    bindings_globales: Bindings,
    scope_global: bool = False,
    escrituras_externas: Bindings | None = None,
    nombres_externos: Procedencias | None = None,
    bindings_exteriores: BindingsExteriores | None = None,
) -> None:
    instrucciones = nodos.instrucciones if isinstance(nodos, NodoBloque) else nodos
    ambiguos = _nombres_ambiguos(instrucciones)

    for indice, nodo in enumerate(instrucciones):
        if isinstance(nodo, NodoClase):
            clase_actual = {nodo.nombre} if nodo.nombre not in ambiguos else set()
            estado_clase = _OTRO if nodo.nombre in ambiguos else _CLASE
            if scope_global:
                bindings_globales[nodo.nombre] = estado_clase
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
                    bindings_globales=bindings_globales,
                    scope_global=False,
                )
            if (
                not scope_global
                and bindings_exteriores is not None
                and nodo.nombre in bindings
                and _es_binding_exterior_recuperable(
                    nodo.nombre, nombres_externos
                )
            ):
                # Un ``con`` hermano debe conservar la invalidación que recibió
                # del padre; fuera de ese alias temporal, el binding visible sí
                # es una capa léxica conocida que precede a la cola ambigua.
                if (
                    escrituras_externas is None
                    or bindings_exteriores.get(nodo.nombre)
                    != _CADENA_EXTERIOR_AMBIGUA
                ):
                    _anteponer_binding_exterior(
                        bindings_exteriores,
                        nodo.nombre,
                        bindings[nodo.nombre],
                        globales.get(nodo.nombre, _LOCAL),
                    )
            bindings[nodo.nombre] = estado_clase
            if scope_global:
                globales[nodo.nombre] = _GLOBAL
            else:
                globales[nodo.nombre] = _LOCAL_PROPIO
            if nombres_externos is not None:
                nombres_externos[nodo.nombre] = _PROCEDENCIA_LOCAL
            continue

        instrucciones[indice] = _resolver_nodo(
            nodo,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            bindings_globales=bindings_globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
            bindings_exteriores=bindings_exteriores,
        )
        if isinstance(nodo, (NodoFuncion, NodoAsignacion)):
            nombre = nodo.nombre if isinstance(nodo, NodoFuncion) else nodo.variable
            if isinstance(nombre, str):
                es_declaracion = isinstance(nodo, NodoFuncion) or (
                    nodo.declaracion or nodo.inferencia
                )
                if es_declaracion:
                    if (
                        not scope_global
                        and bindings_exteriores is not None
                        and nombre in bindings
                        and _es_binding_exterior_recuperable(
                            nombre, nombres_externos
                        )
                    ):
                        # Dentro de ``con`` la cola puede proceder de otro alias
                        # hermano y no constituye una capa concreta recuperable.
                        if (
                            escrituras_externas is None
                            or bindings_exteriores.get(nombre)
                            != _CADENA_EXTERIOR_AMBIGUA
                        ):
                            _anteponer_binding_exterior(
                                bindings_exteriores,
                                nombre,
                                bindings[nombre],
                                globales.get(nombre, _LOCAL),
                            )
                bindings[nombre] = _OTRO
                if es_declaracion:
                    if nombres_externos is not None:
                        nombres_externos[nombre] = _PROCEDENCIA_LOCAL
                    if scope_global:
                        globales[nombre] = _GLOBAL
                        bindings_globales[nombre] = _OTRO
                    else:
                        globales[nombre] = _LOCAL_PROPIO
                else:
                    alcance = globales.get(nombre, _LOCAL)
                    if alcance == _GLOBAL:
                        bindings_globales[nombre] = _OTRO
                    if escrituras_externas is None:
                        continue
                    if (nombres_externos or {}).get(nombre) not in (
                        _PROCEDENCIA_EXTERIOR,
                        _PROCEDENCIA_MIXTA,
                    ):
                        continue
                    if alcance in (_GLOBAL, _NONLOCAL):
                        escrituras_externas[nombre] = _OTRO
                        if alcance == _GLOBAL:
                            bindings_globales[nombre] = _OTRO
                    elif alcance == _ALCANCE_AMBIGUO:
                        escrituras_externas[nombre] = _AMBIGUO


def _resolver_bloque_con(
    nodos: Any,
    bindings: Bindings,
    bindings_padre: Bindings,
    memo: Memo,
    declarados_locales: set[str],
    globales: Alcances,
    bindings_globales: Bindings,
    bindings_globales_padre: Bindings,
    globales_padre: Alcances,
    escrituras_padre: Bindings | None,
    nombres_externos_padre: Procedencias | None,
    bindings_exteriores_padre: BindingsExteriores | None,
) -> None:
    """Resuelve ``con`` y compone escrituras a bindings léxicos exteriores."""

    escrituras: Bindings = {}
    nombres_externos = {
        nombre: _PROCEDENCIA_EXTERIOR for nombre in bindings_padre
    }
    bindings_exteriores = {
        nombre: cadena
        for nombre, cadena in (bindings_exteriores_padre or {}).items()
        if cadena
    }
    _resolver_bloque(
        nodos,
        bindings,
        memo,
        globales=globales,
        bindings_globales=bindings_globales,
        escrituras_externas=escrituras,
        nombres_externos=nombres_externos,
        bindings_exteriores=bindings_exteriores,
    )
    for nombre, alcance in globales.items():
        alcance_padre = globales_padre.get(nombre, _LOCAL)
        if (
            alcance in (_GLOBAL, _NONLOCAL, _ALCANCE_AMBIGUO)
            and alcance != alcance_padre
        ):
            globales_padre[nombre] = alcance
            if bindings_exteriores_padre is not None:
                cadena = bindings_exteriores.get(nombre)
                if cadena is None or cadena == ():
                    bindings_exteriores_padre.pop(nombre, None)
                elif cadena == _CADENA_EXTERIOR_AMBIGUA:
                    bindings_exteriores_padre[nombre] = cadena
            if alcance == _GLOBAL:
                if nombre in bindings_globales:
                    bindings_padre[nombre] = bindings_globales[nombre]
                else:
                    bindings_padre.pop(nombre, None)
            elif alcance == _ALCANCE_AMBIGUO:
                if nombre in bindings:
                    bindings_padre[nombre] = bindings[nombre]
                else:
                    bindings_padre.pop(nombre, None)
    for nombre, estado in escrituras.items():
        # El runtime no materializa el alias de ``con`` en Environment; por
        # ello ``delete`` atraviesa ese nombre y alcanza el binding padre.
        if estado == _ELIMINADO or nombre not in declarados_locales:
            bindings_padre[nombre] = estado
            if globales_padre.get(nombre) == _GLOBAL:
                bindings_globales_padre[nombre] = estado
            if (
                escrituras_padre is not None
                and (nombres_externos_padre or {}).get(nombre)
                in (_PROCEDENCIA_EXTERIOR, _PROCEDENCIA_MIXTA)
            ):
                escrituras_padre[nombre] = estado


def _resolver_nodo(
    nodo: Any,
    bindings: Bindings,
    ambiguos: set[str],
    memo: Memo,
    *,
    globales: Alcances,
    bindings_globales: Bindings,
    scope_global: bool,
    escrituras_externas: Bindings | None = None,
    nombres_externos: Procedencias | None = None,
    bindings_exteriores: BindingsExteriores | None = None,
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
                bindings_globales=bindings_globales,
                scope_global=scope_global,
                escrituras_externas=escrituras_externas,
                nombres_externos=nombres_externos,
                bindings_exteriores=bindings_exteriores,
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
        globales_locales.update(
            (nombre, _LOCAL)
            for nombre, alcance in globales_locales.items()
            if alcance == _LOCAL_PROPIO
        )
        bindings_globales_locales = bindings_globales.copy()
        globales_locales.update(
            (parametro, _LOCAL_PROPIO) for parametro in nodo.parametros
        )
        exteriores_locales = {
            nombre: tuple(
                (estado, _alcance_desde_funcion_hija(alcance))
                for estado, alcance in cadena
            )
            for nombre, cadena in (bindings_exteriores or {}).items()
        }
        for parametro in nodo.parametros:
            if parametro in bindings:
                exteriores_locales[parametro] = (
                    (
                        bindings[parametro],
                        _alcance_desde_funcion_hija(
                            globales.get(parametro, _LOCAL)
                        ),
                    ),
                    *exteriores_locales.get(parametro, ()),
                )
        _resolver_bloque(
            nodo.cuerpo,
            bindings_locales,
            memo,
            globales=globales_locales,
            bindings_globales=bindings_globales_locales,
            scope_global=False,
            nombres_externos={
                nombre: _PROCEDENCIA_EXTERIOR
                for nombre in bindings
                if nombre not in nodo.parametros
            }
            | {
                parametro: _PROCEDENCIA_LOCAL for parametro in nodo.parametros
            },
            bindings_exteriores=exteriores_locales,
        )
        return nodo

    if isinstance(nodo, NodoDel):
        memo[identidad] = nodo
        if not isinstance(nodo.objetivo, NodoIdentificador):
            return nodo
        nombre = nodo.objetivo.nombre
        if nombre not in bindings or bindings[nombre] == _ELIMINADO:
            return nodo

        procedencia = (nombres_externos or {}).get(
            nombre, _PROCEDENCIA_LOCAL
        )
        if procedencia == _PROCEDENCIA_MIXTA:
            bindings[nombre] = _AMBIGUO
            globales[nombre] = _ALCANCE_AMBIGUO
            if bindings_exteriores is not None:
                bindings_exteriores[nombre] = _CADENA_EXTERIOR_AMBIGUA
            if escrituras_externas is not None:
                escrituras_externas[nombre] = _AMBIGUO
            return nodo

        es_exterior = (nombres_externos or {}).get(nombre) == _PROCEDENCIA_EXTERIOR
        if not es_exterior:
            cadena = (bindings_exteriores or {}).get(nombre, ())
            if cadena == _CADENA_EXTERIOR_AMBIGUA:
                bindings[nombre] = _AMBIGUO
                globales[nombre] = _ALCANCE_AMBIGUO
                return nodo
            if cadena:
                bindings[nombre], globales[nombre] = cadena[0]
                bindings_exteriores[nombre] = cadena[1:]
                if nombres_externos is not None:
                    nombres_externos[nombre] = (
                        _PROCEDENCIA_MIXTA
                        if globales[nombre] == _ALCANCE_AMBIGUO
                        else _PROCEDENCIA_EXTERIOR
                    )
            else:
                bindings[nombre] = _ELIMINADO
            return nodo

        alcance_eliminado = globales.get(nombre, _LOCAL)
        cadena = (bindings_exteriores or {}).get(nombre, ())
        if cadena == _CADENA_EXTERIOR_AMBIGUA:
            bindings[nombre] = _AMBIGUO
            globales[nombre] = _ALCANCE_AMBIGUO
            if escrituras_externas is not None:
                escrituras_externas[nombre] = _AMBIGUO
            return nodo
        if cadena:
            bindings[nombre], globales[nombre] = cadena[0]
            bindings_exteriores[nombre] = cadena[1:]
        else:
            bindings[nombre] = _ELIMINADO
        if alcance_eliminado == _GLOBAL:
            bindings_globales[nombre] = _ELIMINADO
        if escrituras_externas is not None and es_exterior:
            escrituras_externas[nombre] = _ELIMINADO
        return nodo

    if isinstance(nodo, NodoGlobal):
        memo[identidad] = nodo
        if scope_global:
            return nodo
        for nombre in nodo.nombres:
            alcance = globales.get(nombre, _LOCAL)
            if alcance in (_NONLOCAL, _LOCAL_PROPIO):
                globales[nombre] = _ALCANCE_AMBIGUO
                bindings[nombre] = _AMBIGUO
            else:
                globales[nombre] = _GLOBAL
                if bindings_exteriores is not None:
                    bindings_exteriores.pop(nombre, None)
                if nombre in bindings_globales:
                    bindings[nombre] = bindings_globales[nombre]
                    if nombres_externos is not None:
                        nombres_externos[nombre] = _PROCEDENCIA_EXTERIOR
                else:
                    bindings.pop(nombre, None)
                    if nombres_externos is not None:
                        nombres_externos.pop(nombre, None)
        return nodo

    if isinstance(nodo, NodoNoLocal):
        memo[identidad] = nodo
        for nombre in nodo.nombres:
            alcance = globales.get(nombre)
            if alcance in (_GLOBAL, _LOCAL_PROPIO):
                globales[nombre] = _ALCANCE_AMBIGUO
                bindings[nombre] = _AMBIGUO
            elif alcance in (_LOCAL, _NONLOCAL):
                globales[nombre] = _NONLOCAL
                if nombres_externos is not None:
                    nombres_externos[nombre] = _PROCEDENCIA_EXTERIOR
        return nodo

    if isinstance(nodo, NodoCondicional):
        memo[identidad] = nodo
        nodo.condicion = _resolver_nodo(
            nodo.condicion,
            bindings,
            ambiguos,
            memo,
            globales=globales,
            bindings_globales=bindings_globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
        )
        bindings_si = bindings.copy()
        globales_si = globales.copy()
        bindings_globales_si = bindings_globales.copy()
        exteriores_si = dict(bindings_exteriores or {})
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
            bindings_globales=bindings_globales_si,
            scope_global=scope_global,
            escrituras_externas=escrituras_si,
            nombres_externos=nombres_externos_si,
            bindings_exteriores=exteriores_si,
        )
        bindings_sino = bindings.copy()
        globales_sino = globales.copy()
        bindings_globales_sino = bindings_globales.copy()
        exteriores_sino = dict(bindings_exteriores or {})
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
            bindings_globales=bindings_globales_sino,
            scope_global=scope_global,
            escrituras_externas=escrituras_sino,
            nombres_externos=nombres_externos_sino,
            bindings_exteriores=exteriores_sino,
        )
        _fusionar_bindings(bindings, (bindings_si, bindings_sino))
        _fusionar_alcances(globales, (globales_si, globales_sino))
        _fusionar_bindings(
            bindings_globales,
            (bindings_globales_si, bindings_globales_sino),
        )
        _fusionar_bindings_exteriores(
            bindings_exteriores,
            (exteriores_si, exteriores_sino),
            bindings_caminos=(bindings_si, bindings_sino),
            alcances_caminos=(globales_si, globales_sino),
            procedencias_caminos=(
                nombres_externos_si or {},
                nombres_externos_sino or {},
            ),
        )
        if nombres_externos is not None:
            _fusionar_procedencias(
                nombres_externos,
                (nombres_externos_si or {}, nombres_externos_sino or {}),
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
            bindings_globales=bindings_globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
            bindings_exteriores=bindings_exteriores,
        )
        bindings_iteracion = bindings.copy()
        globales_iteracion = globales.copy()
        bindings_globales_iteracion = bindings_globales.copy()
        exteriores_antes = dict(bindings_exteriores or {})
        exteriores_iteracion = dict(bindings_exteriores or {})
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
            bindings_globales=bindings_globales_iteracion,
            scope_global=scope_global,
            escrituras_externas=escrituras_iteracion,
            nombres_externos=nombres_externos_iteracion,
            bindings_exteriores=exteriores_iteracion,
        )
        _fusionar_bindings(bindings, (bindings.copy(), bindings_iteracion))
        _fusionar_alcances(globales, (globales.copy(), globales_iteracion))
        _fusionar_bindings(
            bindings_globales,
            (bindings_globales.copy(), bindings_globales_iteracion),
        )
        _fusionar_bindings_exteriores(
            bindings_exteriores, (exteriores_antes, exteriores_iteracion)
        )
        if nombres_externos is not None:
            _fusionar_procedencias(
                nombres_externos,
                (nombres_externos.copy(), nombres_externos_iteracion or {}),
            )
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
            bindings_globales=bindings_globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
            bindings_exteriores=bindings_exteriores,
        )
        bindings_iteracion = bindings.copy()
        globales_iteracion = globales.copy()
        bindings_globales_iteracion = bindings_globales.copy()
        exteriores_antes = dict(bindings_exteriores or {})
        exteriores_iteracion = dict(bindings_exteriores or {})
        nombres_externos_iteracion = (
            nombres_externos.copy() if nombres_externos is not None else None
        )
        if isinstance(nodo.variable, str):
            alcance_target = globales.get(nodo.variable, _LOCAL)
            crea_local = alcance_target == _LOCAL
            if crea_local and nodo.variable in bindings:
                exteriores_iteracion[nodo.variable] = (
                    (bindings[nodo.variable], alcance_target),
                    *exteriores_iteracion.get(nodo.variable, ()),
                )
            elif alcance_target == _ALCANCE_AMBIGUO:
                # El target puede escribir en bindings exteriores distintos
                # según el camino; ninguna cadena concreta es segura tras él.
                exteriores_iteracion.pop(nodo.variable, None)
            bindings_iteracion[nodo.variable] = _OTRO
            if crea_local:
                globales_iteracion[nodo.variable] = _LOCAL_PROPIO
            if crea_local and nombres_externos_iteracion is not None:
                nombres_externos_iteracion[
                    nodo.variable
                ] = _PROCEDENCIA_LOCAL
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
            bindings_globales=bindings_globales_iteracion,
            scope_global=scope_global,
            escrituras_externas=escrituras_iteracion,
            nombres_externos=nombres_externos_iteracion,
            bindings_exteriores=exteriores_iteracion,
        )
        _fusionar_bindings(bindings, (bindings.copy(), bindings_iteracion))
        _fusionar_alcances(globales, (globales.copy(), globales_iteracion))
        _fusionar_bindings(
            bindings_globales,
            (bindings_globales.copy(), bindings_globales_iteracion),
        )
        _fusionar_bindings_exteriores(
            bindings_exteriores, (exteriores_antes, exteriores_iteracion)
        )
        if nombres_externos is not None:
            _fusionar_procedencias(
                nombres_externos,
                (nombres_externos.copy(), nombres_externos_iteracion or {}),
            )
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
            bindings_globales=bindings_globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
            bindings_exteriores=bindings_exteriores,
        )
        bindings_locales = bindings.copy()
        globales_locales = globales.copy()
        bindings_globales_locales = bindings_globales.copy()
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
            bindings_globales_locales,
            bindings_globales,
            globales,
            escrituras_externas,
            nombres_externos,
            bindings_exteriores,
        )
        return nodo

    if isinstance(nodo, NodoBloque):
        memo[identidad] = nodo
        _resolver_bloque(
            nodo,
            bindings,
            memo,
            globales=globales,
            bindings_globales=bindings_globales,
            scope_global=scope_global,
            escrituras_externas=escrituras_externas,
            nombres_externos=nombres_externos,
            bindings_exteriores=bindings_exteriores,
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
                        bindings_globales=bindings_globales,
                        scope_global=scope_global,
                        escrituras_externas=escrituras_externas,
                        nombres_externos=nombres_externos,
                        bindings_exteriores=bindings_exteriores,
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
                            bindings_globales=bindings_globales,
                            scope_global=scope_global,
                            escrituras_externas=escrituras_externas,
                            nombres_externos=nombres_externos,
                            bindings_exteriores=bindings_exteriores,
                        )
        return nodo

    return nodo
