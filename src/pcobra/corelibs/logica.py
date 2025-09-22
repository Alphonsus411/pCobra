"""Operaciones lógicas básicas con validación de tipos."""

from __future__ import annotations

import inspect
from itertools import product
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


def mayoria(valores: Iterable[bool]) -> bool:
    """Evalúa si existe mayoría de valores verdaderos.

    Args:
        valores: Iterable con los valores a considerar.

    Returns:
        ``True`` cuando la cantidad de verdaderos supera a la de falsos.

    Raises:
        ValueError: si no se proporcionan valores.
        TypeError: si alguno de los elementos no es booleano.
    """

    lista = list(valores)
    if not lista:
        raise ValueError("Se necesita al menos un valor booleano para mayoria")

    verdaderos = conteo_verdaderos(lista)
    return verdaderos > len(lista) / 2


def exactamente_n(valores: Iterable[bool], cantidad: int) -> bool:
    """Comprueba si existen exactamente ``cantidad`` valores verdaderos."""

    if isinstance(cantidad, bool) or not isinstance(cantidad, int):
        raise TypeError(
            f"cantidad debe ser un entero, se recibió {type(cantidad).__name__}"
        )
    if cantidad < 0:
        raise ValueError("cantidad no puede ser negativa en exactamente_n")

    lista = list(valores)
    verdaderos = conteo_verdaderos(lista)
    return verdaderos == cantidad


def _generar_nombres(aridad: int, nombres: Iterable[str] | None) -> list[str]:
    if nombres is None:
        return [f"p{indice + 1}" for indice in range(aridad)]

    nombres_lista = list(nombres)
    if len(nombres_lista) != aridad:
        raise ValueError(
            "La cantidad de nombres debe coincidir con la aridad especificada"
        )
    return nombres_lista


def _resolver_aridad(funcion: Callable[..., bool], aridad: int | None) -> int:
    if aridad is not None:
        if aridad < 0:
            raise ValueError("La aridad no puede ser negativa en tabla_verdad")
        return aridad

    try:
        firma = inspect.signature(funcion)
    except (TypeError, ValueError) as error:
        raise ValueError("No se pudo inferir la aridad de la función proporcionada") from error

    for parametro in firma.parameters.values():
        if parametro.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            raise ValueError("tabla_verdad requiere una función con aridad fija")
        if parametro.kind is inspect.Parameter.KEYWORD_ONLY:
            raise ValueError(
                "tabla_verdad solo admite parámetros posicionales; proporciona la aridad manualmente"
            )

    return sum(
        parametro.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        for parametro in firma.parameters.values()
    )


def tabla_verdad(
    funcion: Callable[..., bool],
    *,
    aridad: int | None = None,
    nombres: Iterable[str] | None = None,
    nombre_resultado: str = "resultado",
) -> list[dict[str, bool]]:
    """Genera la tabla de verdad completa de ``funcion``.

    Args:
        funcion: Callable booleano del que se calculará la tabla.
        aridad: Número de argumentos posicionales de la función. Si se omite, se
            intenta inferir mediante introspección.
        nombres: Nombres opcionales para las columnas de entrada. Si se
            proporciona, su longitud debe coincidir con ``aridad``.
        nombre_resultado: Etiqueta para la columna de salida.

    Returns:
        Lista de diccionarios que representan cada combinación de entrada y su
        resultado asociado.

    Raises:
        TypeError: si ``funcion`` no es callable o si ``nombre_resultado`` no es
            una cadena.
        ValueError: cuando la aridad es negativa, cuando no puede inferirse o si
            los nombres no coinciden con la aridad.
    """

    if not callable(funcion):
        raise TypeError("funcion debe ser callable en tabla_verdad")
    if not isinstance(nombre_resultado, str):
        raise TypeError("nombre_resultado debe ser una cadena de texto")

    aridad_resuelta = _resolver_aridad(funcion, aridad)
    nombres_columnas = _generar_nombres(aridad_resuelta, nombres)

    tabla = []
    for combinacion in product((False, True), repeat=aridad_resuelta):
        resultado = funcion(*combinacion)
        fila = dict(zip(nombres_columnas, combinacion))
        fila[nombre_resultado] = _asegurar_booleano(resultado, "resultado")
        tabla.append(fila)

    return tabla


def diferencia_simetrica(*colecciones: Iterable[bool]) -> tuple[bool, ...]:
    """Calcula la diferencia simétrica elemento a elemento sobre colecciones."""

    if not colecciones:
        raise ValueError(
            "Se necesita al menos una colección booleana para diferencia_simetrica"
        )

    listas: list[list[bool]] = []
    longitud_esperada: int | None = None
    for indice_coleccion, coleccion in enumerate(colecciones):
        lista = [
            _asegurar_booleano(valor, f"valor_{indice_coleccion}_{indice}")
            for indice, valor in enumerate(coleccion)
        ]
        if longitud_esperada is None:
            longitud_esperada = len(lista)
        elif len(lista) != longitud_esperada:
            raise ValueError(
                "Todas las colecciones deben tener la misma longitud en diferencia_simetrica"
            )
        listas.append(lista)

    if longitud_esperada is None:
        return ()

    resultado: list[bool] = []
    for indice in range(longitud_esperada):
        valores = [lista[indice] for lista in listas]
        if len(valores) == 1:
            resultado.append(valores[0])
        else:
            resultado.append(xor_multiple(*valores))

    return tuple(resultado)


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
    "mayoria",
    "exactamente_n",
    "tabla_verdad",
    "diferencia_simetrica",
]
