from __future__ import annotations

"""Herramientas para inspeccionar las características soportadas por los transpiladores.

Este módulo analiza los archivos `to_*.py` de los distintos transpiladores
para extraer qué nodos del AST cuentan con implementación.
"""

from pathlib import Path
import re
from typing import Dict, List

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name, target_label

# Carpeta donde se encuentran los transpiladores individuales
BASE_DIR = Path(__file__).resolve().parent / "transpiler"

_TRANSPILER_FILE_BY_TARGET = {
    "javascript": "to_js.py",
    "cpp": "to_cpp.py",
    "asm": "to_asm.py",
}


def _resolve_transpiler_file(target: str) -> str:
    canonical = normalize_target_name(target, allow_legacy_aliases=True)
    return _TRANSPILER_FILE_BY_TARGET.get(canonical, f"to_{canonical}.py")


TRANSPILERS: Dict[str, str] = {
    normalize_target_name(target, allow_legacy_aliases=True): _resolve_transpiler_file(target) for target in OFFICIAL_TARGETS
}

# Patrones para detectar características registradas en los transpiladores
# 1) Asignaciones como `TranspiladorX.visit_algo = ...`
_ASSIGN_PATTERN = re.compile(r"visit_([a-zA-Z_]+)\s*=")
# 2) Entradas en diccionarios como `'algo': visit_algo`
_DICT_PATTERN = re.compile(r"['\"]([a-zA-Z_]+)['\"]\s*:\s*visit_[a-zA-Z_]+")


def extract_features() -> Dict[str, List[str]]:
    """Devuelve un mapeo de lenguaje a la lista de características soportadas."""
    features: Dict[str, List[str]] = {}
    for canonical, transpiler_file in TRANSPILERS.items():
        language = target_label(canonical)
        path = BASE_DIR / transpiler_file
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        found = set(_ASSIGN_PATTERN.findall(content))
        found.update(_DICT_PATTERN.findall(content))
        features[language] = sorted(found)
    return features


if __name__ == "__main__":
    import json

    print(json.dumps(extract_features(), indent=2, ensure_ascii=False))
