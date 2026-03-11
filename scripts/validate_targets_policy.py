#!/usr/bin/env python3
"""Valida que la documentación principal no enumere lenguajes fuera de política."""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOC_FILES = (
    "README.md",
    "docs/README.en.md",
    "docs/lenguajes.rst",
    "docs/lenguajes_soportados.rst",
    "docs/frontend/backends.rst",
    "docs/frontend/index.rst",
    "docs/frontend/arquitectura.rst",
    "docs/frontend/avances.rst",
    "docs/frontend/caracteristicas.rst",
    "docs/frontend/optimizaciones.rst",
    "docs/frontend/sintaxis.rst",
    "docs/frontend/ejemplos.rst",
    "docs/MANUAL_COBRA.md",
    "docs/MANUAL_COBRA.rst",
    "docs/arquitectura_parser_transpiladores.md",
)

# Lenguajes que NO deben aparecer en la documentación principal como targets.
FORBIDDEN_TERMS = (
    "cobol",
    "ruby",
    "kotlin",
    "swift",
    "typescript",
    "php",
    "perl",
    "pascal",
    "fortran",
    "visualbasic",
    "matlab",
    "mojo",
    "julia",
    "latex",
)

pattern = re.compile(r"\\b(" + "|".join(re.escape(t) for t in FORBIDDEN_TERMS) + r")\\b", re.IGNORECASE)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for rel in DOC_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"Archivo de documentación no encontrado: {rel}")
            continue

        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = pattern.search(line)
            if match:
                errors.append(
                    f"{rel}:{line_no}: lenguaje fuera de política detectado -> '{match.group(1)}'"
                )

    if errors:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print("✅ Validación de política de targets: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
