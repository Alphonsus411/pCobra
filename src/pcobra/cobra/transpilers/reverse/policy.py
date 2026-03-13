"""Política de alcance para reverse transpilation.

Recorte activo:
- Solo se consideran lenguajes oficialmente mantenidos para reverse transpilation:
  Python, JavaScript y Java.
- Cualquier módulo fuera de este alcance no se debe cargar desde el registro
  principal ni exponer en la CLI.
"""

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


def normalize_reverse_language(language: str) -> str:
    """Normaliza alias legacy de reverse transpilation al nombre canónico."""
    normalized = language.strip().lower()
    return REVERSE_SCOPE_ALIASES.get(normalized, normalized)
