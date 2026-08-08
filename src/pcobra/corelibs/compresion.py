"""Utilidades de compresión ZIP para las corelibs de Cobra.

La compatibilidad con otros formatos como tar o gzip queda como extensión
futura; la superficie pública inicial cubre únicamente archivos ZIP.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZipInfo

from pcobra.corelibs._sandbox_paths import (
    resolver_destino_nuevo,
    resolver_ruta_existente,
)

PathLike = str | os.PathLike[str]

__all__ = ["crear_zip", "extraer_zip", "listar_zip"]

# Límites internos (no forman parte de la API pública) y sustituibles en pruebas o
# por integradores que necesiten una política más restrictiva.
_MAX_ENTRADAS = 10_000
_MAX_BYTES_ENTRADA = 100 * 1024 * 1024
_MAX_BYTES_TOTALES = 1024 * 1024 * 1024
_MAX_RATIO_COMPRESION = 100.0
_TAMANO_CHUNK = 64 * 1024


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
    destino_zip = resolver_destino_nuevo(_ruta_relativa_sandbox(destino, "destino"))
    if destino_zip.is_symlink():
        raise ValueError("El destino ZIP no puede ser un enlace simbólico")
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
    """Extrae ``origen`` en ``destino`` de forma confinada y limitada.

    Devuelve las rutas extraídas como cadenas. Cada miembro del ZIP se resuelve
    contra el directorio destino y se rechaza si queda fuera de él.
    """

    origen_zip = resolver_ruta_existente(_ruta_relativa_sandbox(origen, "origen"))
    destino_base = resolver_destino_nuevo(_ruta_relativa_sandbox(destino, "destino"))
    if destino_base.is_symlink():
        raise ValueError("El destino de extracción no puede ser un enlace simbólico")
    destino_base.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix=".pcobra-zip-", dir=destino_base))
    try:
        with ZipFile(origen_zip, "r") as archivo_zip:
            miembros = archivo_zip.infolist()
            rutas = _inspeccionar_miembros(miembros, destino_base)
            _comprobar_destinos_libres(rutas, destino_base)
            total_real = 0
            for miembro, ruta_final in zip(miembros, rutas):
                relativa = ruta_final.relative_to(destino_base)
                ruta_temporal = temporal / relativa
                if miembro.is_dir():
                    ruta_temporal.mkdir(parents=True, exist_ok=True)
                    continue
                ruta_temporal.parent.mkdir(parents=True, exist_ok=True)
                bytes_entrada = 0
                with (
                    archivo_zip.open(miembro) as entrada,
                    ruta_temporal.open("xb") as salida,
                ):
                    while chunk := entrada.read(_TAMANO_CHUNK):
                        bytes_entrada += len(chunk)
                        total_real += len(chunk)
                        if bytes_entrada > _MAX_BYTES_ENTRADA:
                            raise ValueError(
                                "Una entrada ZIP supera el tamaño permitido"
                            )
                        if total_real > _MAX_BYTES_TOTALES:
                            raise ValueError("El ZIP supera el tamaño total permitido")
                        salida.write(chunk)

        for miembro, ruta_final in zip(miembros, rutas):
            relativa = ruta_final.relative_to(destino_base)
            ruta_temporal = temporal / relativa
            if miembro.is_dir():
                ruta_final.mkdir(parents=True, exist_ok=True)
            else:
                ruta_final.parent.mkdir(parents=True, exist_ok=True)
                os.replace(ruta_temporal, ruta_final)
        return [str(ruta) for ruta in rutas]
    finally:
        shutil.rmtree(temporal, ignore_errors=True)


def listar_zip(origen: PathLike) -> list[str]:
    """Devuelve la lista simple de nombres incluidos en ``origen``."""

    origen_zip = resolver_ruta_existente(_ruta_relativa_sandbox(origen, "origen"))

    with ZipFile(origen_zip, "r") as archivo_zip:
        return archivo_zip.namelist()


def _normalizar_rutas(
    rutas: PathLike | list[PathLike] | tuple[PathLike, ...],
) -> list[Path]:
    if isinstance(rutas, (str, os.PathLike)):
        return [resolver_ruta_existente(_ruta_relativa_sandbox(rutas, "rutas"))]
    if not isinstance(rutas, (list, tuple)):
        raise TypeError("rutas debe ser una ruta o una lista/tupla de rutas")
    return [
        resolver_ruta_existente(_ruta_relativa_sandbox(ruta, f"rutas[{indice}]"))
        for indice, ruta in enumerate(rutas)
    ]


def _validar_ruta(ruta: PathLike, nombre_argumento: str) -> Path:
    return Path(_texto_ruta(ruta, nombre_argumento))


def _texto_ruta(ruta: PathLike, nombre_argumento: str) -> str:
    if not isinstance(ruta, (str, os.PathLike)):
        raise TypeError(
            f"{nombre_argumento} debe ser una ruta de texto o compatible con os.PathLike"
        )
    texto = os.fspath(ruta)
    if not isinstance(texto, str):
        raise TypeError(f"{nombre_argumento} debe representar una ruta de texto")
    if texto == "":
        raise ValueError(f"{nombre_argumento} no puede estar vacía")
    return texto


def _ruta_relativa_sandbox(ruta: PathLike, nombre_argumento: str) -> str:
    """Adapta rutas absolutas legacy solo cuando ya están dentro del sandbox."""

    texto = _texto_ruta(ruta, nombre_argumento)
    candidata = Path(texto).expanduser()
    if not candidata.is_absolute():
        return texto
    base = os.environ.get("COBRA_IO_BASE_DIR")
    if not base:
        raise ValueError("Las rutas absolutas requieren COBRA_IO_BASE_DIR")
    try:
        return str(
            candidata.resolve(strict=False).relative_to(Path(base).resolve(strict=True))
        )
    except ValueError as exc:
        raise ValueError("La ruta absoluta queda fuera del sandbox") from exc


def _resolver_base(rutas: list[Path], base: PathLike | None) -> Path:
    if not rutas:
        raise ValueError("Debe indicarse al menos una ruta para comprimir")

    if base is not None:
        base_resuelta = resolver_ruta_existente(_ruta_relativa_sandbox(base, "base"))
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


def _inspeccionar_miembros(miembros: list[ZipInfo], destino_base: Path) -> list[Path]:
    if len(miembros) > _MAX_ENTRADAS:
        raise ValueError("El ZIP supera la cantidad de entradas permitida")

    total_declarado = 0
    rutas: list[Path] = []
    for miembro in miembros:
        ruta = _ruta_segura_extraccion(destino_base, miembro.filename)
        tipo = stat.S_IFMT(miembro.external_attr >> 16)
        if tipo not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ValueError(f"Tipo de entrada ZIP no permitido: {miembro.filename}")
        if miembro.file_size > _MAX_BYTES_ENTRADA:
            raise ValueError("Una entrada ZIP supera el tamaño permitido")
        total_declarado += miembro.file_size
        if total_declarado > _MAX_BYTES_TOTALES:
            raise ValueError("El ZIP supera el tamaño total permitido")
        if miembro.compress_size:
            ratio = miembro.file_size / miembro.compress_size
        else:
            ratio = float("inf") if miembro.file_size else 1.0
        if ratio > _MAX_RATIO_COMPRESION:
            raise ValueError("Una entrada ZIP supera el ratio de compresión permitido")
        rutas.append(ruta)
    return rutas


def _comprobar_destinos_libres(rutas: list[Path], destino_base: Path) -> None:
    if len(set(rutas)) != len(rutas):
        raise ValueError("El ZIP contiene destinos duplicados")
    for ruta in rutas:
        if ruta.exists() or ruta.is_symlink():
            raise FileExistsError(f"El destino ya existe: {ruta}")
        for padre in ruta.parents:
            if padre == destino_base:
                break
            if padre.is_symlink() or (padre.exists() and not padre.is_dir()):
                raise FileExistsError(f"Un ancestro del destino no es seguro: {padre}")
