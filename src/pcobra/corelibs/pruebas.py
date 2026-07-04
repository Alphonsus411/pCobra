"""Utilidades mínimas de aserción para pruebas en Cobra.

Convención de retorno:
- Las aserciones exitosas devuelven ``True``.
- ``lanza_error`` devuelve la instancia de error capturada cuando la función
  lanza el tipo esperado, para permitir inspeccionar su mensaje o atributos.

Todas las comprobaciones fallidas lanzan ``AssertionError`` con mensajes
explícitos y deterministas. Este módulo no depende de frameworks externos.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

TError = TypeVar("TError", bound=BaseException)

__all__ = [
    "igual",
    "verdadero",
    "falso",
    "contiene",
    "lanza_error",
]


def _mensaje_personalizado(mensaje: str | None, predeterminado: str) -> str:
    """Devuelve ``mensaje`` si existe; en caso contrario, ``predeterminado``."""

    return predeterminado if mensaje is None else str(mensaje)


def igual(obtenido: Any, esperado: Any, mensaje: str | None = None) -> bool:
    """Afirma que ``obtenido`` y ``esperado`` son iguales.

    Returns:
        ``True`` cuando la aserción se cumple.

    Raises:
        AssertionError: si los valores son distintos.
    """

    if obtenido == esperado:
        return True

    predeterminado = f"Se esperaba {esperado!r}, pero se obtuvo {obtenido!r}"
    raise AssertionError(_mensaje_personalizado(mensaje, predeterminado))


def verdadero(valor: Any, mensaje: str | None = None) -> bool:
    """Afirma que ``valor`` es verdadero según la semántica booleana de Python.

    Returns:
        ``True`` cuando la aserción se cumple.

    Raises:
        AssertionError: si ``bool(valor)`` es ``False``.
    """

    if bool(valor):
        return True

    predeterminado = f"Se esperaba un valor verdadero, pero se obtuvo {valor!r}"
    raise AssertionError(_mensaje_personalizado(mensaje, predeterminado))


def falso(valor: Any, mensaje: str | None = None) -> bool:
    """Afirma que ``valor`` es falso según la semántica booleana de Python.

    Returns:
        ``True`` cuando la aserción se cumple.

    Raises:
        AssertionError: si ``bool(valor)`` es ``True``.
    """

    if not bool(valor):
        return True

    predeterminado = f"Se esperaba un valor falso, pero se obtuvo {valor!r}"
    raise AssertionError(_mensaje_personalizado(mensaje, predeterminado))


def contiene(contenedor: Any, elemento: Any, mensaje: str | None = None) -> bool:
    """Afirma que ``elemento`` pertenece a ``contenedor``.

    Returns:
        ``True`` cuando la aserción se cumple.

    Raises:
        AssertionError: si ``elemento`` no está en ``contenedor`` o si el
        contenedor no soporta la operación de pertenencia.
    """

    try:
        encontrado = elemento in contenedor
    except TypeError as exc:
        predeterminado = (
            f"No se pudo comprobar pertenencia de {elemento!r} "
            f"en {contenedor!r}: {exc}"
        )
        raise AssertionError(_mensaje_personalizado(mensaje, predeterminado)) from exc

    if encontrado:
        return True

    predeterminado = f"Se esperaba que {elemento!r} estuviera en {contenedor!r}"
    raise AssertionError(_mensaje_personalizado(mensaje, predeterminado))


def lanza_error(
    funcion: Callable[..., Any],
    tipo_error: type[TError] | tuple[type[BaseException], ...] = Exception,
    *args: Any,
    **kwargs: Any,
) -> TError | BaseException:
    """Afirma que ``funcion(*args, **kwargs)`` lanza ``tipo_error``.

    Returns:
        La instancia de error capturada cuando coincide con ``tipo_error``.

    Raises:
        TypeError: si ``funcion`` no es invocable o ``tipo_error`` no es una
        clase/tupla de clases de excepción válida para ``except``.
        AssertionError: si no se lanza ningún error o si se lanza otro tipo.
    """

    if not callable(funcion):
        raise TypeError("funcion debe ser callable")
    _validar_tipo_error(tipo_error)

    try:
        funcion(*args, **kwargs)
    except tipo_error as exc:
        return exc
    except Exception as exc:
        nombre_esperado = _nombre_tipo_error(tipo_error)
        predeterminado = (
            f"Se esperaba error {nombre_esperado}, "
            f"pero se lanzó {type(exc).__name__}: {exc}"
        )
        raise AssertionError(predeterminado) from exc

    nombre_esperado = _nombre_tipo_error(tipo_error)
    raise AssertionError(f"Se esperaba error {nombre_esperado}, pero no se lanzó ninguno")


def _validar_tipo_error(
    tipo_error: type[BaseException] | tuple[type[BaseException], ...],
) -> None:
    """Valida que ``tipo_error`` sea compatible con una cláusula ``except``."""

    tipos = tipo_error if isinstance(tipo_error, tuple) else (tipo_error,)
    if not tipos:
        raise TypeError("tipo_error debe incluir al menos una clase de excepción")
    if not all(isinstance(tipo, type) and issubclass(tipo, BaseException) for tipo in tipos):
        raise TypeError("tipo_error debe ser una clase de excepción o una tupla de ellas")


def _nombre_tipo_error(tipo_error: type[BaseException] | tuple[type[BaseException], ...]) -> str:
    """Representa de forma estable un tipo o tupla de tipos de excepción."""

    if isinstance(tipo_error, tuple):
        return "(" + ", ".join(tipo.__name__ for tipo in tipo_error) + ")"
    return tipo_error.__name__
