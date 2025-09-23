"""Funciones utilitarias para trabajar con datos tabulares.

Todas las funciones usan internamente :mod:`pandas` y :mod:`numpy`, pero
devuelven estructuras de datos sencillas (listas y diccionarios) que pueden ser
consumidas directamente desde Cobra sin depender de objetos complejos.
"""

from __future__ import annotations

import importlib.util
import math
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence

import numpy as np
import pandas as pd

Registro = dict[str, Any]
Tabla = list[Registro]


__all__ = [
    "leer_csv",
    "leer_json",
    "escribir_csv",
    "escribir_json",
    "leer_excel",
    "escribir_excel",
    "leer_parquet",
    "escribir_parquet",
    "leer_feather",
    "escribir_feather",
    "describir",
    "correlacion_pearson",
    "correlacion_spearman",
    "matriz_covarianza",
    "calcular_percentiles",
    "resumen_rapido",
    "seleccionar_columnas",
    "filtrar",
    "mutar_columna",
    "separar_columna",
    "unir_columnas",
    "agrupar_y_resumir",
    "ordenar_tabla",
    "combinar_tablas",
    "rellenar_nulos",
    "pivotar_ancho",
    "pivotar_largo",
    "desplegar_tabla",
    "pivotar_tabla",
    "tabla_cruzada",
    "a_listas",
    "de_listas",
]


def _modulo_disponible(nombre: str) -> bool:
    """Devuelve ``True`` si el módulo indicado puede importarse."""

    return importlib.util.find_spec(nombre) is not None


def _seleccionar_motor_parquet(engine: str | None) -> str:
    """Resuelve el motor a utilizar para leer o escribir archivos Parquet."""

    if engine is not None:
        if not _modulo_disponible(engine):
            raise ValueError(
                "Para trabajar con archivos Parquet usando el motor "
                f"'{engine}' es necesario instalar el paquete correspondiente."
            )
        return engine

    for candidato in ("pyarrow", "fastparquet"):
        if _modulo_disponible(candidato):
            return candidato

    raise ValueError(
        "No se encontró un motor compatible para Parquet. Instala 'pyarrow' o 'fastparquet'."
    )


def _asegurar_pyarrow(accion: str) -> None:
    """Comprueba la disponibilidad de ``pyarrow`` y lanza un error descriptivo."""

    if not _modulo_disponible("pyarrow"):
        raise ValueError(f"No fue posible {accion}: instala el paquete opcional 'pyarrow'.")


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


def escribir_csv(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    ruta: str | Path,
    *,
    separador: str = ",",
    encoding: str = "utf-8",
    aniadir: bool = False,
    incluir_indice: bool = False,
) -> None:
    """Escribe ``datos`` en un archivo CSV usando :mod:`pandas`.

    Parameters
    ----------
    datos:
        Registros tabulares convertibles a :class:`pandas.DataFrame`.
    ruta:
        Ruta de destino del archivo CSV. Se crearán las carpetas intermedias si es necesario.
    separador:
        Separador de columnas que se utilizará al generar el CSV. Por defecto ``,``.
    encoding:
        Codificación del archivo de salida. Por defecto ``"utf-8"``.
    aniadir:
        Si es ``True`` se abre el archivo en modo *append* sin reescribir la cabecera existente.
    incluir_indice:
        Cuando es ``True`` se exporta el índice del :class:`~pandas.DataFrame` como primera columna.

    Raises
    ------
    ValueError
        Si no es posible escribir el archivo por un error del sistema o de ``pandas``.
    """

    df = _a_dataframe(datos)
    registros = _sanear_registros(df.to_dict(orient="records"))
    if registros:
        df_saneado = pd.DataFrame(registros)
    else:
        df_saneado = df.iloc[0:0]

    ruta_csv = Path(ruta)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    modo = "a" if aniadir else "w"
    encabezado = not (aniadir and ruta_csv.exists())

    try:
        df_saneado.to_csv(
            ruta_csv,
            sep=separador,
            encoding=encoding,
            index=incluir_indice,
            header=encabezado,
            mode=modo,
            lineterminator="\n",
        )
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError(f"No fue posible escribir el CSV: {exc}") from exc


def escribir_json(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    ruta: str | Path,
    *,
    encoding: str = "utf-8",
    aniadir: bool = False,
    lineas: bool = False,
    indent: int | None = None,
) -> None:
    """Serializa ``datos`` a JSON convencional o en formato JSON Lines.

    Parameters
    ----------
    datos:
        Colección de registros o columnas convertibles a :class:`pandas.DataFrame`.
    ruta:
        Ruta del archivo JSON de salida. Se crearán las carpetas necesarias.
    encoding:
        Codificación del archivo destino. Por defecto ``"utf-8"``.
    aniadir:
        Cuando es ``True`` se agrega el contenido al final del archivo existente.
    lineas:
        Escribe en formato JSON Lines cuando es ``True`` (un objeto por línea).
    indent:
        Número de espacios para sangrar el JSON cuando ``lineas`` es ``False``. Usa ``None`` para compactar.

    Raises
    ------
    ValueError
        Si no es posible escribir el archivo o si se intenta extender un JSON no basado en listas.
    """

    df = _a_dataframe(datos)
    registros = _sanear_registros(df.to_dict(orient="records"))
    ruta_json = Path(ruta)
    ruta_json.parent.mkdir(parents=True, exist_ok=True)

    if lineas:
        modo = "a" if aniadir else "w"
        try:
            with ruta_json.open(modo, encoding=encoding) as archivo:
                for registro in registros:
                    json.dump(registro, archivo, ensure_ascii=False)
                    archivo.write("\n")
        except OSError as exc:
            raise ValueError(f"No fue posible escribir el JSON: {exc}") from exc
        return

    contenido: list[Registro]
    if aniadir and ruta_json.exists():
        try:
            texto_existente = ruta_json.read_text(encoding=encoding).strip()
        except OSError as exc:
            raise ValueError(
                f"No fue posible leer el JSON existente para agregar registros: {exc}"
            ) from exc
        if texto_existente:
            try:
                existente = json.loads(texto_existente)
            except json.JSONDecodeError as exc:
                raise ValueError(f"No fue posible analizar el JSON existente: {exc}") from exc
            if not isinstance(existente, list):
                raise ValueError(
                    "Solo es posible agregar registros a un JSON que contiene una lista de objetos."
                )
            contenido = [*existente, *registros]
        else:
            contenido = registros
    else:
        contenido = registros

    try:
        with ruta_json.open("w", encoding=encoding) as archivo:
            json.dump(contenido, archivo, ensure_ascii=False, indent=indent)
            if indent is not None:
                archivo.write("\n")
    except OSError as exc:
        raise ValueError(f"No fue posible escribir el JSON: {exc}") from exc


