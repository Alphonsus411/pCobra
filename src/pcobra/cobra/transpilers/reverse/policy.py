"""Política de alcance para reverse transpilation.

Recorte activo:
- Solo se consideran lenguajes oficialmente mantenidos para reverse transpilation:
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


REVERSE_SCOPE_ALIASES: Final[Dict[str, str]] = {
    "js": "javascript",
}


def normalize_reverse_language(language: str, *, allow_legacy_aliases: bool = False) -> str:
    """Normaliza el lenguaje reverse al nombre canónico usado internamente.

    Por defecto NO resuelve aliases legacy para evitar aceptarlos en la
    validación directa de argumentos CLI.
    """
    normalized = language.strip().lower()
    if allow_legacy_aliases:
        return REVERSE_SCOPE_ALIASES.get(normalized, normalized)
    return normalized


def parse_reverse_source_language(value: str) -> str:
    """Valida un origen reverse CLI aceptando solo nombres canónicos."""
    canonical = normalize_reverse_language(value)
    if canonical not in REVERSE_SCOPE_LANGUAGES:
        raise ArgumentTypeError(
            "Lenguaje de origen no soportado para transpilación inversa: "
            "'{value}'. Usa uno canónico: {supported}.".format(
                value=value.strip(),
                supported=", ".join(REVERSE_SCOPE_LANGUAGES),
            )
        )
    return canonical
