"""Utilidades de serialización JSON y CSV para las corelibs de Cobra."""

from __future__ import annotations

import csv
import json
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


def codificar_json(objeto: Any, *, ordenar: bool = False, indentar: int | None = None) -> str:
    """Convierte ``objeto`` a texto JSON UTF-8 amigable.

    ``ordenar`` controla el orden alfabético de claves y ``indentar`` permite
    producir una salida legible cuando se proporciona un entero.
    """

    return json.dumps(objeto, ensure_ascii=False, sort_keys=ordenar, indent=indentar)


def decodificar_json(texto: str) -> Any:
    """Convierte un texto JSON en su valor Python equivalente."""

    return json.loads(texto)


def leer_json(ruta: str | Path) -> Any:
    """Lee y decodifica un archivo JSON desde ``ruta``."""

    return decodificar_json(Path(ruta).read_text(encoding="utf-8"))


def escribir_json(ruta: str | Path, objeto: Any, *, indentar: int | None = 2) -> None:
    """Codifica ``objeto`` como JSON y lo escribe en ``ruta``."""

    Path(ruta).write_text(
        codificar_json(objeto, indentar=indentar) + "\n",
        encoding="utf-8",
    )


def leer_csv(ruta: str | Path, *, delimitador: str = ",") -> list[dict[str, str]]:
    """Lee un CSV básico y devuelve una lista de diccionarios.

    La primera fila del archivo se interpreta como cabecera. Se rechazan
    archivos sin cabecera, cabeceras vacías y filas con columnas sobrantes o
    faltantes para ofrecer errores claros ante datos no homogéneos.
    """

    with Path(ruta).open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
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
    ruta: str | Path,
    filas: Iterable[Mapping[str, Any]],
    *,
    delimitador: str = ",",
) -> None:
    """Escribe ``filas`` como CSV usando una lista de diccionarios homogénea.

    Todas las filas deben tener las mismas claves que la primera fila. Se
    rechazan colecciones vacías, filas vacías y filas no homogéneas.
    """

    filas_normalizadas = _normalizar_filas_csv(filas)
    campos = list(filas_normalizadas[0].keys())

    with Path(ruta).open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos, delimiter=delimitador)
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