def leer_excel(
    ruta: str | Path,
    *,
    hoja: str | int | None = 0,
    encabezado: int | Sequence[int] | None = 0,
    engine: str | None = None,
) -> Tabla:
    """Lee una hoja de cálculo de Excel y la devuelve como lista de registros.

    Parameters
    ----------
    ruta:
        Ruta al archivo Excel (``.xlsx``/``.xls``). Puede ser relativa o absoluta.
    hoja:
        Nombre o índice de la hoja que se desea cargar. Por defecto la primera hoja.
    encabezado:
        Fila(s) utilizada(s) como encabezado, igual que en :func:`pandas.read_excel`.
        Usa ``None`` para tratar la hoja como datos sin cabecera.
    engine:
        Motor de lectura a utilizar. ``pandas`` delega en librerías como
        ``openpyxl`` (``.xlsx``) o ``xlrd`` (``.xls``). Si no se indica se deja que
        :mod:`pandas` elija automáticamente.
    """

    ruta_excel = Path(ruta)
    try:
        dataframe = pd.read_excel(
            ruta_excel,
            sheet_name=hoja,
            header=encabezado,
            engine=engine,
        )
    except FileNotFoundError as exc:
        raise ValueError(f"No fue posible leer el Excel: {exc}") from exc
    except ImportError as exc:
        raise ValueError(
            "No fue posible leer el Excel: falta el motor requerido (por ejemplo 'openpyxl')."
        ) from exc
    except ValueError as exc:
        raise ValueError(f"No fue posible leer el Excel: {exc}") from exc

    if isinstance(dataframe, dict):
        raise ValueError(
            "Se recibió un libro con múltiples hojas. Especifica una sola hoja mediante el parámetro 'hoja'."
        )

    return _sanear_registros(dataframe.to_dict(orient="records"))


def escribir_excel(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    ruta: str | Path,
    *,
    hoja: str = "Hoja1",
    incluir_indice: bool = False,
    engine: str | None = None,
) -> None:
    """Escribe ``datos`` en un archivo Excel utilizando :mod:`pandas`.

    Parameters
    ----------
    datos:
        Registros tabulares convertibles a :class:`pandas.DataFrame`.
    ruta:
        Ruta de destino del libro Excel. Se crearán las carpetas intermedias si es necesario.
    hoja:
        Nombre de la hoja donde se volcarán los datos. Por defecto ``"Hoja1"``.
    incluir_indice:
        Si es ``True`` se incluye el índice del :class:`~pandas.DataFrame` como primera columna.
    engine:
        Motor de escritura (por ejemplo ``"openpyxl"`` o ``"xlsxwriter"``). Si es ``None``
        se deja que :mod:`pandas` seleccione uno compatible con la extensión del archivo.
    """

    df = _a_dataframe(datos)
    ruta_excel = Path(ruta)
    ruta_excel.parent.mkdir(parents=True, exist_ok=True)

    try:
        with pd.ExcelWriter(ruta_excel, engine=engine) as writer:
            df.to_excel(writer, sheet_name=hoja, index=incluir_indice)
    except ImportError as exc:
        raise ValueError(
            "No fue posible escribir el Excel: falta el motor requerido (por ejemplo 'openpyxl' o 'xlsxwriter')."
        ) from exc


def leer_parquet(
    ruta: str | Path,
    *,
    columnas: Sequence[str] | None = None,
    engine: str | None = None,
) -> Tabla:
    """Lee un archivo Parquet y devuelve una lista de registros."""

    ruta_parquet = Path(ruta)
    motor = _seleccionar_motor_parquet(engine)
    try:
        dataframe = pd.read_parquet(ruta_parquet, columns=columnas, engine=motor)
    except FileNotFoundError as exc:
        raise ValueError(f"No fue posible leer el Parquet: {exc}") from exc
    except (OSError, ValueError) as exc:
        raise ValueError(f"No fue posible leer el Parquet: {exc}") from exc

    return _sanear_registros(dataframe.to_dict(orient="records"))


def escribir_parquet(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    ruta: str | Path,
    *,
    engine: str | None = None,
    incluir_indice: bool = False,
    compresion: str | None = None,
) -> None:
    """Escribe ``datos`` en formato Parquet creando carpetas si es necesario."""

    df = _a_dataframe(datos)
    ruta_parquet = Path(ruta)
    ruta_parquet.parent.mkdir(parents=True, exist_ok=True)
    motor = _seleccionar_motor_parquet(engine)

    try:
        df.to_parquet(ruta_parquet, engine=motor, index=incluir_indice, compression=compresion)
    except (OSError, ValueError) as exc:
        raise ValueError(f"No fue posible escribir el Parquet: {exc}") from exc


