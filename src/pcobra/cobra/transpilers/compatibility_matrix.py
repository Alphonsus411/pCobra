"""Matriz mínima de compatibilidad de transpiladores por tier.

Esta matriz documenta qué garantías ofrece cada backend para:
- primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`)
- imports base de runtime (`corelibs`, `standard_library`)

Niveles:
- ``full``: soportado con aserciones estrictas (símbolos/hooks/imports esperados).
- ``partial``: soporte limitado validado por fallback explícito y no rotura de generación.
- ``none``: no garantizado por backend.
"""

from __future__ import annotations

from typing import Final

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name

CONTRACT_FEATURES: Final[tuple[str, ...]] = (
    "holobit",
    "proyectar",
    "transformar",
    "graficar",
    "corelibs",
    "standard_library",
)
VALID_COMPATIBILITY_LEVELS: Final[tuple[str, ...]] = ("none", "partial", "full")
VALID_TIERS: Final[tuple[str, ...]] = ("tier1", "tier2")

BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = {
    "python": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "full",
        "standard_library": "full",
    },
    "javascript": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "rust": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "wasm": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "go": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "cpp": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "java": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "asm": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "none",
        "transformar": "none",
        "graficar": "none",
        "corelibs": "partial",
        "standard_library": "partial",
    },
}


# Piso contractual: nivel mínimo que cada backend debe mantener por feature.
# Si BACKEND_COMPATIBILITY baja por debajo de este umbral, debe considerarse regresión.
MIN_REQUIRED_BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = {
    "python": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "full",
        "standard_library": "full",
    },
    "javascript": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "rust": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "wasm": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "go": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "cpp": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "java": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "asm": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "none",
        "transformar": "none",
        "graficar": "none",
        "corelibs": "partial",
        "standard_library": "partial",
    },
}

COMPATIBILITY_LEVEL_ORDER: Final[dict[str, int]] = {"none": 0, "partial": 1, "full": 2}


BACKEND_COMPATIBILITY_NOTES: Final[dict[str, dict[str, str]]] = {
    "python": {
        "contract": "full",
        "evidence": "Imports explícitos (`corelibs`, `standard_library`) + llamadas a hooks `cobra_*` con firmas consistentes para primitivas Holobit.",
    },
    "javascript": {
        "contract": "mixed",
        "evidence": "Primitivas Holobit en JS resueltas con hooks explícitos `cobra_*` inyectados en codegen; `corelibs` y `standard_library` quedan en passthrough JS (sin quoting/semántica completa).",
    },
    "rust": {
        "contract": "partial",
        "evidence": "Hooks `cobra_*` para primitivas Holobit y llamadas passthrough (`longitud(cobra)`, `mostrar(hola)`).",
    },
    "wasm": {
        "contract": "partial",
        "evidence": "Llamadas WAT explícitas a hooks `cobra_*`; cuando el runtime no está implementado, los hooks ejecutan `unreachable` (error explícito, sin no-op).",
    },
    "go": {
        "contract": "partial",
        "evidence": "Hooks `cobra*` para primitivas y passthrough de runtime base (`longitud`/`mostrar`).",
    },
    "cpp": {
        "contract": "partial",
        "evidence": "Hooks inline `cobra_*` para primitivas y passthrough de runtime base.",
    },
    "java": {
        "contract": "partial",
        "evidence": "Hooks estáticos `cobra*` para primitivas y passthrough de runtime base.",
    },
    "asm": {
        "contract": "mixed",
        "evidence": "`holobit` se emite como instrucción ASM/IR; `proyectar`/`transformar`/`graficar` fallan con `NotImplementedError` explícito. Las llamadas `CALL` conservan argumentos.",
    },
}


def _validate_contract_shape(name: str, matrix: dict[str, dict[str, str]]) -> None:
    missing_backends = [backend for backend in OFFICIAL_TARGETS if backend not in matrix]
    if missing_backends:
        raise RuntimeError(
            f"{name} no define compatibilidad para backends oficiales: {missing_backends}"
        )

    extra_backends = sorted(set(matrix) - set(OFFICIAL_TARGETS))
    if extra_backends:
        raise RuntimeError(
            f"{name} contiene backends no oficiales o sin registrar: {extra_backends}"
        )

    for backend, contract in matrix.items():
        if contract.get("tier") not in VALID_TIERS:
            raise RuntimeError(
                f"{name}[{backend}] tiene tier inválido: {contract.get('tier')!r}"
            )

        missing_features = [
            feature for feature in CONTRACT_FEATURES if feature not in contract
        ]
        if missing_features:
            raise RuntimeError(
                f"{name}[{backend}] no define features requeridas: {missing_features}"
            )

        extra_features = sorted(
            set(contract) - {"tier", *CONTRACT_FEATURES}
        )
        if extra_features:
            raise RuntimeError(
                f"{name}[{backend}] contiene features no reconocidas: {extra_features}"
            )

        for feature in CONTRACT_FEATURES:
            level = contract[feature]
            if level not in VALID_COMPATIBILITY_LEVELS:
                raise RuntimeError(
                    f"{name}[{backend}][{feature}] tiene nivel inválido: {level!r}"
                )


def validate_backend_compatibility_contract() -> None:
    """Valida que la matriz pública y su mínimo requerido no se desalineen."""
    _validate_contract_shape("BACKEND_COMPATIBILITY", BACKEND_COMPATIBILITY)
    _validate_contract_shape(
        "MIN_REQUIRED_BACKEND_COMPATIBILITY",
        MIN_REQUIRED_BACKEND_COMPATIBILITY,
    )

    for backend in OFFICIAL_TARGETS:
        actual = BACKEND_COMPATIBILITY[backend]
        required = MIN_REQUIRED_BACKEND_COMPATIBILITY[backend]
        if actual["tier"] != required["tier"]:
            raise RuntimeError(
                f"Tier contractual inconsistente para {backend}: "
                f"{actual['tier']} != {required['tier']}"
            )

        for feature in CONTRACT_FEATURES:
            actual_level = actual[feature]
            required_level = required[feature]
            if (
                COMPATIBILITY_LEVEL_ORDER[actual_level]
                < COMPATIBILITY_LEVEL_ORDER[required_level]
            ):
                raise RuntimeError(
                    f"Regresión contractual en {backend}.{feature}: "
                    f"{actual_level} < {required_level}"
                )


validate_backend_compatibility_contract()

def get_backend_compatibility(backend: str) -> dict[str, str] | None:
    """Obtiene compatibilidad por backend aplicando normalización canónica."""
    return BACKEND_COMPATIBILITY.get(normalize_target_name(backend, allow_legacy_aliases=True))


def get_backend_compatibility_notes(backend: str) -> dict[str, str] | None:
    """Obtiene notas de compatibilidad por backend con normalización."""
    return BACKEND_COMPATIBILITY_NOTES.get(normalize_target_name(backend, allow_legacy_aliases=True))


__all__ = [
    "BACKEND_COMPATIBILITY",
    "MIN_REQUIRED_BACKEND_COMPATIBILITY",
    "COMPATIBILITY_LEVEL_ORDER",
    "BACKEND_COMPATIBILITY_NOTES",
    "CONTRACT_FEATURES",
    "get_backend_compatibility",
    "get_backend_compatibility_notes",
    "validate_backend_compatibility_contract",
]
