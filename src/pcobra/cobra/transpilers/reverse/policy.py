"""Política de alcance para reverse transpilation.

Recorte activo:
- Solo se consideran lenguajes oficialmente mantenidos para reverse transpilation:
  Python, JavaScript y Java.
- Cualquier módulo fuera de este alcance no se debe cargar desde el registro
  principal ni exponer en la CLI.
"""

from typing import Dict, Final, Tuple

REVERSE_SCOPE_LANGUAGES: Final[Tuple[str, ...]] = ("python", "js", "java")

REVERSE_SCOPE_MODULES: Final[Dict[str, str]] = {
    "python": "pcobra.cobra.transpilers.reverse.from_python",
    "js": "pcobra.cobra.transpilers.reverse.from_js",
    "java": "pcobra.cobra.transpilers.reverse.from_java",
}
