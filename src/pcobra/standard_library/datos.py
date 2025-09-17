"""Funciones utilitarias para trabajar con datos tabulares.

Todas las funciones usan internamente :mod:`pandas` y :mod:`numpy`, pero
devuelven estructuras de datos sencillas (listas y diccionarios) que pueden ser
consumidas directamente desde Cobra sin depender de objetos complejos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence

import numpy as np
import pandas as pd

Registro = dict[str, Any]
Tabla = list[Registro]


def _a_dataframe(datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame) -> pd.DataFrame:
    """Convierte ``datos`` a un ``DataFrame`` de ``pandas``.

    Se aceptan ``DataFrame`` ya construidos, listas de registros (diccionarios
    por fila) o diccionarios de listas (columnas).
    """

    if isinstance(datos, pd.DataFrame):
        return datos.copy()
    if isinstance(datos, Mapping):
        return pd.DataFrame(datos)
    if isinstance(datos, Iterable):
        return pd.DataFrame(list(datos))
    raise TypeError("Formato de datos no soportado. Usa registros o columnas.")


def _sanear_valor(valor: Any) -> Any:
    """Reemplaza valores especiales de ``numpy`` por ``None`` y normaliza tipos."""

    if valor is None:
        return None
    if isinstance(valor, (float, np.floating)) and np.isnan(valor):
        return None
    if isinstance(valor, (np.floating, np.integer)):
        escalar = valor.item()
        if isinstance(escalar, float) and np.isnan(escalar):
            return None
        return escalar
    if isinstance(valor, pd.Timestamp):
        return valor.isoformat()
    if isinstance(valor, pd.Timedelta):
        return valor.isoformat() if hasattr(valor, "isoformat") else str(valor)
    if isinstance(valor, np.ndarray):  # pragma: no cover - casos raros
        return valor.tolist()
    return valor


def _sanear_registros(registros: list[MutableMapping[str, Any]]) -> Tabla:
    """Limpia los registros reemplazando valores no serializables."""

    resultado: Tabla = []
    for registro in registros:
        limpio: Registro = {clave: _sanear_valor(valor) for clave, valor in registro.items()}
        resultado.append(limpio)
    return resultado


def leer_csv(
    ruta: str | Path,
    *,
    separador: str = ",",
    encoding: str = "utf-8",
    limite_filas: int | None = None,
) -> Tabla:
    """Lee un archivo CSV y devuelve una tabla como lista de diccionarios.

    Parameters
    ----------
    ruta:
        Ruta al archivo CSV. Puede ser relativa o absoluta.
    separador:
        Separador de columnas utilizado en el archivo. Por defecto ``,``.
    encoding:
        Codificación del archivo. Por defecto ``utf-8``.
    limite_filas:
        Si se especifica, solo se leen las primeras ``limite_filas`` filas.
    """

    try:
        df = pd.read_csv(Path(ruta), sep=separador, encoding=encoding, nrows=limite_filas)
    except (FileNotFoundError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"No fue posible leer el CSV: {exc}") from exc
    return _sanear_registros(df.to_dict(orient="records"))


def leer_json(ruta: str | Path, *, orient: str | None = None, lineas: bool = False) -> Tabla:
    """Lee un archivo JSON con estructura tabular.

    Parameters
    ----------
    ruta:
        Ruta al archivo JSON.
    orient:
        Orientación utilizada por :func:`pandas.read_json`. Si es ``None`` se
        intenta inferir automáticamente.
    lineas:
        Indica si el archivo está en formato JSON Lines.
    """

    try:
        df = pd.read_json(Path(ruta), orient=orient, lines=lineas)
    except (ValueError, FileNotFoundError) as exc:
        raise ValueError(f"No fue posible leer el JSON: {exc}") from exc
    return _sanear_registros(df.to_dict(orient="records"))


def describir(datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame) -> Registro:
    """Genera estadísticas descriptivas para cada columna de ``datos``.

    El resultado es un diccionario donde cada columna contiene sus métricas
    básicas (conteo, media, desviación, percentiles, etc.).
    """

    df = _a_dataframe(datos)
    descripcion = df.describe(include="all").fillna(np.nan)
    return {columna: {indice: _sanear_valor(valor) for indice, valor in serie.items()} for columna, serie in descripcion.to_dict().items()}


def seleccionar_columnas(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columnas: Sequence[str],
) -> Tabla:
    """Devuelve una nueva tabla solo con ``columnas``.

    Lanza ``KeyError`` si alguna de las columnas no existe.
    """

    df = _a_dataframe(datos)
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas inexistentes: {', '.join(faltantes)}")
    return _sanear_registros(df.loc[:, list(columnas)].to_dict(orient="records"))


def filtrar(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    condicion: Callable[[Registro], bool],
) -> Tabla:
    """Aplica ``condicion`` fila por fila y devuelve solo las filas que cumplen.

    La función ``condicion`` recibe un diccionario por fila y debe devolver un
    booleano.
    """

    df = _a_dataframe(datos)

    def _evaluar(fila: pd.Series) -> bool:
        try:
            return bool(condicion(fila.to_dict()))
        except Exception as exc:  # pragma: no cover - defensivo
            raise ValueError(f"Error al evaluar la condición de filtrado: {exc}") from exc

    mascara = df.apply(_evaluar, axis=1)
    return _sanear_registros(df.loc[mascara].to_dict(orient="records"))


def agrupar_y_resumir(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    por: Sequence[str],
    agregaciones: Mapping[str, str | Sequence[str] | Callable[[pd.Series], Any]],
) -> Tabla:
    """Agrupa ``datos`` por las columnas ``por`` y aplica ``agregaciones``.

    Las agregaciones admiten cadenas reconocidas por :meth:`DataFrame.agg`,
    listas de cadenas o funciones personalizadas.
    """

    df = _a_dataframe(datos)
    faltantes = [col for col in por if col not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas inexistentes para agrupar: {', '.join(faltantes)}")
    agrupado = df.groupby(list(por), dropna=False).agg(agregaciones).reset_index()
    # Aplanar columnas con múltiples niveles
    if isinstance(agrupado.columns, pd.MultiIndex):
        columnas = [
            "_".join([str(nivel) for nivel in columna if str(nivel) != ""]).strip("_")
            for columna in agrupado.columns.values
        ]
        agrupado.columns = columnas
    else:
        renombres: dict[str, str] = {}
        for columna, operacion in agregaciones.items():
            if columna in por or columna not in agrupado.columns:
                continue
            if isinstance(operacion, str):
                sufijo = operacion
            elif callable(operacion):
                sufijo = getattr(operacion, "__name__", "func")
                sufijo = sufijo.replace("<", "").replace(">", "") or "func"
            else:
                sufijo = "custom"
            renombres[columna] = f"{columna}_{sufijo}"
        if renombres:
            agrupado = agrupado.rename(columns=renombres)
    return _sanear_registros(agrupado.to_dict(orient="records"))


def a_listas(datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame) -> dict[str, list[Any]]:
    """Convierte ``datos`` a un diccionario ``columna -> lista``."""

    df = _a_dataframe(datos)
    columnas = df.to_dict(orient="list")
    return {col: [_sanear_valor(valor) for valor in valores] for col, valores in columnas.items()}


def de_listas(columnas: Mapping[str, Sequence[Any]]) -> Tabla:
    """Construye una tabla a partir de un diccionario de listas.

    Todas las listas deben tener la misma longitud.
    """

    try:
        df = pd.DataFrame(columnas)
    except ValueError as exc:
        raise ValueError(f"No fue posible construir la tabla: {exc}") from exc
    return _sanear_registros(df.to_dict(orient="records"))

