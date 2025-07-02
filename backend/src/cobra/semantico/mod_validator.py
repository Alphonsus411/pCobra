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
import tomllib
import yaml
from typing import Dict, Any
from jsonschema import validate, ValidationError

from src.cli.utils.semver import es_version_valida
from src.cobra.transpilers import module_map

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "cobra_mod_schema.yaml")
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = yaml.safe_load(f)


def cargar_mod(path: str | None = None) -> Dict[str, Any]:
    """Carga y devuelve el contenido de ``cobra.mod``.

    Se intenta primero interpretar el archivo como TOML. Si falla se usa YAML.
    Si el archivo no existe se devuelve un diccionario vacío.
    """
    path = path or module_map.MODULE_MAP_PATH
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as f:
        data = f.read()
    try:
        return tomllib.loads(data.decode("utf-8"))
    except Exception:
        return yaml.safe_load(data) or {}


def validar_mod(path: str | None = None) -> None:
    """Valida el contenido de ``cobra.mod``.

    Lanza ``ValueError`` si se detecta algún problema.
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
        version = info.get("version")
        if version and not es_version_valida(str(version)):
            errores.append(f"Versión inválida para {modulo}: {version}")
        for clave in ("python", "js"):
            ruta = info.get(clave)
            if ruta:
                if not os.path.exists(ruta):
                    errores.append(f"No existe el archivo {ruta} para {modulo}")
                registro = archivos_py if clave == "python" else archivos_js
                if ruta in registro:
                    errores.append(f"Archivo duplicado: {ruta}")
                registro.add(ruta)
    if errores:
        mensaje = "; ".join(errores)
        raise ValueError(f"Archivo cobra.mod inválido: {mensaje}")
