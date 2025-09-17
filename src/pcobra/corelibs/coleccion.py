"""Funciones para trabajar con colecciones."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Iterable, List, Sequence, Tuple, TypeVar

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")

_SIN_VALOR = object()


def _asegurar_iterable(valor: Iterable[T] | Sequence[T], nombre: str = "lista") -> List[T]:
    try:
        return list(valor)
    except TypeError as exc:  # pragma: no cover - rama de validación
        raise TypeError(f"{nombre} debe ser iterable") from exc


def _asegurar_callable(funcion: Callable[..., Any], nombre: str = "funcion") -> Callable[..., Any]:
    if not callable(funcion):
        raise TypeError(f"{nombre} debe ser invocable")
    return funcion


def _obtener_funcion_clave(clave: Callable[[T], K] | str) -> Callable[[T], K]:
    if callable(clave):
        return clave

    if isinstance(clave, str):
        def extractor(valor: T) -> K:  # type: ignore[return-value]
            if isinstance(valor, dict):
                if clave not in valor:
                    raise KeyError(f"La clave '{clave}' no existe en el diccionario")
                return valor[clave]  # type: ignore[return-value]
            if hasattr(valor, clave):
                return getattr(valor, clave)
            raise AttributeError(f"El atributo '{clave}' no existe en el objeto {valor!r}")

        return extractor

    raise TypeError("clave debe ser una función o una cadena")


def ordenar(lista: Iterable[T] | Sequence[T]) -> List[T]:
    """Devuelve una copia ordenada de *lista*."""
    return sorted(_asegurar_iterable(lista))


def maximo(lista: Iterable[T] | Sequence[T]) -> T:
    """Devuelve el valor máximo de *lista*."""
    elementos = _asegurar_iterable(lista)
    if not elementos:
        raise ValueError("maximo() no acepta listas vacías")
    return max(elementos)


def minimo(lista: Iterable[T] | Sequence[T]) -> T:
    """Devuelve el valor mínimo de *lista*."""
    elementos = _asegurar_iterable(lista)
    if not elementos:
        raise ValueError("minimo() no acepta listas vacías")
    return min(elementos)


def sin_duplicados(lista: Iterable[T] | Sequence[T]) -> List[T]:
    """Retorna una lista sin elementos duplicados manteniendo el orden."""
    elementos = _asegurar_iterable(lista)
    return list(dict.fromkeys(elementos))


def mapear(lista: Iterable[T] | Sequence[T], funcion: Callable[[T], U]) -> List[U]:
    """Aplica ``funcion`` a cada elemento de ``lista`` preservando el orden."""

    elementos = _asegurar_iterable(lista)
    fn = _asegurar_callable(funcion)
    return [fn(elem) for elem in elementos]


def filtrar(lista: Iterable[T] | Sequence[T], funcion: Callable[[T], bool]) -> List[T]:
    """Retorna los elementos de ``lista`` para los que ``funcion`` sea verdadera."""

    elementos = _asegurar_iterable(lista)
    fn = _asegurar_callable(funcion)
    return [elem for elem in elementos if fn(elem)]


def reducir(
    lista: Iterable[T] | Sequence[T],
    funcion: Callable[[U, T], U],
    inicial: U | object = _SIN_VALOR,
) -> U:
    """Reduce ``lista`` a un único valor utilizando ``funcion``."""

    elementos = iter(_asegurar_iterable(lista))
    fn = _asegurar_callable(funcion)

    if inicial is _SIN_VALOR:
        try:
            acumulado = next(elementos)  # type: ignore[assignment]
        except StopIteration as exc:
            raise ValueError(
                "reducir() necesita al menos un elemento o un valor inicial"
            ) from exc
    else:
        acumulado = inicial

    for elemento in elementos:
        acumulado = fn(acumulado, elemento)
    return acumulado  # type: ignore[return-value]


def encontrar(
    lista: Iterable[T] | Sequence[T],
    funcion: Callable[[T], bool],
    predeterminado: U | None = None,
) -> T | U | None:
    """Devuelve el primer elemento que cumpla ``funcion`` o ``predeterminado``."""

    elementos = _asegurar_iterable(lista)
    fn = _asegurar_callable(funcion)
    for elemento in elementos:
        if fn(elemento):
            return elemento
    return predeterminado


def _es_iterable_aplanable(valor: Any) -> bool:
    return isinstance(valor, (list, tuple))


def aplanar(lista: Iterable[Any] | Sequence[Any]) -> List[Any]:
    """Aplana un nivel de anidación en ``lista`` preservando el orden."""

    elementos = _asegurar_iterable(lista)
    resultado: List[Any] = []
    for elemento in elementos:
        if _es_iterable_aplanable(elemento):
            resultado.extend(elemento)
        else:
            resultado.append(elemento)
    return resultado


def agrupar_por(
    lista: Iterable[T] | Sequence[T], clave: Callable[[T], K] | str
) -> OrderedDict[K, List[T]]:
    """Agrupa ``lista`` según ``clave`` preservando el orden de aparición."""

    elementos = _asegurar_iterable(lista)
    obtener = _obtener_funcion_clave(clave)
    grupos: "OrderedDict[K, List[T]]" = OrderedDict()
    for elemento in elementos:
        llave = obtener(elemento)
        grupos.setdefault(llave, []).append(elemento)
    return grupos


def particionar(
    lista: Iterable[T] | Sequence[T], funcion: Callable[[T], bool]
) -> Tuple[List[T], List[T]]:
    """Divide ``lista`` en dos listas según ``funcion``."""

    elementos = _asegurar_iterable(lista)
    fn = _asegurar_callable(funcion)
    verdaderos: List[T] = []
    falsos: List[T] = []
    for elemento in elementos:
        (verdaderos if fn(elemento) else falsos).append(elemento)
    return verdaderos, falsos


def mezclar(
    lista: Iterable[T] | Sequence[T], semilla: int | None = None
) -> List[T]:
    """Retorna una copia de ``lista`` con los elementos reordenados aleatoriamente."""

    import random

    elementos = _asegurar_iterable(lista)
    resultado = list(elementos)
    generador = random.Random(semilla) if semilla is not None else random
    generador.shuffle(resultado)
    return resultado


def zip_listas(*listas: Iterable[T] | Sequence[T]) -> List[Tuple[Any, ...]]:
    """Combina varias listas en tuplas respetando el orden y la longitud mínima."""

    if not listas:
        return []
    materiales = [_asegurar_iterable(lista, nombre=f"lista_{indice + 1}") for indice, lista in enumerate(listas)]
    return [tuple(elementos) for elementos in zip(*materiales)]


def tomar(lista: Iterable[T] | Sequence[T], cantidad: int) -> List[T]:
    """Devuelve los primeros ``cantidad`` elementos de ``lista``."""

    if not isinstance(cantidad, int):
        raise TypeError("cantidad debe ser un entero")
    if cantidad < 0:
        raise ValueError("cantidad debe ser positiva")
    elementos = _asegurar_iterable(lista)
    return elementos[:cantidad]
