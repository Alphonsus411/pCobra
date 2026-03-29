"""Paquete principal de Cobra."""

import importlib
import importlib.util
import logging
import os as _os
from pathlib import Path as _Path
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

_REPO_ROOT = _Path(__file__).resolve().parents[2]
_BIN_PATH = _REPO_ROOT / "scripts" / "bin"
if _BIN_PATH.is_dir():
    _current_path = _os.environ.get("PATH", "")
    if str(_BIN_PATH) not in _current_path.split(_os.pathsep):
        _os.environ["PATH"] = (
            f"{_BIN_PATH}{_os.pathsep}{_current_path}" if _current_path else str(_BIN_PATH)
        )

# Cargar primero los paquetes base para evitar errores de dependencias cruzadas
_submodules = ["cobra", "core", "cli", "ia", "jupyter_kernel", "gui", "lsp", "compiler"]

for pkg in _submodules:
    if importlib.util.find_spec(f".{pkg}", __name__) is None:
        logger.warning("Subm\u00f3dulo %s no encontrado, se omite su importaci\u00f3n", pkg)
        continue
    try:
        module = importlib.import_module(f".{pkg}", __name__)
        globals()[pkg] = module
        _sys.modules.setdefault(pkg, module)
    except ImportError as e:
        logger.warning("No se pudo importar %s: %s", pkg, e)
    except Exception as e:  # nosec B110
        logger.error("Error al importar %s", pkg, exc_info=True)
        raise

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


activar_aliases_legacy()
