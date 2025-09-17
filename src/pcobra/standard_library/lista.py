"""Utilidades para manejar listas."""

from __future__ import annotations

from typing import Any, Callable, Iterable, List, Sequence, Tuple

from corelibs.coleccion import tomar as tomar_core


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

