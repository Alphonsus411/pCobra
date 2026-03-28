#!/usr/bin/env python3
"""Gate CI: valida que la matriz pública de compatibilidad de librerías no se degrade."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.transpilers.library_compatibility import LIBRARY_AREAS, LIBRARY_COMPATIBILITY
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

DOC_PATH = Path("docs/library_compatibility_matrix.md")


def main() -> int:
    if not DOC_PATH.exists():
        raise SystemExit(f"Falta documento requerido: {DOC_PATH}")

    content = DOC_PATH.read_text(encoding="utf-8")

    missing_targets = [target for target in OFFICIAL_TARGETS if f"`{target}`" not in content]
    if missing_targets:
        raise SystemExit(f"Targets faltantes en documentación: {missing_targets}")

    missing_areas = [area for area in LIBRARY_AREAS if area not in content]
    if missing_areas:
        raise SystemExit(f"Áreas faltantes en documentación: {missing_areas}")

    for backend in OFFICIAL_TARGETS:
        for area in LIBRARY_AREAS:
            record = LIBRARY_COMPATIBILITY[backend][area]
            if not record.incompatibility.strip() or not record.workaround.strip():
                raise SystemExit(
                    f"Registro incompleto para backend={backend}, area={area}. "
                    "Debe incluir incompatibilidad y workaround."
                )

    print("Matriz de compatibilidad de librerías validada correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
