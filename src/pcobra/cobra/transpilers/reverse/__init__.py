"""Componentes para convertir código de otros lenguajes a Cobra.

El módulo realiza importaciones seguras de los distintos transpiladores. Si
alguno no puede cargarse por dependencias faltantes, simplemente se ignora para
no impedir el uso de los demás.
"""
import logging
from importlib import import_module
from typing import List, Type

from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler
try:  # pragma: no cover - dependencia opcional
    from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler
except ModuleNotFoundError as exc:  # pragma: no cover - sin tree_sitter
    _TREE_SITTER_IMPORT_ERROR = exc

    class TreeSitterReverseTranspiler(BaseReverseTranspiler):  # type: ignore
        """Stub cuando tree-sitter no está disponible."""

        def __init__(self, *args, **kwargs) -> None:  # noqa: D401
            raise ModuleNotFoundError(
                "tree_sitter es necesario para los transpiladores inversos"
            ) from _TREE_SITTER_IMPORT_ERROR

# Lista de módulos a intentar importar
logger = logging.getLogger(__name__)

_MODULOS = [
    "pcobra.cobra.transpilers.reverse.from_c",
    "pcobra.cobra.transpilers.reverse.from_cpp",
    "pcobra.cobra.transpilers.reverse.from_js",
    "pcobra.cobra.transpilers.reverse.from_java",
    "pcobra.cobra.transpilers.reverse.from_go",
    "pcobra.cobra.transpilers.reverse.from_julia",
    "pcobra.cobra.transpilers.reverse.from_php",
    "pcobra.cobra.transpilers.reverse.from_perl",
    "pcobra.cobra.transpilers.reverse.from_r",
    "pcobra.cobra.transpilers.reverse.from_ruby",
    "pcobra.cobra.transpilers.reverse.from_rust",
    "pcobra.cobra.transpilers.reverse.from_swift",
    "pcobra.cobra.transpilers.reverse.from_kotlin",
    "pcobra.cobra.transpilers.reverse.from_fortran",
    "pcobra.cobra.transpilers.reverse.from_python",
    "pcobra.cobra.transpilers.reverse.from_asm",
    "pcobra.cobra.transpilers.reverse.from_cobol",
    "pcobra.cobra.transpilers.reverse.from_latex",
    "pcobra.cobra.transpilers.reverse.from_matlab",
    "pcobra.cobra.transpilers.reverse.from_mojo",
    "pcobra.cobra.transpilers.reverse.from_pascal",
    "pcobra.cobra.transpilers.reverse.from_visualbasic",
    "pcobra.cobra.transpilers.reverse.from_wasm",
    "pcobra.cobra.reverse",
]

_LEGACY_FALLBACKS = {
    mod_name: mod_name.replace("pcobra.cobra", "cobra", 1)
    for mod_name in _MODULOS
}

# Importaciones seguras -------------------------------------------------
for mod_name in list(_MODULOS):
    try:
        module = import_module(mod_name)
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", None)
        if missing == mod_name:
            legacy_mod = _LEGACY_FALLBACKS.get(mod_name)
            if legacy_mod is None:
                _MODULOS.remove(mod_name)
                logger.debug("Transpilador omitido: %s (sin fallback)", mod_name)
                continue
            try:
                module = import_module(legacy_mod)
                logger.debug(
                    "Transpilador cargado vía fallback legacy: %s -> %s",
                    mod_name,
                    legacy_mod,
                )
            except ModuleNotFoundError as legacy_exc:
                if getattr(legacy_exc, "name", None) == legacy_mod:
                    logger.info(
                        "Transpilador no disponible: %s (también falló fallback %s)",
                        mod_name,
                        legacy_mod,
                    )
                else:
                    logger.warning(
                        "Transpilador %s omitido por dependencia opcional faltante: %s",
                        mod_name,
                        legacy_exc,
                    )
                _MODULOS.remove(mod_name)
                continue
        else:
            logger.warning(
                "Transpilador %s omitido por dependencia opcional faltante: %s",
                mod_name,
                exc,
            )
            _MODULOS.remove(mod_name)
            continue
    except ImportError as exc:
        logger.warning(
            "Transpilador %s omitido por error de importación: %s",
            mod_name,
            exc,
        )
        _MODULOS.remove(mod_name)
        continue

    try:
        for attr in dir(module):
            if attr.startswith("ReverseFrom"):
                globals()[attr] = getattr(module, attr)
    except AttributeError as exc:
        logger.warning(
            "Error inspeccionando %s para registrar transpiladores: %s",
            mod_name,
            exc,
        )
        _MODULOS.remove(mod_name)

# Clasificación de transpiladores disponibles ---------------------------
TREE_SITTER_TRANSPILERS: List[Type[TreeSitterReverseTranspiler]] = [
    cls
    for cls_name, cls in globals().items()
    if cls_name.startswith("ReverseFrom") and issubclass(cls, TreeSitterReverseTranspiler)
]

CUSTOM_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    cls
    for cls_name, cls in globals().items()
    if cls_name.startswith("ReverseFrom") and issubclass(cls, BaseReverseTranspiler)
    and cls not in TREE_SITTER_TRANSPILERS
]

INCOMPLETE_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    cls
    for cls in CUSTOM_TRANSPILERS
    if cls.__name__ not in {"ReverseFromPython", "ReverseFromJS", "ReverseFromJava"}
]

__all__ = ["BaseReverseTranspiler", "TreeSitterReverseTranspiler"] + [
    cls.__name__ for cls in TREE_SITTER_TRANSPILERS + CUSTOM_TRANSPILERS
]
