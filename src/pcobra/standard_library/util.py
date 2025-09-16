"""Pequeñas funciones de ayuda."""

from __future__ import annotations

import threading
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional, Union

_MISSING = object()


def es_nulo(valor) -> bool:
    """Indica si ``valor`` es ``None``."""
    return valor is None


def es_vacio(secuencia) -> bool:
    """Devuelve ``True`` si la secuencia no contiene elementos."""
    return len(secuencia) == 0


def repetir(cadena: str, veces: int) -> str:
    """Retorna ``cadena`` repetida ``veces`` veces."""
    return cadena * veces


@contextmanager
def rel(
    objetivo: Any,
    cambios: Union[Mapping[str, Any], Callable[[Any], Optional[Callable[[], None]]]],
    condicion: Optional[Callable[[Any], bool]] = None,
    duracion: Optional[float] = None,
) -> Iterator[Any]:
    """Aplica cambios temporales sobre ``objetivo`` y los revierte automáticamente.

    ``rel`` funciona como un *context manager* que permite modificar atributos de un
    objeto o función durante un bloque ``with``. Las modificaciones pueden indicarse
    mediante un diccionario (clave atributo, valor nuevo) o a través de una función
    que reciba el objetivo, efectúe los cambios deseados y devuelva opcionalmente otra
    función encargada de revertirlos.

    Args:
        objetivo: Función u objeto cuyos atributos serán modificados temporalmente.
        cambios: Diccionario con los nuevos valores o callable que aplica y opcionalmente
            devuelve una función de restauración.
        condicion: Callable opcional que recibe ``objetivo`` y devuelve ``True`` cuando
            se deben aplicar los cambios. Si es ``None`` se asume ``True``.
        duracion: Intervalo en segundos tras el cual los cambios se revertirán
            automáticamente, incluso si el bloque ``with`` sigue en ejecución.

    Yields:
        El ``objetivo`` recibido, para facilitar su manipulación dentro del bloque.

    Ejemplos:
        >>> class Demo:
        ...     valor = 1
        ...
        >>> demo = Demo()
        >>> with rel(demo, {"valor": 99}):
        ...     demo.valor
        99
        >>> demo.valor
        1

        >>> def parchear_doc(funcion):
        ...     original = funcion.__doc__
        ...     funcion.__doc__ = "doc temporal"
        ...     return lambda: setattr(funcion, "__doc__", original)
        ...
        >>> def hola():
        ...     '''Saluda.'''
        ...     return "hola"
        ...
        >>> with rel(hola, parchear_doc):
        ...     hola.__doc__
        'doc temporal'
        >>> hola.__doc__
        'Saluda.'

        >>> import time
        >>> demo = Demo()
        >>> with rel(demo, {"valor": 5}, duracion=0.01):
        ...     time.sleep(0.02)
        ...     demo.valor
        1

    """

    condicion_real: Callable[[Any], bool] = condicion or (lambda _: True)
    aplicar = condicion_real(objetivo)

    restaurado = False
    temporizador: Optional[threading.Timer] = None
    restaurar_callable: Optional[Callable[[], None]] = None
    valores_originales: Dict[str, Any] = {}

    def restaurar() -> None:
        nonlocal restaurado
        if restaurado:
            return
        restaurado = True

        if isinstance(cambios, Mapping):
            for atributo, valor_original in valores_originales.items():
                try:
                    if valor_original is _MISSING:
                        delattr(objetivo, atributo)
                    else:
                        setattr(objetivo, atributo, valor_original)
                except AttributeError:
                    # El atributo ya no existe; continuar sin interrumpir la restauración.
                    continue
        elif restaurar_callable is not None:
            restaurar_callable()

    try:
        if aplicar:
            if isinstance(cambios, Mapping):
                try:
                    for atributo, valor_nuevo in cambios.items():
                        valores_originales.setdefault(
                            atributo,
                            getattr(objetivo, atributo, _MISSING),
                        )
                        setattr(objetivo, atributo, valor_nuevo)
                except Exception:
                    restaurar()
                    raise
            elif callable(cambios):
                restaurar_callable = cambios(objetivo)
                if restaurar_callable is not None and not callable(restaurar_callable):
                    restaurar()
                    raise TypeError(
                        "El callable proporcionado en 'cambios' debe devolver una función "
                        "de restauración o None",
                    )
            else:
                raise TypeError("'cambios' debe ser un mapeo o un callable")

            if duracion is not None:
                temporizador = threading.Timer(duracion, restaurar)
                temporizador.daemon = True
                temporizador.start()

        yield objetivo
    finally:
        if temporizador is not None:
            temporizador.cancel()
        if aplicar:
            restaurar()

