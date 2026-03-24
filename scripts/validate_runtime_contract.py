#!/usr/bin/env python3
"""Valida que la matriz pública de runtime no contradiga la matriz contractual."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pcobra.cobra.cli.target_policies import (
    ADVANCED_HOLOBIT_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_STANDARD_LIBRARY_TARGETS,
    SDK_COMPATIBLE_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
    validate_runtime_support_contract,
)
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    BACKEND_FEATURE_GAPS,
    CONTRACT_FEATURES,
)


def main() -> int:
    validate_runtime_support_contract()

    for backend in OFFICIAL_RUNTIME_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        for feature in ("corelibs", "standard_library"):
            if contract[feature] == "none":
                raise RuntimeError(
                    f"{backend} figura como runtime oficial, pero {feature}={contract[feature]}"
                )

    for backend in ADVANCED_HOLOBIT_RUNTIME_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        for feature in ("holobit", "proyectar", "transformar", "graficar"):
            if contract[feature] == "none":
                raise RuntimeError(
                    f"{backend} figura con soporte Holobit avanzado, pero {feature}={contract[feature]}"
                )

    for backend in SDK_COMPATIBLE_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        for feature in (
            "holobit",
            "proyectar",
            "transformar",
            "graficar",
            "corelibs",
            "standard_library",
        ):
            if contract[feature] != "full":
                raise RuntimeError(
                    f"{backend} figura con compatibilidad SDK completa, pero {feature}={contract[feature]}"
                )

    for backend in OFFICIAL_RUNTIME_TARGETS:
        for feature in CONTRACT_FEATURES:
            level = BACKEND_COMPATIBILITY[backend][feature]
            gaps = BACKEND_FEATURE_GAPS[backend][feature]
            if level == "full" and gaps:
                raise RuntimeError(
                    f"{backend}.{feature} está en full pero declara gaps: {gaps}"
                )
            if level == "partial" and not gaps:
                raise RuntimeError(
                    f"{backend}.{feature} está en partial pero no declara gaps explícitos"
                )

    print("✅ Runtime contract validation: OK")
    print(f"   Runtime oficial: {', '.join(OFFICIAL_RUNTIME_TARGETS)}")
    print(f"   Verificación ejecutable: {', '.join(VERIFICATION_EXECUTABLE_TARGETS)}")
    print(
        "   Runtime oficial con corelibs/standard_library mantenidos: "
        f"{', '.join(OFFICIAL_STANDARD_LIBRARY_TARGETS)}"
    )
    print(
        "   Adaptador Holobit mantenido: "
        f"{', '.join(ADVANCED_HOLOBIT_RUNTIME_TARGETS)}"
    )
    print(f"   Compatibilidad SDK completa: {', '.join(SDK_COMPATIBLE_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
