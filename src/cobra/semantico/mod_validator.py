"""Validación de archivos cobra.mod.

Este módulo proporciona utilidades para leer un archivo ``cobra.mod``
(tanto en formato YAML como TOML) y verificar su integridad. Las
comprobaciones incluyen:

- Existencia de los archivos declarados en las claves ``python`` y ``js``.
- Validez de las versiones indicadas utilizando el formato semver.
- Detección de nombres de módulos o archivos duplicados.
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional

try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib
import yaml
from jsonschema import validate, ValidationError

from cobra.cli.utils.semver import es_version_valida
from cobra.transpilers import module_map

# Constantes
MAX_FILE_SIZE = 10_000_000  # 10MB
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "cobra_mod_schema.yaml")

# Verificar existencia del esquema y cargarlo
if not os.path.exists(SCHEMA_PATH):
    raise FileNotFoundError(f"No se encuentra el archivo de esquema: {SCHEMA_PATH}")

try:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        SCHEMA = yaml.safe_load(f)
except (yaml.YAMLError, OSError) as e:
    raise RuntimeError(f"Error al cargar el esquema: {e}") from None


def cargar_mod(path: str | None = None) -> Dict[str, Any]:
    """Carga y devuelve el contenido de ``cobra.mod``.

    Args:
        path: Ruta al archivo cobra.mod. Si es None, usa la ruta por defecto.

    Returns:
        Dict[str, Any]: Contenido del archivo parseado como diccionario.

    Raises:
        ValueError: Si el archivo está mal formateado o es demasiado grande.
        OSError: Si hay problemas al leer el archivo.
        TypeError: Si path no es str o None.
    """
    if not isinstance(path, (str, type(None))):
        raise TypeError("path debe ser str o None")

    path = path or module_map.MODULE_MAP_PATH
    if not os.path.exists(path):
        return {}

    # Verificar tamaño del archivo
    if os.path.getsize(path) > MAX_FILE_SIZE:
        raise ValueError(f"Archivo demasiado grande (máximo {MAX_FILE_SIZE} bytes)")

    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        raise OSError(f"Error al leer el archivo {path}: {e}") from None

    try:
        return tomllib.loads(data.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        try:
            resultado = yaml.safe_load(data)
            return resultado if resultado is not None else {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error al parsear archivo: {e}") from None


def validar_mod(path: str | None = None) -> None:
    """Valida el contenido de ``cobra.mod``.

    Args:
        path: Ruta opcional al archivo cobra.mod.

    Raises:
        ValueError: Si se detecta algún problema en la validación.
        TypeError: Si path no es str o None.
        OSError: Si hay problemas al acceder a los archivos.
    """
    datos = cargar_mod(path)
    try:
        validate(instance=datos, schema=SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Archivo cobra.mod inválido: {e.message}") from None

    errores: list[str] = []
    archivos_py: set[str] = set()
    archivos_js: set[str] = set()

    for modulo, info in datos.items():
        if modulo == "lock":
            continue

        if not isinstance(info, dict):
            errores.append(f"Entrada inválida para {modulo}")
            continue

        # Validar versión
        version = info.get("version")
        if version is not None:
            try:
                if not es_version_valida(str(version)):
                    errores.append(f"Versión inválida para {modulo}: {version}")
            except (TypeError, ValueError):
                errores.append(f"Formato de versión inválido para {modulo}")

        # Validar archivos
        for clave in ("python", "js"):
            ruta = info.get(clave)
            if not ruta:
                continue

            if not isinstance(ruta, str):
                errores.append(f"Ruta inválida para {clave} en {modulo}")
                continue

            registro = archivos_py if clave == "python" else archivos_js
            if ruta in registro:
                errores.append(f"Archivo duplicado: {ruta}")
            else:
                registro.add(ruta)
                try:
                    if not os.path.exists(ruta):
                        errores.append(f"No existe el archivo {ruta} para {modulo}")
                except OSError as e:
                    errores.append(f"Error al verificar archivo {ruta}: {e}")

    if errores:
        mensaje = "; ".join(errores)
        raise ValueError(f"Archivo cobra.mod inválido: {mensaje}")