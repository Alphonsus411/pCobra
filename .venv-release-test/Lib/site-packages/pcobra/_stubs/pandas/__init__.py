"""Implementación mínima de ``pandas`` para las pruebas de la biblioteca."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

__all__ = ["DataFrame", "Timestamp"]


@dataclass
class DataFrame:
    """Contenedor tabular ligero con la API necesaria en las pruebas."""

    _records: list[dict[str, Any]]
    _columns: list[str]

    def __init__(
        self,
        datos: Iterable[Any] | Mapping[str, Sequence[Any]] | None = None,
        columns: Sequence[str] | None = None,
    ) -> None:
        registros: list[dict[str, Any]]
        columnas: list[str]
        if datos is None:
            registros = []
            columnas = list(columns or [])
        elif isinstance(datos, Mapping):
            columnas = list(datos.keys())
            longitudes = {len(valores) for valores in datos.values()}
            if len(longitudes) > 1:
                raise ValueError("Todas las columnas deben tener la misma longitud")
            longitud = longitudes.pop() if columnas else 0
            registros = [
                {columna: list(datos[columna])[indice] for columna in columnas}
                for indice in range(longitud)
            ]
        else:
            filas = list(datos)
            if filas and isinstance(filas[0], Mapping):
                registros = [dict(fila) for fila in filas]  # type: ignore[arg-type]
                columnas = list(registros[0].keys()) if registros else list(columns or [])
            else:
                filas_secuencias = [list(fila) for fila in filas]
                columnas = (
                    list(columns)
                    if columns is not None
                    else [f"col_{indice}" for indice in range(len(filas_secuencias[0]) if filas_secuencias else 0)]
                )
                registros = [
                    {columna: fila[indice] if indice < len(fila) else None for indice, columna in enumerate(columnas)}
                    for fila in filas_secuencias
                ]
        self._records = registros
        self._columns = columnas

    def to_dict(self, orient: str = "records") -> list[dict[str, Any]]:
        if orient != "records":
            raise ValueError("Solo se admite orient='records' en el stub")
        return [dict(fila) for fila in self._records]

    def copy(self) -> "DataFrame":
        return DataFrame([dict(fila) for fila in self._records], columns=self._columns)

    @property
    def columns(self) -> list[str]:  # pragma: no cover - compatibilidad
        return list(self._columns)

    def to_excel(
        self,
        ruta: str | Path,
        *,
        header: bool = True,
        index: bool = False,
        engine: str | None = None,
    ) -> None:
        from openpyxl import Workbook  # type: ignore[import-not-found]

        libro = Workbook()
        hoja = libro.active
        if header:
            hoja.append(self._columns)
        for indice, fila in enumerate(self._records):
            fila_valores = [fila.get(columna) for columna in self._columns]
            if index:
                hoja.append([indice] + fila_valores)
            else:
                hoja.append(fila_valores)
        libro.save(Path(ruta))


def Timestamp(valor: str | datetime) -> datetime:
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor)
    texto = str(valor)
    try:
        return datetime.fromisoformat(texto)
    except ValueError:  # pragma: no cover - rutas poco comunes
        raise ValueError(f"Formato de fecha no reconocido: {valor!r}")
