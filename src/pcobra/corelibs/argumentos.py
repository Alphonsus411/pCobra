"""Utilidades simples para consultar argumentos de línea de comandos.

El módulo no captura ``sys.argv`` al importarse. Las funciones leen los
argumentos reales únicamente cuando se invocan con ``argv=None``.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Any

__all__ = [
    "obtener_argumentos",
    "contiene_flag",
    "obtener_opcion",
    "parsear_pares",
]


def obtener_argumentos(argv: Sequence[object] | None = None) -> list[str]:
    """Devuelve una copia normalizada de los argumentos de usuario.

    Cuando ``argv`` es ``None`` se usa ``sys.argv[1:]`` en el momento de la
    llamada. Si se entrega una secuencia explícita, se copia completa sin
    eliminar el primer elemento para facilitar pruebas y usos embebidos.
    """

    if argv is None:
        return list(sys.argv[1:])
    if isinstance(argv, (str, bytes, bytearray)):
        raise TypeError("argv debe ser una secuencia de argumentos, no texto plano")
    return [str(argumento) for argumento in argv]


def _normalizar_nombre(nombre: str) -> str:
    nombre = str(nombre).strip()
    if not nombre:
        raise ValueError("el nombre de la opción no puede estar vacío")

    if nombre.startswith("--"):
        nombre = nombre[2:]
    elif nombre.startswith("-"):
        nombre = nombre[1:]

    if not nombre:
        raise ValueError("el nombre de la opción no puede estar vacío")
    return nombre


def _tokens_opcion(nombre: str) -> tuple[str, str | None]:
    nombre = _normalizar_nombre(nombre)
    largo = f"--{nombre}"
    corto = f"-{nombre}" if len(nombre) == 1 else None
    return largo, corto


def _es_opcion(argumento: str) -> bool:
    if not argumento.startswith("-") or argumento == "-":
        return False
    try:
        float(argumento)
    except ValueError:
        return True
    return False


def contiene_flag(nombre: str, argv: Sequence[object] | None = None) -> bool:
    """Indica si ``argv`` contiene un flag largo o corto simple.

    Reconoce ``--flag`` y, para nombres de un solo carácter, ``-v``. Las formas
    con valor (``--clave=valor`` o ``--clave valor``) no cuentan como flag.
    """

    largo, corto = _tokens_opcion(nombre)
    for argumento in obtener_argumentos(argv):
        if argumento == largo or (corto is not None and argumento == corto):
            return True
    return False


def obtener_opcion(
    nombre: str,
    argv: Sequence[object] | None = None,
    por_defecto: Any = None,
) -> str | Any:
    """Obtiene el valor asociado a una opción o ``por_defecto`` si no existe.

    Soporta ``--clave=valor``, ``--clave valor`` y opciones cortas simples como
    ``-v valor`` cuando ``nombre`` tiene un solo carácter.
    """

    largo, corto = _tokens_opcion(nombre)
    argumentos = obtener_argumentos(argv)

    for indice, argumento in enumerate(argumentos):
        if argumento.startswith(f"{largo}="):
            return argumento.split("=", 1)[1]
        if corto is not None and argumento.startswith(f"{corto}="):
            return argumento.split("=", 1)[1]
        if argumento == largo or (corto is not None and argumento == corto):
            siguiente = indice + 1
            if siguiente < len(argumentos) and not _es_opcion(argumentos[siguiente]):
                return argumentos[siguiente]
            return por_defecto

    return por_defecto


def parsear_pares(argv: Sequence[object] | None = None) -> dict[str, str | bool]:
    """Parsea argumentos básicos en un diccionario de opciones.

    ``--flag`` y flags cortos como ``-v`` se guardan con valor ``True``.
    ``--clave valor``, ``--clave=valor`` y ``-v valor`` guardan el valor como
    texto. Los argumentos posicionales se ignoran.
    """

    argumentos = obtener_argumentos(argv)
    pares: dict[str, str | bool] = {}
    indice = 0

    while indice < len(argumentos):
        argumento = argumentos[indice]

        if argumento.startswith("--") and len(argumento) > 2:
            nombre_valor = argumento[2:]
            if "=" in nombre_valor:
                nombre, valor = nombre_valor.split("=", 1)
                if not nombre:
                    raise ValueError("el nombre de la opción no puede estar vacío")
                pares[nombre] = valor
            else:
                nombre = _normalizar_nombre(nombre_valor)
                siguiente = indice + 1
                if siguiente < len(argumentos) and not _es_opcion(argumentos[siguiente]):
                    pares[nombre] = argumentos[siguiente]
                    indice += 1
                else:
                    pares[nombre] = True
        elif _es_opcion(argumento) and len(argumento) == 2:
            nombre = _normalizar_nombre(argumento)
            siguiente = indice + 1
            if siguiente < len(argumentos) and not _es_opcion(argumentos[siguiente]):
                pares[nombre] = argumentos[siguiente]
                indice += 1
            else:
                pares[nombre] = True
        elif _es_opcion(argumento) and len(argumento) > 2 and "=" in argumento:
            nombre, valor = argumento[1:].split("=", 1)
            if len(nombre) == 1:
                pares[_normalizar_nombre(nombre)] = valor

        indice += 1

    return pares