def leer_feather(
    ruta: str | Path,
    *,
    columnas: Sequence[str] | None = None,
) -> Tabla:
    """Lee un archivo Feather y devuelve sus registros como diccionarios."""

    ruta_feather = Path(ruta)
    _asegurar_pyarrow("leer el archivo Feather")
    try:
        dataframe = pd.read_feather(ruta_feather, columns=columnas)
    except FileNotFoundError as exc:
        raise ValueError(f"No fue posible leer el Feather: {exc}") from exc
    except (OSError, ValueError) as exc:
        raise ValueError(f"No fue posible leer el Feather: {exc}") from exc

    return _sanear_registros(dataframe.to_dict(orient="records"))


def escribir_feather(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    ruta: str | Path,
    *,
    incluir_indice: bool = False,
    compresion: str | None = None,
) -> None:
    """Escribe ``datos`` en formato Feather usando ``pyarrow`` como backend."""

    df = _a_dataframe(datos)
    if incluir_indice:
        df = df.reset_index()

    ruta_feather = Path(ruta)
    ruta_feather.parent.mkdir(parents=True, exist_ok=True)
    _asegurar_pyarrow("escribir el archivo Feather")

    try:
        df.to_feather(ruta_feather, compression=compresion)
    except (OSError, ValueError) as exc:
        raise ValueError(f"No fue posible escribir el Feather: {exc}") from exc


def describir(datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame) -> Registro:
    """Genera estadísticas descriptivas para cada columna de ``datos``.

    El resultado es un diccionario donde cada columna contiene sus métricas
    básicas (conteo, media, desviación, percentiles, etc.).
    """

    df = _a_dataframe(datos)
    descripcion = df.describe(include="all").fillna(np.nan)
    return {
        columna: {indice: _sanear_valor(valor) for indice, valor in serie.items()}
        for columna, serie in descripcion.to_dict().items()
    }


def _calcular_correlacion(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    *,
    columnas: Sequence[str] | None = None,
    metodo: str,
) -> Registro:
    """Calcula una matriz de correlación usando ``pandas`` y la normaliza."""

    df = _a_dataframe(datos)
    if columnas is not None:
        faltantes = [col for col in columnas if col not in df.columns]
        if faltantes:
            raise KeyError(f"Columnas inexistentes para correlación: {', '.join(faltantes)}")
        df_num = df.loc[:, list(columnas)].apply(pd.to_numeric, errors="coerce")
    else:
        df_num = df.select_dtypes(include=[np.number])

    if df_num.empty:
        raise ValueError("No hay columnas numéricas para calcular correlaciones.")

    matriz = df_num.corr(method=metodo)
    return {
        columna: {indice: _sanear_valor(valor) for indice, valor in serie.items()}
        for columna, serie in matriz.to_dict().items()
    }


def correlacion_pearson(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columnas: Sequence[str] | None = None,
) -> Registro:
    """Devuelve la matriz de correlación de Pearson como diccionario anidado."""

    return _calcular_correlacion(datos, columnas=columnas, metodo="pearson")


def correlacion_spearman(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columnas: Sequence[str] | None = None,
) -> Registro:
    """Devuelve la matriz de correlación de Spearman como diccionario anidado."""

    return _calcular_correlacion(datos, columnas=columnas, metodo="spearman")


def matriz_covarianza(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columnas: Sequence[str] | None = None,
) -> Registro:
    """Calcula la matriz de covarianzas normalizada en diccionarios simples."""

    df = _a_dataframe(datos)
    if columnas is not None:
        faltantes = [col for col in columnas if col not in df.columns]
        if faltantes:
            raise KeyError(f"Columnas inexistentes para covarianzas: {', '.join(faltantes)}")
        df_num = df.loc[:, list(columnas)].apply(pd.to_numeric, errors="coerce")
    else:
        df_num = df.select_dtypes(include=[np.number])

    if df_num.empty:
        raise ValueError("No hay columnas numéricas para calcular covarianzas.")

    matriz = df_num.cov()
    return {
        columna: {indice: _sanear_valor(valor) for indice, valor in serie.items()}
        for columna, serie in matriz.to_dict().items()
    }


def calcular_percentiles(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    *,
    columnas: Sequence[str] | None = None,
    percentiles: Sequence[float] = (0.25, 0.5, 0.75),
    interpolacion: str = "linear",
) -> Registro:
    """Obtiene percentiles para columnas numéricas, incluyendo los cuartiles."""

    if not percentiles:
        raise ValueError("Debes indicar al menos un percentil.")
    for valor in percentiles:
        if not 0 <= valor <= 1:
            raise ValueError("Los percentiles deben estar entre 0 y 1.")

    df = _a_dataframe(datos)
    if columnas is not None:
        faltantes = [col for col in columnas if col not in df.columns]
        if faltantes:
            raise KeyError(f"Columnas inexistentes para percentiles: {', '.join(faltantes)}")
        df_num = df.loc[:, list(columnas)].apply(pd.to_numeric, errors="coerce")
    else:
        df_num = df.select_dtypes(include=[np.number])

    if df_num.empty:
        raise ValueError("No hay columnas numéricas para calcular percentiles.")

    cuantiles = df_num.quantile(percentiles, interpolation=interpolacion)

    resultado: Registro = {}
    for columna in df_num.columns:
        serie = cuantiles[columna]
        resumen_columna: dict[str, Any] = {}
        for indice, valor in serie.items():
            porcentaje = indice * 100
            if math.isclose(porcentaje, round(porcentaje)):
                etiqueta = f"p{int(round(porcentaje))}"
            else:
                etiqueta = f"p{porcentaje:.6g}".rstrip("0").rstrip(".")
            resumen_columna[etiqueta] = _sanear_valor(valor)
        resultado[columna] = resumen_columna
    return resultado


