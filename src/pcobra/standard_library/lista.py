"""Utilidades para manejar listas."""

from __future__ import annotations

from typing import Any, Callable, Iterable, List, Sequence, Tuple

from corelibs.coleccion import (
    mapear_aplanado as mapear_aplanado_core,
    tomar as tomar_core,
    tomar_mientras as tomar_mientras_core,
    descartar_mientras as descartar_mientras_core,
    scanear as scanear_core,
    pares_consecutivos as pares_consecutivos_core,
)

_SIN_INICIAL = object()


def cabeza(lista):
    """Devuelve el primer elemento de ``lista`` o ``None`` si está vacía."""
    return lista[0] if lista else None


def cola(lista):
    """Retorna una copia de ``lista`` sin el primer elemento."""
    return list(lista[1:]) if len(lista) > 1 else []


def longitud(lista) -> int:
    """Número de elementos en ``lista``."""
    return len(lista)


def combinar(*listas):
    """Concatena varias listas en una nueva."""
    resultado = []
    for l in listas:
        resultado.extend(l)
    return resultado


def _asegurar_lista(lista: Iterable[Any] | Sequence[Any]) -> List[Any]:
    try:
        return list(lista)
    except TypeError as exc:  # pragma: no cover - rama defensiva
        raise TypeError("lista debe ser iterable") from exc


def mapear_seguro(
    lista: Iterable[Any] | Sequence[Any],
    funcion: Callable[[Any], Any],
    valor_por_defecto: Any | None = None,
) -> Tuple[List[Any], List[Tuple[Any, Exception]]]:
    """Aplica ``funcion`` controlando errores.

    Devuelve una tupla con los resultados y una lista de pares ``(entrada, error)``
    para los elementos que fallaron. Cuando ocurre una excepción, el resultado se
    rellena con ``valor_por_defecto`` preservando el orden original.
    """

    if not callable(funcion):
        raise TypeError("funcion debe ser invocable")

    elementos = _asegurar_lista(lista)
    resultados: List[Any] = []
    errores: List[Tuple[Any, Exception]] = []
    for elemento in elementos:
        try:
            resultados.append(funcion(elemento))
        except Exception as exc:  # pragma: no cover - dependiente de usuario
            resultados.append(valor_por_defecto)
            errores.append((elemento, exc))
    return resultados, errores


def mapear_aplanado(
    lista: Iterable[Any] | Sequence[Any], funcion: Callable[[Any], Iterable[Any]]
) -> List[Any]:
    """Aplica ``funcion`` y concatena los iterables resultantes en una lista.

    El orden de los elementos producidos se mantiene estable respecto a la
    entrada. Si ``funcion`` devuelve un valor que no sea iterable se lanza un
    ``TypeError`` para facilitar el diagnóstico.
    """

    elementos = _asegurar_lista(lista)
    return mapear_aplanado_core(elementos, funcion)


def ventanas(
    lista: Iterable[Any] | Sequence[Any],
    tamano: int,
    paso: int = 1,
    incluir_incompletas: bool = False,
) -> List[List[Any]]:
    """Genera ventanas deslizantes sobre ``lista``.

    ``tamano`` y ``paso`` deben ser enteros positivos. Cuando ``incluir_incompletas``
    es ``True`` se incluyen las ventanas finales aunque tengan menos elementos.
    """

    if not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un entero positivo")
    if not isinstance(paso, int) or paso <= 0:
        raise ValueError("paso debe ser un entero positivo")

    elementos = _asegurar_lista(lista)
    resultado: List[List[Any]] = []
    for inicio in range(0, len(elementos), paso):
        ventana = tomar_core(elementos[inicio:], tamano)
        if len(ventana) < tamano and not incluir_incompletas:
            break
        if not ventana:
            break
        resultado.append(ventana)
    return resultado


def chunk(
    lista: Iterable[Any] | Sequence[Any], tamano: int, incluir_incompleto: bool = True
) -> List[List[Any]]:
    """Divide ``lista`` en bloques de longitud ``tamano``."""

    if not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un entero positivo")

    elementos = _asegurar_lista(lista)
    resultado: List[List[Any]] = []
    for inicio in range(0, len(elementos), tamano):
        bloque = tomar_core(elementos[inicio:], tamano)
        if len(bloque) < tamano and not incluir_incompleto:
            break
        resultado.append(bloque)
    return resultado


def tomar_mientras(
    lista: Iterable[Any] | Sequence[Any], funcion: Callable[[Any], bool]
) -> List[Any]:
    """Obtiene los elementos iniciales que cumplen ``funcion``."""

    elementos = _asegurar_lista(lista)
    return tomar_mientras_core(elementos, funcion)


def descartar_mientras(
    lista: Iterable[Any] | Sequence[Any], funcion: Callable[[Any], bool]
) -> List[Any]:
    """Elimina elementos iniciales mientras ``funcion`` devuelva ``True``."""

    elementos = _asegurar_lista(lista)
    return descartar_mientras_core(elementos, funcion)


def scanear(
    lista: Iterable[Any] | Sequence[Any],
    funcion: Callable[[Any, Any], Any],
    inicial: Any | object = _SIN_INICIAL,
) -> List[Any]:
    """Devuelve las acumulaciones parciales de ``funcion``."""

    elementos = _asegurar_lista(lista)
    if inicial is _SIN_INICIAL:
        return scanear_core(elementos, funcion)
    return scanear_core(elementos, funcion, inicial)


def pares_consecutivos(lista: Iterable[Any] | Sequence[Any]) -> List[Tuple[Any, Any]]:
    """Construye pares consecutivos ``(anterior, actual)``."""

    elementos = _asegurar_lista(lista)
    return pares_consecutivos_core(elementos)


__all__ = [
    "cabeza",
    "cola",
    "longitud",
    "combinar",
    "mapear_seguro",
    "mapear_aplanado",
    "ventanas",
    "chunk",
    "tomar_mientras",
    "descartar_mientras",
    "scanear",
    "pares_consecutivos",
]

