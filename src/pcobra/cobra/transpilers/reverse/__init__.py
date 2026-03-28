"""Componentes para convertir código de otros lenguajes a Cobra.

Este paquete registra únicamente transpiladores inversos de **entrada**.
No amplía el conjunto de targets oficiales de salida del proyecto.

El módulo realiza importaciones seguras de los distintos transpiladores. Si
alguno no puede cargarse por dependencias faltantes, simplemente se ignora para
no impedir el uso de los demás.
"""

import logging
import os
from importlib import import_module
from typing import Dict, List, Type

from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler
from pcobra.cobra.transpilers.reverse.policy import (
    REVERSE_SCOPE_CLASS_NAMES,
    REVERSE_SCOPE_LANGUAGES,
    REVERSE_SCOPE_MODULES,
    normalize_reverse_language,
)

try:  # pragma: no cover - dependencia opcional
    from pcobra.cobra.transpilers.reverse.tree_sitter_base import (
        TreeSitterReverseTranspiler,
    )
except ModuleNotFoundError as exc:  # pragma: no cover - sin tree_sitter
    _TREE_SITTER_IMPORT_ERROR = exc

    class TreeSitterReverseTranspiler(BaseReverseTranspiler):  # type: ignore
        """Stub cuando tree-sitter no está disponible."""

        def __init__(self, *args, **kwargs) -> None:  # noqa: D401
            raise ModuleNotFoundError(
                "tree_sitter es necesario para los transpiladores inversos"
            ) from _TREE_SITTER_IMPORT_ERROR


logger = logging.getLogger(__name__)

def _resolve_legacy_import_phase() -> int:
    raw_phase = os.environ.get("PCOBRA_LEGACY_IMPORT_PHASE", "1") or "1"
    try:
        phase = int(raw_phase)
    except (TypeError, ValueError):
        phase = 1
    if phase < 1:
        return 1
    if phase > 3:
        return 3
    return phase


_LEGACY_IMPORT_PHASE = _resolve_legacy_import_phase()
_ALLOW_INTERNAL_LEGACY_FALLBACKS = _LEGACY_IMPORT_PHASE <= 1 or (
    _LEGACY_IMPORT_PHASE == 2
    and (
        os.environ.get("PCOBRA_INTERNAL_REVERSE_LEGACY_FALLBACKS") == "1"
        or os.environ.get("PCOBRA_ENABLE_LEGACY_IMPORTS") == "1"
    )
)
_REGISTERED_REVERSE_CLASSES: Dict[str, Type[BaseReverseTranspiler]] = {}
_EXPORTED_CLASS_NAMES: List[str] = []


def _import_reverse_module(mod_name: str):
    """Importa un módulo reverse canónico con fallback legacy solo interno."""
    try:
        return import_module(mod_name)
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", None)
        if missing != mod_name or not _ALLOW_INTERNAL_LEGACY_FALLBACKS:
            raise

        legacy_mod = mod_name.replace("pcobra.cobra", "cobra", 1)
        logger.warning(
            "Compatibilidad legacy interna activada para reverse: %s -> %s. "
            "Migre el import a `pcobra.*` (retirada progresiva: fase 1 warning, fase 2 opt-in, fase 3 eliminación).",
            mod_name,
            legacy_mod,
        )
        return import_module(legacy_mod)


for language in REVERSE_SCOPE_LANGUAGES:
    mod_name = REVERSE_SCOPE_MODULES[language]
    class_name = REVERSE_SCOPE_CLASS_NAMES[language]

    try:
        module = _import_reverse_module(mod_name)
    except ModuleNotFoundError as exc:
        if getattr(exc, "name", None) == mod_name:
            logger.info("Transpilador no disponible: %s", mod_name)
        else:
            logger.warning(
                "Transpilador %s omitido por dependencia opcional faltante: %s",
                mod_name,
                exc,
            )
        continue
    except ImportError as exc:
        logger.warning(
            "Transpilador %s omitido por error de importación: %s",
            mod_name,
            exc,
        )
        continue

    try:
        cls = getattr(module, class_name)
    except AttributeError as exc:
        logger.warning(
            "Módulo reverse fuera de contrato esperado (%s no existe en %s): %s",
            class_name,
            mod_name,
            exc,
        )
        continue

    globals()[class_name] = cls
    _EXPORTED_CLASS_NAMES.append(class_name)

    canonical_language = normalize_reverse_language(
        getattr(cls, "LANGUAGE", language).lower(),
    )
    if canonical_language != language:
        logger.warning(
            "Transpilador reverse %s declara LANGUAGE=%s; se ignora porque el canónico esperado es %s",
            class_name,
            canonical_language,
            language,
        )
        continue

    _REGISTERED_REVERSE_CLASSES[language] = cls


TREE_SITTER_TRANSPILERS: List[Type[TreeSitterReverseTranspiler]] = [
    cls
    for cls in _REGISTERED_REVERSE_CLASSES.values()
    if issubclass(cls, TreeSitterReverseTranspiler)
]

CUSTOM_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    cls
    for cls in _REGISTERED_REVERSE_CLASSES.values()
    if cls not in TREE_SITTER_TRANSPILERS
]

INCOMPLETE_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    cls
    for cls in CUSTOM_TRANSPILERS
    if cls.__name__ not in {"ReverseFromPython", "ReverseFromJS", "ReverseFromJava"}
]

REGISTERED_REVERSE_TRANSPILERS: Dict[str, Type[BaseReverseTranspiler]] = {
    language: _REGISTERED_REVERSE_CLASSES[language]
    for language in REVERSE_SCOPE_LANGUAGES
    if language in _REGISTERED_REVERSE_CLASSES
}

__all__ = (
    ["BaseReverseTranspiler", "TreeSitterReverseTranspiler"]
    + _EXPORTED_CLASS_NAMES
    + ["REGISTERED_REVERSE_TRANSPILERS", "REVERSE_SCOPE_LANGUAGES"]
)
