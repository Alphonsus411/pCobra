"""Operaciones lógicas básicas con validación de tipos."""

from __future__ import annotations

from typing import Iterable


def _asegurar_booleano(valor: bool, nombre: str = "valor") -> bool:
    """Valida que *valor* sea booleano y lo retorna.

    Args:
        valor: objeto a validar.
        nombre: identificador del parámetro para los mensajes de error.

    Raises:
        TypeError: si *valor* no es de tipo :class:`bool`.
    """

    if isinstance(valor, bool):
        return valor
    raise TypeError(f"{nombre} debe ser un booleano, se recibió {type(valor).__name__}")


def conjuncion(a: bool, b: bool) -> bool:
    """Devuelve ``True`` cuando *a* y *b* son verdaderos."""

    a_bool = _asegurar_booleano(a, "a")
    b_bool = _asegurar_booleano(b, "b")
    return a_bool and b_bool


def disyuncion(a: bool, b: bool) -> bool:
    """Devuelve ``True`` si alguno de los argumentos es verdadero."""

    a_bool = _asegurar_booleano(a, "a")
    b_bool = _asegurar_booleano(b, "b")
    return a_bool or b_bool


def negacion(valor: bool) -> bool:
    """Devuelve el opuesto lógico de ``valor``."""

    return not _asegurar_booleano(valor)


def xor(a: bool, b: bool) -> bool:
    """Retorna ``True`` únicamente cuando *a* y *b* difieren."""

    return _asegurar_booleano(a, "a") ^ _asegurar_booleano(b, "b")


def nand(a: bool, b: bool) -> bool:
    """Implementa la operación NAND."""

    return not conjuncion(a, b)


def nor(a: bool, b: bool) -> bool:
    """Implementa la operación NOR."""

    return not disyuncion(a, b)


def implica(antecedente: bool, consecuente: bool) -> bool:
    """Representa la implicación lógica ``antecedente → consecuente``."""

    return disyuncion(negacion(antecedente), consecuente)


def equivale(a: bool, b: bool) -> bool:
    """Devuelve ``True`` si *a* y *b* comparten el mismo valor."""

    return not xor(a, b)


def xor_multiple(*valores: bool) -> bool:
    """Aplica XOR sobre múltiples argumentos.

    Se requiere al menos dos valores para poder evaluar la operación.
    """

    if len(valores) < 2:
        raise ValueError("Se necesitan al menos dos valores booleanos para xor_multiple")

    resultado = False
    for indice, valor in enumerate(valores):
        resultado ^= _asegurar_booleano(valor, f"valor_{indice}")
    return resultado


def todas(valores: Iterable[bool]) -> bool:
    """Devuelve ``True`` si todos los elementos de *valores* son verdaderos."""

    lista = list(valores)
    for indice, valor in enumerate(lista):
        _asegurar_booleano(valor, f"valor_{indice}")
    return all(lista)


def alguna(valores: Iterable[bool]) -> bool:
    """Devuelve ``True`` si algún elemento de *valores* es verdadero."""

    lista = list(valores)
    for indice, valor in enumerate(lista):
        _asegurar_booleano(valor, f"valor_{indice}")
    return any(lista)


def ninguna(valores: Iterable[bool]) -> bool:
    """Devuelve ``True`` cuando todos los elementos son ``False``."""

    lista = list(valores)
    for indice, valor in enumerate(lista):
        _asegurar_booleano(valor, f"valor_{indice}")
    return not any(lista)


def solo_uno(*valores: bool) -> bool:
    """Devuelve ``True`` si exactamente uno de los argumentos es verdadero."""

    if not valores:
        raise ValueError("Se necesita al menos un valor booleano para solo_uno")

    verdaderos = 0
    for indice, valor in enumerate(valores):
        if _asegurar_booleano(valor, f"valor_{indice}"):
            verdaderos += 1
            if verdaderos > 1:
                return False
    return verdaderos == 1


def conteo_verdaderos(valores: Iterable[bool]) -> int:
    """Cuenta la cantidad de elementos verdaderos en *valores*."""

    contador = 0
    for indice, valor in enumerate(valores):
        if _asegurar_booleano(valor, f"valor_{indice}"):
            contador += 1
    return contador


def paridad(valores: Iterable[bool]) -> bool:
    """Retorna ``True`` si el número de verdaderos en *valores* es par."""

    return conteo_verdaderos(valores) % 2 == 0


__all__ = [
    "conjuncion",
    "disyuncion",
    "negacion",
    "xor",
    "nand",
    "nor",
    "implica",
    "equivale",
    "xor_multiple",
    "todas",
    "alguna",
    "ninguna",
    "solo_uno",
    "conteo_verdaderos",
    "paridad",
]
