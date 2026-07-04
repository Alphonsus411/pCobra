"""Utilidades de compresión ZIP para las corelibs de Cobra.

La compatibilidad con otros formatos como tar o gzip queda como extensión
futura; la superficie pública inicial cubre únicamente archivos ZIP.
"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

PathLike = str | os.PathLike[str]

__all__ = ["crear_zip", "extraer_zip", "listar_zip"]


def crear_zip(
    destino: PathLike,
    rutas: PathLike | list[PathLike] | tuple[PathLike, ...],
    *,
    base: PathLike | None = None,
) -> list[str]:
    """Crea un ZIP en ``destino`` con las rutas indicadas y devuelve sus nombres.

    Cada ruta de ``rutas`` debe existir. Cuando ``base`` se proporciona, los
    nombres dentro del ZIP se calculan de forma relativa a ese directorio; si
    no se indica, se usa el directorio común de las rutas recibidas.
    """

    rutas_normalizadas = _normalizar_rutas(rutas)
    for ruta in rutas_normalizadas:
        if not ruta.exists():
            raise FileNotFoundError(f"La ruta a comprimir no existe: {ruta}")

    base_resuelta = _resolver_base(rutas_normalizadas, base)
    destino_zip = _validar_ruta(destino, "destino")
    destino_zip.parent.mkdir(parents=True, exist_ok=True)

    nombres: list[str] = []
    with ZipFile(destino_zip, "w") as archivo_zip:
        for ruta in rutas_normalizadas:
            for elemento in _iterar_elementos_zip(ruta):
                nombre = _nombre_en_zip(elemento, base_resuelta)
                archivo_zip.write(elemento, nombre)
                nombres.append(nombre)

    return nombres


def extraer_zip(origen: PathLike, destino: PathLike) -> list[str]:
    """Extrae ``origen`` en ``destino`` evitando path traversal.

    Devuelve las rutas extraídas como cadenas. Cada miembro del ZIP se resuelve
    contra el directorio destino y se rechaza si queda fuera de él.
    """

    origen_zip = _validar_ruta(origen, "origen")
    if not origen_zip.exists():
        raise FileNotFoundError(f"El ZIP de origen no existe: {origen_zip}")

    destino_base = _validar_ruta(destino, "destino").resolve()
    destino_base.mkdir(parents=True, exist_ok=True)
    rutas_extraidas: list[str] = []

    with ZipFile(origen_zip, "r") as archivo_zip:
        for miembro in archivo_zip.infolist():
            ruta_destino = _ruta_segura_extraccion(destino_base, miembro.filename)
            if miembro.is_dir():
                ruta_destino.mkdir(parents=True, exist_ok=True)
            else:
                ruta_destino.parent.mkdir(parents=True, exist_ok=True)
                with (
                    archivo_zip.open(miembro, "r") as origen_archivo,
                    ruta_destino.open("wb") as destino_archivo,
                ):
                    destino_archivo.write(origen_archivo.read())
            rutas_extraidas.append(str(ruta_destino))

    return rutas_extraidas


def listar_zip(origen: PathLike) -> list[str]:
    """Devuelve la lista simple de nombres incluidos en ``origen``."""

    origen_zip = _validar_ruta(origen, "origen")
    if not origen_zip.exists():
        raise FileNotFoundError(f"El ZIP de origen no existe: {origen_zip}")

    with ZipFile(origen_zip, "r") as archivo_zip:
        return archivo_zip.namelist()


def _normalizar_rutas(
    rutas: PathLike | list[PathLike] | tuple[PathLike, ...],
) -> list[Path]:
    if isinstance(rutas, (str, os.PathLike)):
        return [_validar_ruta(rutas, "rutas")]
    if not isinstance(rutas, (list, tuple)):
        raise TypeError("rutas debe ser una ruta o una lista/tupla de rutas")
    return [
        _validar_ruta(ruta, f"rutas[{indice}]") for indice, ruta in enumerate(rutas)
    ]


def _validar_ruta(ruta: PathLike, nombre_argumento: str) -> Path:
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


def _resolver_base(rutas: list[Path], base: PathLike | None) -> Path:
    if not rutas:
        raise ValueError("Debe indicarse al menos una ruta para comprimir")

    if base is not None:
        base_resuelta = _validar_ruta(base, "base").resolve()
        if not base_resuelta.exists():
            raise FileNotFoundError(f"La base no existe: {base_resuelta}")
        if not base_resuelta.is_dir():
            raise ValueError(f"La base debe ser un directorio: {base_resuelta}")
    else:
        padres = [ruta.resolve().parent for ruta in rutas]
        base_resuelta = Path(os.path.commonpath(padres)).resolve()

    for ruta in rutas:
        try:
            ruta.resolve().relative_to(base_resuelta)
        except ValueError as exc:
            raise ValueError(f"La ruta queda fuera de la base: {ruta}") from exc
    return base_resuelta


def _iterar_elementos_zip(ruta: Path) -> list[Path]:
    if ruta.is_dir():
        return sorted(
            (elemento for elemento in ruta.rglob("*") if elemento.is_file()),
            key=lambda p: str(p),
        )
    return [ruta]


def _nombre_en_zip(ruta: Path, base: Path) -> str:
    return ruta.resolve().relative_to(base).as_posix()


def _ruta_segura_extraccion(destino_base: Path, nombre: str) -> Path:
    nombre_normalizado = nombre.replace("\\", "/")
    ruta_posix = PurePosixPath(nombre_normalizado)
    if (
        ruta_posix.is_absolute()
        or ".." in ruta_posix.parts
        or _parece_ruta_windows_absoluta(nombre_normalizado)
    ):
        raise ValueError(f"Entrada ZIP insegura fuera del destino: {nombre}")

    ruta_destino = (destino_base / ruta_posix).resolve()
    try:
        ruta_destino.relative_to(destino_base)
    except ValueError as exc:
        raise ValueError(f"Entrada ZIP insegura fuera del destino: {nombre}") from exc
    return ruta_destino


def _parece_ruta_windows_absoluta(nombre: str) -> bool:
    return len(nombre) >= 2 and nombre[1] == ":" and nombre[0].isalpha()
