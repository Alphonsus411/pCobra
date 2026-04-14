import os
import logging
from typing import Any, Dict

try:
    import tomllib  # Python ≥3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from pcobra.cobra.transpilers.target_utils import normalize_target_name
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

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

_toml_cache = None

STDLIB_CONTRACTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'stdlib_contract')
)

_stdlib_contract_cache: dict[str, Dict[str, Any]] | None = None


def _load_stdlib_contracts() -> dict[str, Dict[str, Any]]:
    """Carga manifiestos contractuales de ``stdlib_contract``."""
    global _stdlib_contract_cache
    if _stdlib_contract_cache is not None:
        return _stdlib_contract_cache

    loaded: dict[str, Dict[str, Any]] = {}
    if not os.path.isdir(STDLIB_CONTRACTS_DIR):
        _stdlib_contract_cache = loaded
        return loaded

    for entry in sorted(os.listdir(STDLIB_CONTRACTS_DIR)):
        contract_path = os.path.join(STDLIB_CONTRACTS_DIR, entry)
        if not os.path.isfile(contract_path):
            continue
        try:
            with open(contract_path, 'rb') as handle:
                parsed = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError):
            logger.warning('No se pudo cargar manifest contractual: %s', contract_path)
            continue
        if isinstance(parsed, dict):
            loaded[entry] = parsed

    _stdlib_contract_cache = loaded
    return loaded


def get_stdlib_contracts() -> Dict[str, Dict[str, Any]]:
    """Devuelve todos los manifiestos contractuales cargados."""
    return dict(_load_stdlib_contracts())


def get_stdlib_contract(module: str) -> Dict[str, Any]:
    """Devuelve el manifiesto contractual declarado para ``module``."""
    contracts = _load_stdlib_contracts()
    contract = contracts.get(module)
    if isinstance(contract, dict):
        return contract
    return {}


def resolve_backend_for_module(module: str, backend: str) -> str:
    """Resuelve backend efectivo por contrato sin exponer transpilers internos."""
    canonical_backend = normalize_target_name(backend)
    contract = get_stdlib_contract(module)
    if not contract:
        return canonical_backend

    preferred_backend = contract.get('backend_preferido')
    if not isinstance(preferred_backend, str):
        return canonical_backend
    preferred = normalize_target_name(preferred_backend)

    fallback = contract.get('fallback_permitido', [])
    if not isinstance(fallback, list):
        fallback = []
    allowed_fallbacks = {
        normalize_target_name(item)
        for item in fallback
        if isinstance(item, str)
    }

    if canonical_backend == preferred or canonical_backend in allowed_fallbacks:
        return canonical_backend
    return preferred

_RUNTIME_PATH_FORBIDDEN_SEGMENTS = (
    "core/nativos",
    "corelibs",
    "standard_library",
    "pcobra/core",
    "pcobra/corelibs",
    "pcobra/standard_library",
    "cobra/core",
    "cobra/corelibs",
    "cobra/standard_library",
    "nativos/",
)


def _is_runtime_path_forbidden(mapped_path: str) -> bool:
    """Indica si ``mapped_path`` intenta inyectar rutas de runtime reservadas."""
    canonical = mapped_path.replace("\\", "/").strip().lower()
    if not canonical:
        return False
    return any(segment in canonical for segment in _RUNTIME_PATH_FORBIDDEN_SEGMENTS)


def get_toml_map() -> Dict[str, Any]:
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


def get_mapped_path(module: str, backend: str) -> str:
    """Return the mapped path for *module* under canonical ``[modulos]`` config.

    Solo acepta nombres canónicos incluidos en ``OFFICIAL_TARGETS`` y resuelve
    exclusivamente desde ``cobra.toml`` usando la estructura
    ``[modulos."<module>"]``. Si no hay mapeo válido, devuelve ``module``.
    """
    canonical_backend = resolve_backend_for_module(module, backend)
    if canonical_backend not in OFFICIAL_TARGETS:
        return module

    mapa = get_toml_map()
    if not isinstance(mapa, dict):
        return module

    modulos = mapa.get("modulos", {})
    if not isinstance(modulos, dict):
        return module

    module_mapping = modulos.get(module, {})
    if not isinstance(module_mapping, dict):
        return module

    mapped = module_mapping.get(canonical_backend)
    if not isinstance(mapped, str):
        return module
    if _is_runtime_path_forbidden(mapped):
        logger.warning(
            "Mapping de módulo ignorado por política de runtime: módulo=%s backend=%s destino=%s",
            module,
            canonical_backend,
            mapped,
        )
        return module
    return mapped
