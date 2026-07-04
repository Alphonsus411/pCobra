"""Utilidades de serialización JSON y CSV para las corelibs de Cobra."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

__all__ = [
    "codificar_json",
    "decodificar_json",
    "leer_json",
    "escribir_json",
    "leer_csv",
    "escribir_csv",
]

PathLike = str | os.PathLike[str]


def _validar_ruta(ruta: PathLike, nombre_argumento: str = "ruta") -> Path:
    if not isinstance(ruta, (str, os.PathLike)):
        raise TypeError(
            f"{nombre_argumento} debe ser una ruta de texto o compatible con os.PathLike"
        )
    texto = os.fspath(ruta)
    if not isinstance(texto, str):
        raise TypeError(f"{nombre_argumento} debe representar una ruta de texto")
    if texto == "":
        raise ValueError(f"{nombre_argumento} no puede estar vacía")
    return Path(texto)


def _validar_delimitador(delimitador: str) -> str:
    if not isinstance(delimitador, str):
        raise TypeError("delimitador debe ser texto")
    if len(delimitador) != 1:
        raise ValueError("delimitador debe contener exactamente un carácter")
    return delimitador


def codificar_json(
    objeto: Any, *, ordenar: bool = False, indentar: int | None = None
) -> str:
    """Convierte ``objeto`` a texto JSON UTF-8 amigable.

    ``ordenar`` controla el orden alfabético de claves y ``indentar`` permite
    producir una salida legible cuando se proporciona un entero.
    """

    try:
        return json.dumps(
            objeto, ensure_ascii=False, sort_keys=ordenar, indent=indentar
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"No se pudo codificar JSON: {exc}") from exc


def decodificar_json(texto: str) -> Any:
    """Convierte un texto JSON en su valor Python equivalente."""

    if not isinstance(texto, str):
        raise TypeError("texto debe ser una cadena JSON")
    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON inválido en línea {exc.lineno}, columna {exc.colno}: {exc.msg}"
        ) from None


def leer_json(ruta: PathLike) -> Any:
    """Lee y decodifica un archivo JSON desde ``ruta``."""

    return decodificar_json(_validar_ruta(ruta).read_text(encoding="utf-8"))


def escribir_json(ruta: PathLike, objeto: Any, *, indentar: int | None = 2) -> None:
    """Codifica ``objeto`` como JSON y lo escribe en ``ruta``."""

    _validar_ruta(ruta).write_text(
        codificar_json(objeto, indentar=indentar) + "\n",
        encoding="utf-8",
    )


def leer_csv(ruta: PathLike, *, delimitador: str = ",") -> list[dict[str, str]]:
    """Lee un CSV básico y devuelve una lista de diccionarios.

    La primera fila del archivo se interpreta como cabecera. Se rechazan
    archivos sin cabecera, cabeceras vacías y filas con columnas sobrantes o
    faltantes para ofrecer errores claros ante datos no homogéneos.
    """

    delimitador_validado = _validar_delimitador(delimitador)
    with _validar_ruta(ruta).open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador_validado)
        if lector.fieldnames is None:
            raise ValueError("El CSV debe incluir una fila de cabecera")

        campos = list(lector.fieldnames)
        _validar_cabecera_csv(campos)

        filas: list[dict[str, str]] = []
        for numero_fila, fila in enumerate(lector, start=2):
            if None in fila:
                raise ValueError(
                    f"La fila {numero_fila} tiene columnas sobrantes; "
                    "todas las filas deben compartir la misma cabecera"
                )

            faltantes = [campo for campo, valor in fila.items() if valor is None]
            if faltantes:
                campos_faltantes = ", ".join(faltantes)
                raise ValueError(
                    f"La fila {numero_fila} no contiene valores para: {campos_faltantes}"
                )

            filas.append(dict(fila))

    return filas


def escribir_csv(
    ruta: PathLike,
    filas: Iterable[Mapping[str, Any]],
    *,
    delimitador: str = ",",
) -> None:
    """Escribe ``filas`` como CSV usando una lista de diccionarios homogénea.

    Todas las filas deben tener las mismas claves que la primera fila. Se
    rechazan colecciones vacías, filas vacías y filas no homogéneas.
    """

    delimitador_validado = _validar_delimitador(delimitador)
    filas_normalizadas = _normalizar_filas_csv(filas)
    campos = list(filas_normalizadas[0].keys())

    with _validar_ruta(ruta).open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=campos, delimiter=delimitador_validado
        )
        escritor.writeheader()
        escritor.writerows(filas_normalizadas)


def _validar_cabecera_csv(campos: list[str]) -> None:
    if not campos or all(campo == "" for campo in campos):
        raise ValueError("El CSV debe incluir una cabecera no vacía")

    vacios = [indice + 1 for indice, campo in enumerate(campos) if campo == ""]
    if vacios:
        posiciones = ", ".join(str(posicion) for posicion in vacios)
        raise ValueError(f"La cabecera CSV contiene columnas sin nombre: {posiciones}")

    if len(set(campos)) != len(campos):
        raise ValueError("La cabecera CSV contiene nombres de columna duplicados")


def _normalizar_filas_csv(filas: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    filas_normalizadas = list(filas)
    if not filas_normalizadas:
        raise ValueError("No se puede escribir CSV sin filas")

    primera = filas_normalizadas[0]
    if not isinstance(primera, Mapping):
        raise TypeError("Cada fila CSV debe ser un diccionario")
    if not primera:
        raise ValueError("Las filas CSV no pueden estar vacías")

    campos = tuple(primera.keys())
    resultado: list[dict[str, Any]] = []
    for numero_fila, fila in enumerate(filas_normalizadas, start=1):
        if not isinstance(fila, Mapping):
            raise TypeError(f"La fila {numero_fila} debe ser un diccionario")
        if not fila:
            raise ValueError(f"La fila {numero_fila} está vacía")
        if tuple(fila.keys()) != campos:
            esperadas = ", ".join(str(campo) for campo in campos)
            recibidas = ", ".join(str(campo) for campo in fila.keys())
            raise ValueError(
                f"La fila {numero_fila} no es homogénea; "
                f"claves esperadas: {esperadas}; claves recibidas: {recibidas}"
            )
        resultado.append(dict(fila))

    return resultado
