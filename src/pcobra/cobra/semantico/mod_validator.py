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
import re
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

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.cli.utils.semver import es_version_valida
from pcobra.cobra.transpilers import module_map
from pcobra.cobra.transpilers.target_utils import (
    LEGACY_OR_AMBIGUOUS_TARGETS,
    normalize_target_name,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS

# Constantes
MAX_FILE_SIZE = 10_000_000  # 10MB
SCHEMA_PATH_V1 = os.path.join(os.path.dirname(__file__), "cobra_mod_schema.yaml")
SCHEMA_PATH_V2 = os.path.join(os.path.dirname(__file__), "cobra_mod_schema_v2.yaml")

logger = logging.getLogger(__name__)

DEFAULT_REQUIRED_TARGETS: tuple[str, ...] = TIER1_TARGETS
DEFAULT_REQUIRED_TARGETS_V2: tuple[str, ...] = PUBLIC_BACKENDS



def _official_targets_with_tier_text() -> str:
    tier_rows = [*(f"{target}=tier1" for target in TIER1_TARGETS), *(f"{target}=tier2" for target in TIER2_TARGETS)]
    return ", ".join(tier_rows)


def _allowed_targets_text(allowed_targets: tuple[str, ...]) -> str:
    if allowed_targets == PUBLIC_BACKENDS:
        return ", ".join(PUBLIC_BACKENDS)
    return _official_targets_with_tier_text()


# Verificar existencia del esquema y cargarlo
if not os.path.exists(SCHEMA_PATH_V1):
    raise FileNotFoundError(f"No se encuentra el archivo de esquema: {SCHEMA_PATH_V1}")
if not os.path.exists(SCHEMA_PATH_V2):
    raise FileNotFoundError(f"No se encuentra el archivo de esquema: {SCHEMA_PATH_V2}")

if yaml is None:
    logger.debug("PyYAML no está instalado; se omite la carga del esquema cobra_mod.")
    SCHEMA_V1: dict[str, Any] | None = None
    SCHEMA_V2: dict[str, Any] | None = None
else:
    try:
        with open(SCHEMA_PATH_V1, "r", encoding="utf-8") as f:
            SCHEMA_V1 = yaml.safe_load(f)
        with open(SCHEMA_PATH_V2, "r", encoding="utf-8") as f:
            SCHEMA_V2 = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:  # type: ignore[attr-defined]
        raise RuntimeError(f"Error al cargar el esquema: {e}") from None

# Alias para compatibilidad con tests existentes
SCHEMA = SCHEMA_V1


MIGRATION_WARNING = (
    "cobra.mod en esquema v1 está deprecado; migra a v2 usando solo claves públicas "
    f"({', '.join(PUBLIC_BACKENDS)})."
)


_VERSION_PREFIX = re.compile(r"^v?(\d+)")


def _extract_major_version(value: Any) -> int | None:
    if value is None:
        return None
    match = _VERSION_PREFIX.match(str(value).strip())
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _schema_flag_from_metadata(datos: Dict[str, Any]) -> int | None:
    raw_metadata = datos.get("metadata")
    if not isinstance(raw_metadata, dict):
        return None

    for key in ("schema_version", "mod_schema_version", "version"):
        major = _extract_major_version(raw_metadata.get(key))
        if major is not None:
            return major
    return None


def _use_v2_for_module(datos: Dict[str, Any], modulo: str, info: Dict[str, Any]) -> bool:
    metadata_version = _schema_flag_from_metadata(datos)
    if metadata_version is not None:
        return metadata_version >= 2
    return (_extract_major_version(info.get("version")) or 1) >= 2


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



def _required_targets_from_policy(allowed_targets: tuple[str, ...], default_required: tuple[str, ...]) -> tuple[str, ...]:
    """Obtiene targets requeridos desde ``cobra.toml`` según política de proyecto."""
    toml_map = module_map.get_toml_map()
    if not isinstance(toml_map, dict):
        return default_required

    project_cfg = toml_map.get("project")
    if not isinstance(project_cfg, dict):
        project_cfg = toml_map.get("proyecto")

    raw_targets = None
    if isinstance(project_cfg, dict):
        raw_targets = project_cfg.get("required_targets")
        if raw_targets is None:
            raw_targets = project_cfg.get("targets_requeridos")

    if not raw_targets:
        return default_required

    if not isinstance(raw_targets, list):
        raise ValueError(
            "La política [project].required_targets en cobra.toml debe ser una lista de strings canónicos. "
            f"Valor recibido: {type(raw_targets).__name__}. "
            f"Targets válidos: {_allowed_targets_text(allowed_targets)}"
        )

    normalized: list[str] = []
    for target in raw_targets:
        if not isinstance(target, str):
            raise ValueError(
                "La política [project].required_targets en cobra.toml debe contener solo strings. "
                f"Elemento inválido: {target!r}. "
                f"Targets válidos: {_allowed_targets_text(allowed_targets)}"
            )
        if target.strip().lower() in LEGACY_OR_AMBIGUOUS_TARGETS:
            raise ValueError(
                "La política [project].required_targets no acepta aliases legacy/ambiguos. "
                f"Valor inválido: {target}. "
                f"Targets válidos: {_allowed_targets_text(allowed_targets)}"
            )
        canonical = normalize_target_name(target)
        if canonical not in allowed_targets:
            raise ValueError(
                "La política [project].required_targets contiene un target no permitido: "
                f"{target}. Targets válidos: {_allowed_targets_text(allowed_targets)}"
            )
        if canonical not in normalized:
            normalized.append(canonical)

    return tuple(normalized) if normalized else default_required


def _warn_if_tier2_used_as_optional_mapping(modulo: str, info: dict[str, Any]) -> None:
    """Emite trazas informativas cuando un módulo declara mappings Tier 2 opcionales."""
    tier2_present = [target for target in TIER2_TARGETS if info.get(target)]
    if tier2_present:
        logger.debug(
            "El módulo %s declara targets Tier 2 opcionales: %s",
            modulo,
            ", ".join(tier2_present),
        )


def _find_noncanonical_backend_keys(info: dict[str, Any], allowed_targets: tuple[str, ...]) -> list[str]:
    """Devuelve claves backend no canónicas presentes en un mapping de módulo."""
    ignored_keys = {"version"}
    noncanonical: list[str] = []
    for key in info:
        if key in ignored_keys:
            continue
        if key not in allowed_targets:
            noncanonical.append(key)
    return sorted(noncanonical)


def _schema_for_module(datos: Dict[str, Any], modulo: str, info: Dict[str, Any]) -> tuple[dict[str, Any] | None, tuple[str, ...], tuple[str, ...], str]:
    if _use_v2_for_module(datos, modulo, info):
        return SCHEMA_V2, PUBLIC_BACKENDS, DEFAULT_REQUIRED_TARGETS_V2, "v2"
    return SCHEMA_V1, OFFICIAL_TARGETS, DEFAULT_REQUIRED_TARGETS, "v1"


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

    errores: list[str] = []
    backend_archivos: dict[str, set[str]] = {
        target: set() for target in OFFICIAL_TARGETS
    }
    required_targets_v1 = _required_targets_from_policy(OFFICIAL_TARGETS, DEFAULT_REQUIRED_TARGETS)
    required_targets_v2 = _required_targets_from_policy(PUBLIC_BACKENDS, DEFAULT_REQUIRED_TARGETS_V2)
    warned_v1 = False

    for modulo, info in datos.items():
        if modulo in {"lock", "metadata"}:
            continue

        if not isinstance(info, dict):
            errores.append(f"Entrada inválida para {modulo}")
            continue

        info_normalized = dict(info)

        schema, allowed_targets, _, schema_name = _schema_for_module(datos, modulo, info_normalized)

        if schema_name == "v1" and not warned_v1:
            logger.warning(MIGRATION_WARNING)
            warned_v1 = True

        if schema is None or validate is None or ValidationError is None:
            logger.debug(
                "Se omite la validación por esquema de cobra.mod por dependencias opcionales faltantes.",
            )
        else:
            try:
                validate(instance={modulo: info_normalized}, schema=schema)
            except ValidationError as e:
                errores.append(f"{modulo}: {e.message}")
                continue

        _warn_if_tier2_used_as_optional_mapping(modulo, info_normalized)

        invalid_backend_keys = _find_noncanonical_backend_keys(info_normalized, allowed_targets)
        if invalid_backend_keys:
            errores.append(
                "Backends no canónicos en {modulo}: {targets}. "
                "Usa únicamente: {allowed}".format(
                    modulo=modulo,
                    targets=", ".join(invalid_backend_keys),
                    allowed=", ".join(allowed_targets),
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

        required_targets = required_targets_v2 if schema_name == "v2" else required_targets_v1
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
        for target in allowed_targets:
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
