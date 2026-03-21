import os
import logging
from typing import Any, Dict

try:  # pragma: no cover - dependencia opcional
    import yaml
except ModuleNotFoundError:  # pragma: no cover - entornos sin PyYAML
    yaml = None  # type: ignore[assignment]

try:
    import tomllib  # Python ≥3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name

LEGACY_MODULE_MAP_KEYS = {
    "javascript": ("js",),
    "asm": ("ensamblador",),
}

logger = logging.getLogger(__name__)

MODULE_MAP_PATH = os.environ.get(
    'COBRA_MODULE_MAP',
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'cobra.mod')
    ),
)

COBRA_TOML_PATH = os.environ.get(
    'COBRA_TOML',
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'cobra.toml')
    ),
)

_cache = None
_toml_cache = None


def _load_toml_file(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, 'rb') as f:
        return tomllib.load(f) or {}

def get_map() -> Dict[str, Any]:
    """Carga el mapa de módulos soportados desde ``cobra.mod``.

    Soporta formato TOML (preferido) y YAML legacy como compatibilidad.
    """
    global _cache
    if _cache is None:
        try:
            if os.path.exists(MODULE_MAP_PATH):
                if MODULE_MAP_PATH.endswith('.toml') or MODULE_MAP_PATH.endswith('.mod'):
                    data = _load_toml_file(MODULE_MAP_PATH)
                elif yaml is not None:
                    with open(MODULE_MAP_PATH, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f) or {}
                else:
                    logger.debug(
                        "PyYAML no está instalado; se devuelve un mapa de módulos vacío.",
                    )
                    data = {}
            else:
                data = {}
            _cache = data
        except (tomllib.TOMLDecodeError, OSError) as e:
            logger.error(f"Error al cargar el archivo de mapeo (TOML): {e}")
            return {}
        except Exception as e:  # pragma: no cover - compatibilidad YAML opcional
            if yaml is not None and isinstance(e, yaml.YAMLError):  # type: ignore[attr-defined]
                logger.error(f"Error al cargar el archivo de mapeo (YAML): {e}")
                return {}
            logger.error(f"Error al cargar el archivo de mapeo: {e}")
            return {}
    return _cache


def get_toml_map():
    """Devuelve la configuración del archivo ``cobra.toml``."""
    global _toml_cache
    if _toml_cache is None:
        try:
            if os.path.exists(COBRA_TOML_PATH):
                with open(COBRA_TOML_PATH, 'rb') as f:
                    data = tomllib.load(f) or {}
            else:
                data = {}
            _toml_cache = data
        except (tomllib.TOMLDecodeError, OSError) as e:
            logger.error(f"Error al cargar cobra.toml: {e}")
            _toml_cache = {}
    return _toml_cache


def _find_legacy_module_map_key(module_mapping: dict[str, Any], backend: str) -> str | None:
    """Detecta aliases legacy configurados para un backend canónico."""
    for legacy_key in LEGACY_MODULE_MAP_KEYS.get(backend, ()):  # pragma: no branch - tabla pequeña
        if legacy_key in module_mapping:
            return legacy_key
    return None


def get_mapped_path(module: str, backend: str) -> str:
    """Return the path for *module* mapped for the given *backend*.

    Resuelve únicamente con nombres canónicos oficiales. Si no hay mapeo,
    devuelve ``module``. Si la configuración usa aliases legacy retirados para
    el backend solicitado, falla con un error accionable.
    """
    canonical_backend = normalize_target_name(backend)
    if canonical_backend not in OFFICIAL_TARGETS:
        return module
    mapa = get_toml_map()
    modulos = mapa.get("modulos", {}) if isinstance(mapa, dict) else {}

    if isinstance(modulos, dict) and isinstance(modulos.get(module), dict):
        module_mapping = dict(modulos.get(module, {}))
    else:
        # Compatibilidad con formatos legacy donde el módulo está en la raíz.
        root_mapping = mapa.get(module, {}) if isinstance(mapa, dict) else {}
        module_mapping = dict(root_mapping) if isinstance(root_mapping, dict) else {}

    # Fallback/merge con cobra.mod (TOML/YAML legacy).
    mapa_mod = get_map()
    modulos_mod = mapa_mod.get("modulos", {}) if isinstance(mapa_mod, dict) else {}
    if isinstance(modulos_mod, dict) and isinstance(modulos_mod.get(module), dict):
        module_mapping = {**modulos_mod.get(module, {}), **module_mapping}
    elif isinstance(mapa_mod, dict) and isinstance(mapa_mod.get(module), dict):
        module_mapping = {**mapa_mod.get(module, {}), **module_mapping}

    if not isinstance(module_mapping, dict) or not module_mapping:
        return module

    mapped = module_mapping.get(canonical_backend)
    if isinstance(mapped, str):
        return mapped

    legacy_key = _find_legacy_module_map_key(module_mapping, canonical_backend)
    if legacy_key is not None:
        raise ValueError(
            "El módulo "
            f"{module} usa la clave legacy '{legacy_key}' en cobra.mod/cobra.toml; "
            f"renómbrala a '{canonical_backend}'."
        )

    return module
