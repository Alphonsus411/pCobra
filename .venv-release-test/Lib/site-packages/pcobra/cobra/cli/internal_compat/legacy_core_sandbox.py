"""Compatibilidad temporal para el namespace legacy ``core.sandbox``.

Este módulo encapsula todo el fallback legacy fuera del flujo principal de
servicios como ``run``. La ruta canónica contractual es
``pcobra.core.sandbox``.
"""

from __future__ import annotations

import importlib
import logging
import os
import warnings
from pathlib import Path
from types import ModuleType
from typing import Final

LEGACY_SANDBOX_COMPAT_FLAG: Final[str] = "PCOBRA_ENABLE_LEGACY_CORE_SANDBOX"
LEGACY_SANDBOX_RETIREMENT_DATE: Final[str] = "2026-12-31"

_logger = logging.getLogger(__name__)


def legacy_core_sandbox_compat_enabled() -> bool:
    raw = (os.environ.get(LEGACY_SANDBOX_COMPAT_FLAG, "") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _expected_legacy_target_path() -> Path:
    return Path(__file__).resolve().parents[3] / "core" / "sandbox.py"


def _validar_modulo_sandbox_legacy(module: ModuleType) -> None:
    module_file = getattr(module, "__file__", None)
    if not module_file:
        raise ImportError("El módulo legacy 'core.sandbox' no expone __file__")

    detected = Path(module_file).resolve()
    expected = _expected_legacy_target_path().resolve()
    if not detected.is_file() or detected != expected:
        raise ImportError(
            "El módulo legacy 'core.sandbox' no apunta al paquete esperado "
            f"('{expected}'). Ruta detectada: {detected}"
        )


def load_legacy_core_sandbox(*, canonical_error: ModuleNotFoundError) -> ModuleType:
    if not legacy_core_sandbox_compat_enabled():
        raise ImportError(
            "No se pudo importar 'pcobra.core.sandbox'. "
            "El fallback legacy 'core.sandbox' está deshabilitado por defecto. "
            f"Para transición controlada habilite {LEGACY_SANDBOX_COMPAT_FLAG}=1."
        ) from canonical_error

    try:
        module = importlib.import_module("core.sandbox")
    except ModuleNotFoundError:
        raise canonical_error

    _validar_modulo_sandbox_legacy(module)
    warnings.warn(
        "Compatibilidad legacy activa: 'core.sandbox' está deprecado y será retirado "
        f"el {LEGACY_SANDBOX_RETIREMENT_DATE}. Use 'pcobra.core.sandbox'.",
        DeprecationWarning,
        stacklevel=2,
    )
    _logger.warning(
        "Fallback legacy core.sandbox activado (retiro %s)",
        LEGACY_SANDBOX_RETIREMENT_DATE,
        extra={
            "event": "legacy_core_sandbox_fallback",
            "compatibility_flag": LEGACY_SANDBOX_COMPAT_FLAG,
            "retirement_date": LEGACY_SANDBOX_RETIREMENT_DATE,
        },
    )
    return module
