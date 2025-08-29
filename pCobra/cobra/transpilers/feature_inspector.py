from __future__ import annotations

"""Herramientas para inspeccionar las características soportadas por los transpiladores.

Este módulo analiza los archivos `to_*.py` de los distintos transpiladores
para extraer qué nodos del AST cuentan con implementación.
"""

from pathlib import Path
import re
from typing import Dict, List

# Carpeta donde se encuentran los transpiladores individuales
BASE_DIR = Path(__file__).resolve().parent / "transpiler"

# Archivos a inspeccionar y su nombre de lenguaje asociado
TRANSPILERS = {
    "Python": "to_python.py",
    "JavaScript": "to_js.py",
    "C++": "to_cpp.py",
    "Rust": "to_rust.py",
    "Go": "to_go.py",
    "Java": "to_java.py",
}

# Patrones para detectar características registradas en los transpiladores
# 1) Asignaciones como `TranspiladorX.visit_algo = ...`
_ASSIGN_PATTERN = re.compile(r"visit_([a-zA-Z_]+)\s*=")
# 2) Entradas en diccionarios como `'algo': visit_algo`
_DICT_PATTERN = re.compile(r"['\"]([a-zA-Z_]+)['\"]\s*:\s*visit_[a-zA-Z_]+")


def extract_features() -> Dict[str, List[str]]:
    """Devuelve un mapeo de lenguaje a la lista de características soportadas."""
    features: Dict[str, List[str]] = {}
    for language, filename in TRANSPILERS.items():
        path = BASE_DIR / filename
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
