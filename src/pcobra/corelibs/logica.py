"""Operaciones lógicas básicas con validación de tipos."""

from __future__ import annotations

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def _evaluar_resultado(resultado: T | Callable[[], T]) -> T:
    """Evalúa *resultado* si es un callable, de lo contrario lo retorna tal cual."""

    if callable(resultado):
        return resultado()
    return resultado


def _evaluar_condicion(condicion: bool | Callable[[], bool], nombre: str) -> bool:
    """Evalúa *condicion* perezosamente y la valida como booleana."""

    valor = condicion() if callable(condicion) else condicion
    return _asegurar_booleano(valor, nombre)


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


def es_verdadero(valor: bool) -> bool:
    """Valida que *valor* sea booleano y retorna ``bool(valor)``."""

    return bool(_asegurar_booleano(valor))


def es_falso(valor: bool) -> bool:
    """Valida que *valor* sea booleano y retorna ``bool(not valor)``."""

    return bool(not _asegurar_booleano(valor))


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


def entonces(valor: bool, resultado: T | Callable[[], T]) -> T | None:
    """Devuelve *resultado* cuando ``valor`` es verdadero.

    Si *resultado* es un callable, se evalúa perezosamente solo cuando ``valor``
    es ``True``. En caso contrario, retorna ``None``.
    """

    if _asegurar_booleano(valor):
        return _evaluar_resultado(resultado)
    return None


def si_no(valor: bool, resultado: T | Callable[[], T]) -> T | None:
    """Devuelve *resultado* únicamente cuando ``valor`` es falso.

    Si *resultado* es un callable, se evalúa perezosamente solo cuando ``valor``
    es ``False``. En caso contrario, retorna ``None``.
    """

    if not _asegurar_booleano(valor):
        return _evaluar_resultado(resultado)
    return None


def condicional(
    *casos: tuple[bool | Callable[[], bool], T | Callable[[], T]],
    por_defecto: T | Callable[[], T] | None = None,
) -> T | None:
    """Evalúa pares ``(condición, resultado)`` en orden determinista.

    Cada ``caso`` debe ser un iterable de dos elementos donde el primero es una
    condición booleana (o un callable sin argumentos que la produzca) y el
    segundo el resultado asociado (o un callable que lo compute). Se evalúa el
    primer caso verdadero y se retorna su resultado, respetando evaluación
    perezosa tanto de condiciones como de resultados.

    Args:
        *casos: pares ``(condición, resultado)`` a verificar en orden.
        por_defecto: valor o callable a usar cuando ningún caso es verdadero.

    Returns:
        El resultado del primer caso verdadero o ``por_defecto`` si se
        proporciona, en caso contrario ``None``.

    Raises:
        ValueError: si algún caso no contiene exactamente dos elementos.
        TypeError: si las condiciones no son booleanas ni callables que
            produzcan booleanos.
    """

    for indice, caso in enumerate(casos):
        try:
            condicion, resultado = caso
        except (TypeError, ValueError):
            raise ValueError(
                "Cada caso debe ser una tupla de dos elementos (condición, resultado)"
            ) from None

        if _evaluar_condicion(condicion, f"condicion_{indice}"):
            return _evaluar_resultado(resultado)

    if por_defecto is not None:
        return _evaluar_resultado(por_defecto)
    return None


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
    "es_verdadero",
    "es_falso",
    "conjuncion",
    "disyuncion",
    "negacion",
    "xor",
    "nand",
    "nor",
    "implica",
    "equivale",
    "xor_multiple",
    "entonces",
    "si_no",
    "condicional",
    "todas",
    "alguna",
    "ninguna",
    "solo_uno",
    "conteo_verdaderos",
    "paridad",
]
