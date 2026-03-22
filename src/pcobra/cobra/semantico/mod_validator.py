"""Validación de archivos cobra.mod.

Este módulo proporciona utilidades para leer un archivo ``cobra.mod``
(tanto en formato YAML como TOML) y verificar su integridad. Las
comprobaciones incluyen:

- Existencia de los archivos declarados para los backends oficiales definidos en
  ``OFFICIAL_TARGETS``.
- Rechazo de aliases legacy o backends fuera de la lista canónica oficial.
- Validez de las versiones indicadas utilizando el formato semver.
- Detección de nombres de módulos o archivos duplicados.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

try:  # pragma: no cover - dependencia opcional
    import yaml
except ModuleNotFoundError:  # pragma: no cover - entornos sin PyYAML
    yaml = None  # type: ignore[assignment]

try:  # pragma: no cover - dependencia opcional
    from jsonschema import ValidationError, validate
except ModuleNotFoundError:  # pragma: no cover - entornos sin jsonschema
    ValidationError = None  # type: ignore[assignment]
    validate = None  # type: ignore[assignment]

from pcobra.cobra.cli.utils.semver import es_version_valida
from pcobra.cobra.transpilers import module_map
from pcobra.cobra.transpilers.target_utils import normalize_target_name
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS

# Constantes
MAX_FILE_SIZE = 10_000_000  # 10MB
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "cobra_mod_schema.yaml")

logger = logging.getLogger(__name__)

DEFAULT_REQUIRED_TARGETS: tuple[str, ...] = TIER1_TARGETS

# Verificar existencia del esquema y cargarlo
if not os.path.exists(SCHEMA_PATH):
    raise FileNotFoundError(f"No se encuentra el archivo de esquema: {SCHEMA_PATH}")

if yaml is None:
    logger.debug("PyYAML no está instalado; se omite la carga del esquema cobra_mod.")
    SCHEMA: dict[str, Any] | None = None
else:
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            SCHEMA = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:  # type: ignore[attr-defined]
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
        if yaml is None:
            raise ValueError(
                "No se pudo parsear cobra.mod: PyYAML no está instalado para usar el formato YAML.",
            )
        try:
            resultado = yaml.safe_load(data)
            return resultado if resultado is not None else {}
        except yaml.YAMLError as e:  # type: ignore[attr-defined]
            raise ValueError(f"Error al parsear archivo: {e}") from None




def _required_targets_from_policy() -> tuple[str, ...]:
    """Obtiene targets requeridos desde ``cobra.toml`` según política de proyecto."""
    toml_map = module_map.get_toml_map()
    if not isinstance(toml_map, dict):
        return DEFAULT_REQUIRED_TARGETS

    project_cfg = toml_map.get("project")
    if not isinstance(project_cfg, dict):
        project_cfg = toml_map.get("proyecto")

    raw_targets = None
    if isinstance(project_cfg, dict):
        raw_targets = project_cfg.get("required_targets")
        if raw_targets is None:
            raw_targets = project_cfg.get("targets_requeridos")

    if not raw_targets:
        return DEFAULT_REQUIRED_TARGETS

    if not isinstance(raw_targets, list):
        logger.warning(
            "La política de targets requeridos en cobra.toml debe ser lista; se usa valor por defecto %s.",
            DEFAULT_REQUIRED_TARGETS,
        )
        return DEFAULT_REQUIRED_TARGETS

    normalized: list[str] = []
    for target in raw_targets:
        if not isinstance(target, str):
            continue
        canonical = normalize_target_name(target)
        if canonical in OFFICIAL_TARGETS and canonical not in normalized:
            normalized.append(canonical)

    return tuple(normalized) if normalized else DEFAULT_REQUIRED_TARGETS


def _warn_if_tier2_used_as_optional_mapping(modulo: str, info: dict[str, Any]) -> None:
    """Emite trazas informativas cuando un módulo declara mappings Tier 2 opcionales."""
    tier2_present = [target for target in TIER2_TARGETS if info.get(target)]
    if tier2_present:
        logger.debug(
            "El módulo %s declara targets Tier 2 opcionales: %s",
            modulo,
            ", ".join(tier2_present),
        )


def _find_noncanonical_backend_keys(info: dict[str, Any]) -> list[str]:
    """Devuelve claves backend no canónicas presentes en un mapping de módulo."""
    ignored_keys = {"version"}
    noncanonical: list[str] = []
    for key in info:
        if key in ignored_keys:
            continue
        if key not in OFFICIAL_TARGETS:
            noncanonical.append(key)
    return sorted(noncanonical)


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
    if SCHEMA is None or validate is None or ValidationError is None:
        logger.debug(
            "Se omite la validación por esquema de cobra.mod por dependencias opcionales faltantes.",
        )
    else:
        try:
            validate(instance=datos, schema=SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Archivo cobra.mod inválido: {e.message}") from None

    errores: list[str] = []
    backend_archivos: dict[str, set[str]] = {
        target: set() for target in OFFICIAL_TARGETS
    }
    required_targets = _required_targets_from_policy()

    for modulo, info in datos.items():
        if modulo == "lock":
            continue

        if not isinstance(info, dict):
            errores.append(f"Entrada inválida para {modulo}")
            continue

        info_normalized = dict(info)
        _warn_if_tier2_used_as_optional_mapping(modulo, info_normalized)

        invalid_backend_keys = _find_noncanonical_backend_keys(info_normalized)
        if invalid_backend_keys:
            errores.append(
                "Backends no canónicos en {modulo}: {targets}. "
                "Usa únicamente: {allowed}".format(
                    modulo=modulo,
                    targets=", ".join(invalid_backend_keys),
                    allowed=", ".join(OFFICIAL_TARGETS),
                )
            )

        # Validar versión
        version = info_normalized.get("version")
        if version is not None:
            try:
                if not es_version_valida(str(version)):
                    errores.append(f"Versión inválida para {modulo}: {version}")
            except (TypeError, ValueError):
                errores.append(f"Formato de versión inválido para {modulo}")

        missing_required = [
            target for target in required_targets if not info_normalized.get(target)
        ]
        if missing_required:
            joined_targets = ", ".join(missing_required)
            errores.append(
                "Faltan rutas para targets requeridos por política "
                f"en {modulo}: {joined_targets}. "
                "Decláralas en cobra.mod o ajusta [project].required_targets en cobra.toml."
            )

        # Validar archivos por targets canónicos soportados
        for target in OFFICIAL_TARGETS:
            canonical_target = normalize_target_name(target)
            ruta = info_normalized.get(canonical_target)
            if not ruta:
                continue

            if not isinstance(ruta, str):
                errores.append(f"Ruta inválida para {canonical_target} en {modulo}")
                continue

            registro = backend_archivos.setdefault(canonical_target, set())
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
