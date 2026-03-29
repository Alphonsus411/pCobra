"""Paquete principal de Cobra."""

import importlib
import importlib.util
import logging
import os as _os
import sys as _sys
import warnings as _warnings
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

_LEGACY_IMPORT_PHASE_ENV = "PCOBRA_LEGACY_IMPORT_PHASE"
_LEGACY_IMPORT_OPT_IN_ENV = "PCOBRA_ENABLE_LEGACY_IMPORTS"
_LEGACY_IMPORT_PHASE_DEFAULT = 1
_LEGACY_IMPORT_SCHEDULE = {
    1: "Fase 1 (warning explícito): activa en 2.3.x.",
    2: "Fase 2 (opt-in): prevista para 2.4.0, requiere flag/env.",
    3: "Fase 3 (eliminación): prevista para 3.0.0.",
}
LEGACY_IMPORT_ALIAS_INVENTORY: Dict[str, str] = {
    "cobra": "pcobra.cobra",
    "cobra.core": "pcobra.cobra.core",
    "core": "pcobra.core",
}

# Submódulos públicos expuestos de forma perezosa (sin import-time eager loading).
_LAZY_SUBMODULES = {
    "cobra",
    "core",
    "cli",
    "ia",
    "jupyter_kernel",
    "gui",
    "lsp",
    "compiler",
}

__all__ = sorted(_LAZY_SUBMODULES) + ["activar_aliases_legacy", "LEGACY_IMPORT_ALIAS_INVENTORY"]


def _resolve_legacy_import_policy() -> Tuple[int, bool]:
    """Resuelve fase de deprecación de imports legacy y si están habilitados."""

    raw_phase = _os.environ.get(_LEGACY_IMPORT_PHASE_ENV, str(_LEGACY_IMPORT_PHASE_DEFAULT))
    try:
        phase = int(raw_phase)
    except ValueError:
        logger.warning(
            "Valor inválido para %s=%r; se usa fase %s",
            _LEGACY_IMPORT_PHASE_ENV,
            raw_phase,
            _LEGACY_IMPORT_PHASE_DEFAULT,
        )
        phase = _LEGACY_IMPORT_PHASE_DEFAULT

    phase = min(max(phase, 1), 3)
    opt_in = _os.environ.get(_LEGACY_IMPORT_OPT_IN_ENV) == "1"
    enabled = phase == 1 or (phase == 2 and opt_in)
    return phase, enabled


def _legacy_migration_message(phase: int) -> str:
    """Mensaje estándar de migración para imports heredados."""

    return (
        "Compatibilidad de imports legacy activa para módulos heredados "
        f"({', '.join(sorted(LEGACY_IMPORT_ALIAS_INVENTORY.keys()))}). "
        "Migre a rutas canónicas `pcobra.*` (por ejemplo `pcobra.cobra` y `pcobra.core`). "
        f"Calendario de retirada: {_LEGACY_IMPORT_SCHEDULE[1]} {_LEGACY_IMPORT_SCHEDULE[2]} {_LEGACY_IMPORT_SCHEDULE[3]} "
        f"Fase actual: {phase}."
    )


def _load_submodule(name: str):
    """Carga un submódulo público de ``pcobra`` bajo demanda."""

    if name not in _LAZY_SUBMODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    spec = importlib.util.find_spec(f".{name}", __name__)
    if spec is None:
        raise AttributeError(
            f"El submódulo público {name!r} no está disponible en {__name__!r}"
        )

    try:
        module = importlib.import_module(f".{name}", __name__)
    except ImportError as exc:
        logger.warning("No se pudo importar %s: %s", name, exc)
        raise

    globals()[name] = module
    return module


def __getattr__(name: str):
    """Expone submódulos públicos de forma lazy para evitar imports ansiosos."""

    if name in _LAZY_SUBMODULES:
        return _load_submodule(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Incluye la API pública lazy en ``dir(pcobra)``."""

    return sorted(set(globals()) | set(__all__))


# Registrar alias de compatibilidad para importaciones absolutas heredadas
def _registrar_alias_legacy() -> None:
    """Sincroniza los nombres históricos ``cobra`` y ``core`` con ``pcobra``."""
    phase, enabled = _resolve_legacy_import_policy()
    if phase >= 3:
        logger.warning(
            "Compatibilidad de imports legacy eliminada (fase 3). Use rutas `pcobra.*`."
        )
        return
    if not enabled:
        logger.warning(
            "Compatibilidad de imports legacy deshabilitada en fase %s. "
            "Use `--legacy-imports` o %s=1 temporalmente y migre a `pcobra.*`.",
            phase,
            _LEGACY_IMPORT_OPT_IN_ENV,
        )
        return

    cobra_spec = importlib.util.find_spec("pcobra.cobra")
    if cobra_spec is None:
        return

    cobra_pkg = importlib.import_module("pcobra.cobra")
    _sys.modules.setdefault("cobra", cobra_pkg)

    core_spec = importlib.util.find_spec("pcobra.cobra.core")
    if core_spec is not None:
        core_pkg = importlib.import_module("pcobra.cobra.core")
        _sys.modules.setdefault("cobra.core", core_pkg)
        for nombre, modulo in list(_sys.modules.items()):
            if nombre.startswith("pcobra.cobra.core."):
                alias = "cobra.core." + nombre.split("pcobra.cobra.core.", 1)[1]
                _sys.modules.setdefault(alias, modulo)

    legacy_core_spec = importlib.util.find_spec("pcobra.core")
    if legacy_core_spec is None:
        return

    legacy_core = importlib.import_module("pcobra.core")
    _sys.modules.setdefault("core", legacy_core)
    for nombre, modulo in list(_sys.modules.items()):
        if nombre.startswith("pcobra.core."):
            alias = "core." + nombre.split("pcobra.core.", 1)[1]
            _sys.modules.setdefault(alias, modulo)

    _warnings.warn(
        _legacy_migration_message(phase),
        DeprecationWarning,
        stacklevel=2,
    )
    logger.warning(_legacy_migration_message(phase))


def activar_aliases_legacy() -> None:
    """API pública e idempotente para habilitar alias legacy en runtime."""

    _registrar_alias_legacy()