def resumen_rapido(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
) -> list[Registro]:
    """Genera un resumen compacto por columna (tipo, nulos, valores claves)."""

    df = _a_dataframe(datos)
    resumen: list[Registro] = []
    for columna in df.columns:
        serie = df[columna]
        sin_nulos = serie.dropna()
        entrada: Registro = {
            "columna": columna,
            "tipo": str(serie.dtype),
            "n_filas": int(len(serie)),
            "nulos": int(serie.isna().sum()),
            "unicos": int(serie.nunique(dropna=True)),
        }
        ejemplo = _sanear_valor(sin_nulos.iloc[0]) if not sin_nulos.empty else None
        entrada["ejemplo"] = ejemplo

        if pd.api.types.is_numeric_dtype(serie):
            entrada.update(
                {
                    "min": _sanear_valor(serie.min(skipna=True)),
                    "max": _sanear_valor(serie.max(skipna=True)),
                    "media": _sanear_valor(serie.mean(skipna=True)),
                }
            )
        elif pd.api.types.is_datetime64_any_dtype(serie):
            entrada.update(
                {
                    "min": _sanear_valor(serie.min(skipna=True)),
                    "max": _sanear_valor(serie.max(skipna=True)),
                }
            )

        resumen.append(entrada)

    return resumen



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


def mutar_columna(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    nombre: str,
    funcion: Callable[[Registro], Any],
    *,
    crear_si_no_existe: bool = True,
) -> Tabla:
    """Crea o modifica ``nombre`` evaluando ``funcion`` fila a fila.

    Parameters
    ----------
    datos:
        Datos tabulares convertibles a :class:`pandas.DataFrame`.
    nombre:
        Columna a crear o actualizar.
    funcion:
        Callable que recibe cada fila como diccionario y devuelve el valor para la
        columna ``nombre``.
    crear_si_no_existe:
        Cuando es ``False`` se exige que ``nombre`` exista previamente en los datos.
    """

    df = _a_dataframe(datos)
    if nombre not in df.columns and not crear_si_no_existe:
        raise KeyError(f"La columna '{nombre}' no existe y no se permite crearla.")

    def _evaluar(fila: pd.Series) -> Any:
        try:
            return funcion(fila.to_dict())
        except Exception as exc:  # pragma: no cover - defensivo
            raise ValueError(f"Error al calcular la columna '{nombre}': {exc}") from exc

    serie = df.apply(_evaluar, axis=1)
    df[nombre] = serie
    return _sanear_registros(df.to_dict(orient="records"))


def separar_columna(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columna: str,
    *,
    en: Sequence[str],
    separador: str = " ",
    maximo_divisiones: int | None = None,
    eliminar_original: bool = True,
    descartar_nulos: bool = False,
    relleno: Any | None = None,
) -> Tabla:
    """Divide ``columna`` en múltiples campos usando ``pandas.Series.str.split``.

    Parameters
    ----------
    datos:
        Registros tabulares convertibles a :class:`pandas.DataFrame`.
    columna:
        Nombre de la columna que se separará.
    en:
        Secuencia con los nombres de las columnas resultantes.
    separador:
        Delimitador utilizado al fragmentar el texto. Se pasa directamente a
        :meth:`pandas.Series.str.split`.
    maximo_divisiones:
        Número máximo de divisiones a realizar. Por defecto se limita a
        ``len(en) - 1`` para conservar la última parte completa.
    eliminar_original:
        Cuando es ``True`` elimina ``columna`` tras la separación.
    descartar_nulos:
        Si es ``True`` descarta las filas donde alguna de las nuevas columnas
        queda vacía tras el proceso. El filtrado se evalúa después de aplicar
        ``relleno``.
    relleno:
        Valor opcional que reemplazará los fragmentos faltantes antes de
        evaluar ``descartar_nulos``. Usa ``None`` (por defecto) para conservar
        los ``NA`` generados por ``pandas``.

    Returns
    -------
    Tabla
        Lista de registros con las columnas recién creadas.

    Notas
    -----
    Inspirada en la función ``separate`` de *tidyr* (R) y en ``separatecols``
    de *DataFrames.jl* (Julia), manteniendo compatibilidad semántica en la
    manera en que se generan las nuevas columnas y se tratan los valores
    faltantes.
    """

    destinos = list(en)
    if not destinos:
        raise ValueError("Debes proporcionar al menos una columna de destino.")

    df = _a_dataframe(datos)
    if columna not in df.columns:
        raise KeyError(f"La columna '{columna}' no existe en los datos.")

    serie_original = df[columna]
    serie_texto = serie_original.astype("string")
    divisiones = len(destinos) - 1 if maximo_divisiones is None else maximo_divisiones
    partes = serie_texto.str.split(separador, n=divisiones, expand=True)

    # Garantizar que existan suficientes columnas intermedias
    while partes.shape[1] < len(destinos):
        partes[partes.shape[1]] = pd.NA
    partes = partes.iloc[:, : len(destinos)].copy()
    partes.columns = destinos

    if relleno is not None:
        partes = partes.fillna(relleno).replace({pd.NA: relleno})

    if descartar_nulos:
        mascara_validos = ~partes.isna().any(axis=1)
        df = df.loc[mascara_validos].copy()
        partes = partes.loc[mascara_validos].copy()
    else:
        partes = partes.reindex(df.index, fill_value=pd.NA)

    for destino in destinos:
        df[destino] = partes[destino]

    if eliminar_original:
        df = df.drop(columns=[columna])

    return _sanear_registros(df.to_dict(orient="records"))


