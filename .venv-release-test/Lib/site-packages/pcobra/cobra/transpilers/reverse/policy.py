"""Política de alcance para reverse transpilation.

Este módulo define únicamente **orígenes reverse de entrada** para
``cobra transpilar-inverso``. No describe targets oficiales de salida ni amplía
el set oficial de backends públicos.

Recorte activo:
- Solo se consideran lenguajes oficialmente mantenidos como origen reverse de entrada:
  Python, JavaScript y Java.
- Cualquier módulo fuera de este alcance no se debe cargar desde el registro
  principal ni exponer en la CLI.
"""

from argparse import ArgumentTypeError
from typing import Dict, Final, Tuple

REVERSE_SCOPE_LANGUAGES: Final[Tuple[str, ...]] = ("python", "javascript", "java")

REVERSE_SCOPE_MODULES: Final[Dict[str, str]] = {
    "python": "pcobra.cobra.transpilers.reverse.from_python",
    "javascript": "pcobra.cobra.transpilers.reverse.from_js",
    "java": "pcobra.cobra.transpilers.reverse.from_java",
}

REVERSE_SCOPE_CLASS_NAMES: Final[Dict[str, str]] = {
    "python": "ReverseFromPython",
    "javascript": "ReverseFromJS",
    "java": "ReverseFromJava",
}


def normalize_reverse_language(language: str) -> str:
    """Normaliza un origen reverse de entrada al nombre canónico interno."""
    return language.strip().lower()


def parse_reverse_source_language(value: str) -> str:
    """Valida un origen reverse CLI aceptando solo nombres canónicos de entrada."""
    canonical = normalize_reverse_language(value)
    if canonical not in REVERSE_SCOPE_LANGUAGES:
        raise ArgumentTypeError(
            "Lenguaje de origen no soportado para transpilación inversa: "
            "'{value}'. Este comando solo acepta orígenes reverse de entrada: {supported}.".format(
                value=value.strip(),
                supported=", ".join(REVERSE_SCOPE_LANGUAGES),
            )
        )
    return canonical