def unir_columnas(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columnas: Sequence[str],
    destino: str,
    *,
    separador: str = "_",
    omitir_nulos: bool = True,
    relleno: str = "",
    eliminar_original: bool = True,
) -> Tabla:
    """Concatena ``columnas`` en ``destino`` controlando valores faltantes.

    Parameters
    ----------
    datos:
        Datos tabulares convertibles a :class:`pandas.DataFrame`.
    columnas:
        Columnas que se unirán, en orden.
    destino:
        Nombre de la columna resultante.
    separador:
        Texto utilizado entre cada fragmento al unir.
    omitir_nulos:
        Cuando es ``True`` ignora los valores nulos y elimina separadores
        redundantes. Si todas las columnas están vacías la salida será ``None``.
    relleno:
        Cadena empleada para sustituir valores faltantes cuando
        ``omitir_nulos`` es ``False``. Se ignora cuando ``omitir_nulos`` es
        ``True``. Por defecto se usa la cadena vacía.
    eliminar_original:
        Si es ``True`` elimina las columnas utilizadas una vez creada la nueva
        columna.

    Returns
    -------
    Tabla
        Tabla resultante con la columna combinada.

    Notas
    -----
    El comportamiento replica el de ``unite`` en *tidyr* (R) y las
    transformaciones ``select``/``ByRow`` de *DataFrames.jl*, manteniendo la
    compatibilidad conceptual sobre cómo se tratan los separadores y los
    valores nulos durante la concatenación.
    """

    columnas_ordenadas = list(columnas)
    if not columnas_ordenadas:
        raise ValueError("Debes especificar al menos una columna a unir.")

    df = _a_dataframe(datos)
    faltantes = [col for col in columnas_ordenadas if col not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas inexistentes para unir: {', '.join(faltantes)}")

    resultados: list[Any] = []
    for valores in df[columnas_ordenadas].itertuples(index=False, name=None):
        piezas: list[str] = []
        for valor in valores:
            if pd.isna(valor):
                if omitir_nulos:
                    continue
                piezas.append(str(relleno))
            else:
                piezas.append(str(valor))

        if not piezas:
            resultados.append(None if omitir_nulos else str(relleno))
        else:
            resultados.append(separador.join(piezas))

    df[destino] = resultados

    if eliminar_original:
        a_eliminar = [col for col in columnas_ordenadas if col != destino]
        if a_eliminar:
            df = df.drop(columns=a_eliminar)

    return _sanear_registros(df.to_dict(orient="records"))


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


def ordenar_tabla(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    por: str | Sequence[str],
    ascendente: bool | Sequence[bool] = True,
) -> Tabla:
    """Ordena ``datos`` por las columnas indicadas inspirándose en ``pandas`` y ``R``.

    Parameters
    ----------
    datos:
        Registros tabulares convertibles a :class:`pandas.DataFrame`.
    por:
        Nombre de la columna o lista de columnas utilizadas como clave de orden.
    ascendente:
        Indicador global o lista booleana que define el sentido del ordenamiento
        para cada columna. Por defecto se ordena de forma ascendente.

    Returns
    -------
    Tabla
        Lista de diccionarios ordenada según las claves solicitadas.
    """

    df = _a_dataframe(datos)
    columnas = [por] if isinstance(por, str) else list(por)
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas inexistentes para ordenar: {', '.join(faltantes)}")

    if isinstance(ascendente, bool):
        sentido: bool | list[bool] = ascendente
    else:
        if isinstance(ascendente, Sequence) and not isinstance(ascendente, (str, bytes)):
            sentido = list(ascendente)
            if len(sentido) != len(columnas):
                raise ValueError("La lista 'ascendente' debe coincidir con las columnas.")
            if not all(isinstance(valor, bool) for valor in sentido):
                raise TypeError("Los valores en 'ascendente' deben ser booleanos.")
        else:  # pragma: no cover - verificación defensiva
            raise TypeError("'ascendente' debe ser un booleano o secuencia de booleanos.")

    ordenado = df.sort_values(columnas, ascending=sentido, na_position="last")
    return _sanear_registros(ordenado.to_dict(orient="records"))


def combinar_tablas(
    izquierda: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    derecha: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    claves: (
        str
        | Sequence[str]
        | tuple[str | Sequence[str], str | Sequence[str]]
        | Mapping[str, str | Sequence[str]]
    ),
    tipo: str = "inner",
) -> Tabla:
    """Combina tablas al estilo ``pandas.merge`` y ``dplyr::join`` manteniendo saneamiento.

    Parameters
    ----------
    izquierda, derecha:
        Tablas o estructuras convertibles a :class:`pandas.DataFrame`.
    claves:
        Columna compartida o par de columnas (izquierda, derecha) empleadas como
        llave de unión. Puede ser una cadena, una secuencia o un ``dict`` con las
        claves ``"izquierda"`` y ``"derecha"``.
    tipo:
        Variante del join a realizar: ``inner``, ``left``, ``right``, ``outer`` o ``cross``.

    Returns
    -------
    Tabla
        Lista de registros combinados según el tipo de unión solicitado.
    """

    permitidos = {"inner", "left", "right", "outer", "cross"}
    if tipo not in permitidos:
        raise ValueError(f"Tipo de combinación no soportado: {tipo}")

    df_izq = _a_dataframe(izquierda)
    df_der = _a_dataframe(derecha)

    def _a_lista(valor: str | Sequence[str]) -> list[str]:
        if isinstance(valor, str):
            return [valor]
        return list(valor)

    if isinstance(claves, Mapping):
        if "izquierda" not in claves or "derecha" not in claves:
            raise KeyError("El mapeo de 'claves' debe incluir 'izquierda' y 'derecha'.")
        claves_izq = _a_lista(claves["izquierda"])
        claves_der = _a_lista(claves["derecha"])
    elif isinstance(claves, tuple) and len(claves) == 2:
        claves_izq = _a_lista(claves[0])
        claves_der = _a_lista(claves[1])
    else:
        claves_izq = _a_lista(claves)  # type: ignore[arg-type]
        claves_der = claves_izq

    if len(claves_izq) != len(claves_der):
        raise ValueError("Las claves izquierda y derecha deben tener la misma longitud.")

    faltantes_izq = [col for col in claves_izq if col not in df_izq.columns]
    faltantes_der = [col for col in claves_der if col not in df_der.columns]
    if faltantes_izq or faltantes_der:
        faltantes = []
        if faltantes_izq:
            faltantes.append(f"izquierda: {', '.join(faltantes_izq)}")
        if faltantes_der:
            faltantes.append(f"derecha: {', '.join(faltantes_der)}")
        raise KeyError(f"Columnas inexistentes para combinar ({'; '.join(faltantes)})")

    combinado = pd.merge(
        df_izq,
        df_der,
        how=tipo,
        left_on=claves_izq,
        right_on=claves_der,
        sort=False,
        copy=False,
    )
    return _sanear_registros(combinado.to_dict(orient="records"))


def rellenar_nulos(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    valores: Mapping[str, Any],
) -> Tabla:
    """Rellena valores faltantes por columna siguiendo ``pandas`` y ``tidyr`` de R.

    Parameters
    ----------
    datos:
        Datos tabulares convertibles a :class:`pandas.DataFrame`.
    valores:
        Diccionario ``columna -> valor`` con los reemplazos para cada campo.

    Returns
    -------
    Tabla
        Tabla saneada donde los valores nulos se sustituyeron según ``valores``.
    """

    df = _a_dataframe(datos)
    faltantes = [col for col in valores.keys() if col not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas inexistentes para rellenar: {', '.join(faltantes)}")
    relleno = df.fillna(value=dict(valores))
    return _sanear_registros(relleno.to_dict(orient="records"))


def pivotar_ancho(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    *,
    id_columnas: str | Sequence[str] | None = None,
    nombres_desde: str | Sequence[str],
    valores_desde: str | Sequence[str],
    valores_relleno: Any | Mapping[str, Any] | None = None,
    agregacion: str
    | Sequence[str]
    | Callable[[pd.Series], Any]
    | Mapping[str, str | Sequence[str] | Callable[[pd.Series], Any]]
    | None = None,
) -> Tabla:
    """Convierte datos en formato largo a ancho similar a ``pivot_wider`` de *tidyr*.

    Parameters
    ----------
    datos:
        Registros o columnas convertibles a :class:`pandas.DataFrame`.
    id_columnas:
        Columnas que se mantienen como identificadores en la salida. Si es ``None``
        se infieren como todas las columnas distintas a ``nombres_desde`` y
        ``valores_desde``.
    nombres_desde:
        Columna(s) cuyos valores se usarán como nuevos encabezados.
    valores_desde:
        Columna(s) que se distribuyen entre los nuevos encabezados.
    valores_relleno:
        Valor o diccionario ``columna -> valor`` para reemplazar resultados nulos
        tras el pivoteo.
    agregacion:
        Función de agregación opcional utilizada cuando existen múltiples filas por
        combinación de identificadores y encabezados. Por defecto se emplea ``'first'``.
    """

    df = _a_dataframe(datos)

    def _asegurar_lista(entrada: str | Sequence[str]) -> list[str]:
        if isinstance(entrada, str):
            return [entrada]
        return list(entrada)

    columnas_nombres = _asegurar_lista(nombres_desde)
    columnas_valores = _asegurar_lista(valores_desde)

    if id_columnas is None:
        columnas_id = [
            columna
            for columna in df.columns
            if columna not in columnas_nombres and columna not in columnas_valores
        ]
        if not columnas_id:
            raise ValueError(
                "No fue posible inferir columnas identificadoras. Especifica 'id_columnas'."
            )
    else:
        columnas_id = _asegurar_lista(id_columnas)

    faltantes = [
        columna
        for columna in columnas_id + columnas_nombres + columnas_valores
        if columna not in df.columns
    ]
    if faltantes:
        raise KeyError(
            "Columnas inexistentes para pivotar en ancho: "
            f"{', '.join(dict.fromkeys(faltantes))}"
        )

    aggfunc = agregacion if agregacion is not None else "first"
    pivotado = pd.pivot_table(
        df,
        index=columnas_id,
        columns=columnas_nombres,
        values=columnas_valores,
        aggfunc=aggfunc,
        dropna=False,
    ).reset_index()

    if isinstance(pivotado.columns, pd.MultiIndex):
        columnas_planas = [
            "_".join(
                [str(nivel) for nivel in columna if str(nivel) not in {"", "None"}]
            ).strip("_")
            for columna in pivotado.columns.values
        ]
        pivotado.columns = columnas_planas

    columnas_identificadoras = list(pivotado.columns[: len(columnas_id)])

    if valores_relleno is not None:
        columnas_objetivo = [
            columna for columna in pivotado.columns if columna not in columnas_identificadoras
        ]
        if isinstance(valores_relleno, Mapping):
            relleno_filtrado = {
                columna: valores_relleno[columna]
                for columna in columnas_objetivo
                if columna in valores_relleno
            }
            if relleno_filtrado:
                pivotado = pivotado.fillna(value=relleno_filtrado)
        else:
            if columnas_objetivo:
                pivotado.loc[:, columnas_objetivo] = pivotado.loc[
                    :, columnas_objetivo
                ].fillna(valores_relleno)

    return _sanear_registros(pivotado.to_dict(orient="records"))


def pivotar_largo(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    columnas: str | Sequence[str],
    *,
    id_columnas: str | Sequence[str] | None = None,
    nombres_a: str = "variable",
    valores_a: str = "value",
    eliminar_nulos: bool = False,
) -> Tabla:
    """Transforma columnas en filas siguiendo el estilo de ``pivot_longer``.

    Parameters
    ----------
    datos:
        Estructura tabular convertible a :class:`pandas.DataFrame`.
    columnas:
        Columnas que se apilarán en la salida.
    id_columnas:
        Columnas que se mantienen sin modificar como identificadores. Si es ``None``
        se consideran todas las columnas no incluidas en ``columnas``.
    nombres_a:
        Nombre de la columna resultante con las etiquetas originales.
    valores_a:
        Nombre de la columna que contendrá los valores apilados.
    eliminar_nulos:
        Cuando es ``True`` se eliminan las filas cuyo valor resultante es nulo.
    """

    df = _a_dataframe(datos)

    def _asegurar_lista(entrada: str | Sequence[str]) -> list[str]:
        if isinstance(entrada, str):
            return [entrada]
        return list(entrada)

    columnas_objetivo = _asegurar_lista(columnas)

    if id_columnas is None:
        columnas_id = [col for col in df.columns if col not in columnas_objetivo]
    else:
        columnas_id = _asegurar_lista(id_columnas)

    faltantes = [
        columna
        for columna in columnas_id + columnas_objetivo
        if columna not in df.columns
    ]
    if faltantes:
        raise KeyError(
            "Columnas inexistentes para pivotar en largo: "
            f"{', '.join(dict.fromkeys(faltantes))}"
        )

    largo = pd.melt(
        df,
        id_vars=columnas_id,
        value_vars=columnas_objetivo,
        var_name=nombres_a,
        value_name=valores_a,
    )

    if eliminar_nulos:
        largo = largo.dropna(subset=[valores_a])

    return _sanear_registros(largo.to_dict(orient="records"))


def desplegar_tabla(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    *,
    identificadores: str | Sequence[str] | None = None,
    valores: str | Sequence[str] | None = None,
    var_name: str | None = None,
    value_name: str | None = None,
    ignorar_indice: bool = True,
) -> Tabla:
    """Convierte ``datos`` a formato largo como ``pandas.melt`` o ``pivot_longer`` de R.

    Parameters
    ----------
    datos:
        Tabla de origen convertible a :class:`pandas.DataFrame`.
    identificadores:
        Columna o columnas que permanecen como identificadores en la salida
        (argumento ``id_vars`` de :func:`pandas.melt`). Si es ``None`` se usan
        todas las columnas salvo las indicadas en ``valores``.
    valores:
        Columnas que se apilan en formato largo (equivalente a ``value_vars``).
        Si es ``None`` se consideran todas las columnas no presentes en
        ``identificadores``.
    var_name:
        Nombre opcional para la columna con las etiquetas originales. Por
        defecto se conserva ``"variable"`` igual que :func:`pandas.melt`.
    value_name:
        Nombre opcional para la columna con los valores. Mantiene ``"value"``
        cuando no se especifica.
    ignorar_indice:
        Replica el parámetro ``ignore_index`` de :func:`pandas.melt`. Cuando es
        ``True`` se reinicia el índice en la tabla resultante.

    Returns
    -------
    Tabla
        Lista de registros saneados en formato largo.
    """

    df = _a_dataframe(datos)

    def _asegurar_lista(entrada: str | Sequence[str] | None) -> list[str] | None:
        if entrada is None:
            return None
        if isinstance(entrada, str):
            return [entrada]
        return list(entrada)

    columnas_id = _asegurar_lista(identificadores)
    columnas_valor = _asegurar_lista(valores)

    def _validar(nombre: str, columnas: list[str] | None) -> None:
        if columnas is None:
            return
        faltantes = [col for col in columnas if col not in df.columns]
        if faltantes:
            raise KeyError(f"Columnas inexistentes para {nombre}: {', '.join(faltantes)}")

    _validar("identificadores", columnas_id)
    _validar("valores", columnas_valor)

    argumentos: dict[str, Any] = {
        "id_vars": columnas_id,
        "value_vars": columnas_valor,
        "ignore_index": ignorar_indice,
    }
    if var_name is not None:
        argumentos["var_name"] = var_name
    if value_name is not None:
        argumentos["value_name"] = value_name

    derretido = pd.melt(df, **argumentos)
    return _sanear_registros(derretido.to_dict(orient="records"))


def pivotar_tabla(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    index: str | Sequence[str],
    columnas: str | Sequence[str],
    valores: str | Sequence[str],
    agregacion: str | Sequence[str] | Mapping[str, str | Sequence[str] | Callable[[pd.Series], Any]],
) -> Tabla:
    """Reorganiza datos tabulares como ``pandas.pivot_table`` y ``tidyr::pivot_wider``.

    Parameters
    ----------
    datos:
        Datos de origen convertibles a :class:`pandas.DataFrame`.
    index:
        Columna o columnas que identifican cada fila pivoteada.
    columnas:
        Columna(s) cuyos valores formarán nuevos encabezados.
    valores:
        Medidas que se distribuyen en la tabla resultante.
    agregacion:
        Función o etiqueta(s) de agregación compatible(s) con ``pandas``.

    Returns
    -------
    Tabla
        Lista de registros pivoteados con encabezados aplanados y valores saneados.
    """

    df = _a_dataframe(datos)

    def _asegurar_lista(entrada: str | Sequence[str]) -> list[str]:
        if isinstance(entrada, str):
            return [entrada]
        return list(entrada)

    columnas_index = _asegurar_lista(index)
    columnas_columnas = _asegurar_lista(columnas)
    columnas_valores = _asegurar_lista(valores)

    faltantes = [
        col
        for col in columnas_index + columnas_columnas + columnas_valores
        if col not in df.columns
    ]
    if faltantes:
        raise KeyError(f"Columnas inexistentes para pivotar: {', '.join(dict.fromkeys(faltantes))}")

    pivotado = pd.pivot_table(
        df,
        index=columnas_index,
        columns=columnas_columnas,
        values=columnas_valores,
        aggfunc=agregacion,
        dropna=False,
    ).reset_index()

    if isinstance(pivotado.columns, pd.MultiIndex):
        columnas_pivot = [
            "_".join([str(nivel) for nivel in col if str(nivel) != ""]).strip("_")
            for col in pivotado.columns.values
        ]
        pivotado.columns = columnas_pivot

    return _sanear_registros(pivotado.to_dict(orient="records"))


def tabla_cruzada(
    datos: Iterable[Registro] | Mapping[str, Sequence[Any]] | pd.DataFrame,
    filas: str | Sequence[str],
    columnas: str | Sequence[str],
    *,
    valores: str | Sequence[Any] | pd.Series | None = None,
    aggfunc: str
    | Callable[[pd.Series], Any]
    | Sequence[str | Callable[[pd.Series], Any]]
    | None = "count",
    normalizar: str | bool | None = None,
) -> Tabla:
    """Construye una tabla cruzada mediante :func:`pandas.crosstab`.

    Parameters
    ----------
    datos:
        Registros tabulares convertibles a :class:`pandas.DataFrame`.
    filas:
        Columna o columnas categóricas que formarán el índice de la tabla.
    columnas:
        Columna o columnas que se expandirán como encabezados.
    valores:
        Columna con los valores a agregar o una secuencia con una medida por
        fila. Cuando es ``None`` (por defecto) la función devuelve conteos.
    aggfunc:
        Función de agregación compatible con ``pandas``. Se ignora cuando no se
        proporcionan ``valores`` y por defecto cuenta los registros.
    normalizar:
        Permite obtener proporciones en lugar de valores absolutos. Acepta los
        alias ``"filas"``/``"index"`` y ``"columnas"``/``"columns"`` para
        normalizar por filas o columnas, ``"total"``/``"all"``/``True`` para el
        total global y ``None`` para omitir la normalización.

    Returns
    -------
    Tabla
        Lista de registros con los encabezados aplanados y valores saneados.

    Raises
    ------
    KeyError
        Si alguna columna indicada en ``filas``, ``columnas`` o ``valores`` no
        existe en los datos de entrada.
    ValueError
        Si ``valores`` no coincide en longitud con los datos o si ``normalizar``
        tiene un alias desconocido.
    """

    df = _a_dataframe(datos)

    def _asegurar_columnas(
        seleccion: str | Sequence[str], nombre: str
    ) -> pd.Series | list[pd.Series]:
        columnas_sel = [seleccion] if isinstance(seleccion, str) else list(seleccion)
        if not columnas_sel:
            raise ValueError(f"Debes proporcionar al menos una columna para {nombre}.")
        faltantes = [col for col in columnas_sel if col not in df.columns]
        if faltantes:
            raise KeyError(
                f"Columnas inexistentes para {nombre}: {', '.join(dict.fromkeys(faltantes))}"
            )
        series = [df[col] for col in columnas_sel]
        return series[0] if len(series) == 1 else series

    index = _asegurar_columnas(filas, "filas")
    columnas_sel = _asegurar_columnas(columnas, "columnas")

    if valores is None:
        valores_crosstab: pd.Series | None = None
        if aggfunc not in (None, "count"):
            raise ValueError(
                "No es posible usar 'aggfunc' sin proporcionar la columna 'valores'."
            )
        aggfunc_param = None
    else:
        if isinstance(valores, str):
            if valores not in df.columns:
                raise KeyError(f"La columna '{valores}' indicada en 'valores' no existe.")
            valores_crosstab = df[valores]
        else:
            serie_valores = pd.Series(valores)
            if len(serie_valores) != len(df.index):
                raise ValueError(
                    "La secuencia entregada en 'valores' debe tener la misma longitud que los datos."
                )
            valores_crosstab = serie_valores
        aggfunc_param = aggfunc
        if aggfunc_param is None:
            raise ValueError(
                "Debes indicar una función de agregación cuando proporcionas la columna 'valores'."
            )

    if normalizar in (None, False):
        normalizar_param: str | bool = False
    elif normalizar is True:
        normalizar_param = "all"
    elif isinstance(normalizar, str):
        mapa_normalizacion = {
            "filas": "index",
            "fila": "index",
            "index": "index",
            "indices": "index",
            "columnas": "columns",
            "columna": "columns",
            "columns": "columns",
            "total": "all",
            "todo": "all",
            "all": "all",
        }
        clave = normalizar.lower()
        if clave not in mapa_normalizacion:
            raise ValueError(
                "El parámetro 'normalizar' solo admite None, 'filas', 'columnas', 'total' o sus equivalentes."
            )
        normalizar_param = mapa_normalizacion[clave]
    else:
        raise ValueError(
            "El parámetro 'normalizar' debe ser None, un booleano o un alias conocido ('filas', 'columnas', 'total')."
        )

    tabla = pd.crosstab(
        index=index,
        columns=columnas_sel,
        values=valores_crosstab,
        aggfunc=aggfunc_param,
        normalize=normalizar_param,
        dropna=False,
    )

    resultado = tabla.reset_index()
    if isinstance(resultado.columns, pd.MultiIndex):
        resultado.columns = [
            "_".join(
                str(nivel) for nivel in col if str(nivel) not in {"", "None"}
            ).strip("_")
            for col in resultado.columns.to_flat_index()
        ]
    else:
        resultado.columns = [col if isinstance(col, str) else str(col) for col in resultado.columns]

    return _sanear_registros(resultado.to_dict(orient="records"))


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

