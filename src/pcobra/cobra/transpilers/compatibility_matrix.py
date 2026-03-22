"""Matriz mínima de compatibilidad de transpiladores por tier.

Esta matriz documenta qué garantías ofrece cada backend para:
- primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`)
- imports base de runtime (`corelibs`, `standard_library`)

Niveles:
- ``full``: contrato de codegen y hooks cubierto por regresión; si falta una
  dependencia requerida por el backend, el fallo debe ser explícito y documentado.
- ``partial``: soporte limitado o stub explícito; genera código válido pero la
  ejecución puede terminar con error controlado en lugar de emular el backend
  avanzado.
- ``none``: la feature no está garantizada por backend y puede rechazar la
  generación.
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
SDK_FULL_BACKENDS: Final[tuple[str, ...]] = ("python",)
SDK_PARTIAL_BACKENDS: Final[tuple[str, ...]] = tuple(
    backend for backend in OFFICIAL_TARGETS if backend not in SDK_FULL_BACKENDS
)

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
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
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
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
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
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
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
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
}

COMPATIBILITY_LEVEL_ORDER: Final[dict[str, int]] = {"none": 0, "partial": 1, "full": 2}


BACKEND_COMPATIBILITY_NOTES: Final[dict[str, dict[str, str]]] = {
    "python": {
        "contract": "full",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports Python explícitos y símbolos invocables en el código generado. Holobit usa hooks `cobra_*` canónicos; `cobra_holobit` crea `Holobit` real y las primitivas avanzadas fallan con `ModuleNotFoundError` mencionando `holobit_sdk` cuando el entorno incumple la dependencia obligatoria de Python `>=3.10`.",
    },
    "javascript": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports ES module explícitos y una capa adaptadora mantenida por el proyecto (`cobraJsCorelibs`, `cobraJsStandardLibrary`) que hace invocables `longitud` y `mostrar`. Holobit usa hooks `cobra_*` canónicos sobre un objeto runtime propio (`__cobra_tipo__=holobit`) con proyección 1D/2D/3D, transformaciones base (`escalar`, `normalizar`, `mover`, `rotar` sobre eje z) y `graficar` textual; el contrato sigue siendo `partial` porque no equivale al SDK Python ni cubre toda la semántica avanzada.",
    },
    "rust": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports base más una capa adaptadora Rust mantenida por el proyecto (`longitud`, `mostrar`) generada inline. Holobit usa hooks `cobra_*` canónicos sobre `CobraHolobit` y devuelve `Result` con `CobraRuntimeError`; soporta proyecciones 1D/2D/3D/vector, transformaciones base (`escalar`, `normalizar`, `mover`, `rotar` planar) y `graficar` textual. El contrato permanece `partial` porque no existe paridad completa con `holobit_sdk`.",
    },
    "wasm": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa emitir wrappers WAT e imports explícitos hacia un runtime host-managed (`pcobra:corelibs`, `pcobra:standard_library`). Holobit usa hooks `cobra_*` canónicos que delegan en imports `pcobra:holobit`; el backend deja de usar `unreachable`, pero sigue en `partial` porque la semántica completa depende del host y del protocolo de handles/param buffers externo al módulo generado.",
    },
    "go": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports Go verificables (`cobra/corelibs`, `cobra/standard_library`) y preservación de símbolos de runtime. Holobit usa hooks canónicos `cobra_*`; `cobra_holobit` devuelve la colección y las primitivas avanzadas fallan con `panic` explícito.",
    },
    "cpp": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa includes verificables (`cobra/corelibs.hpp`, `cobra/standard_library.hpp`) y preservación de símbolos de runtime. Holobit usa hooks inline `cobra_*`; `cobra_holobit` devuelve la colección y las primitivas avanzadas fallan con `std::runtime_error` explícito.",
    },
    "java": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports verificables (`cobra.corelibs.*`, `cobra.standard_library.*`) y preservación de símbolos de runtime. Holobit usa hooks estáticos canónicos `cobra_*`; `cobra_holobit` devuelve la colección y las primitivas avanzadas fallan con `UnsupportedOperationException` explícito.",
    },
    "asm": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa conservar puntos de llamada `CALL` y declarar explícitamente que el runtime externo se administra fuera del backend. Holobit inyecta hooks `cobra_*`; `cobra_holobit` conserva la representación IR y `proyectar`/`transformar`/`graficar` fallan con `TRAP` explícito, sin `none` ni no-op silencioso.",
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

    for feature in CONTRACT_FEATURES:
        full_backends = {
            backend
            for backend in OFFICIAL_TARGETS
            if BACKEND_COMPATIBILITY[backend][feature] == "full"
        }
        if full_backends != set(SDK_FULL_BACKENDS):
            raise RuntimeError(
                "Promoción contractual inválida: "
                f"solo {SDK_FULL_BACKENDS} puede figurar como 'full' para {feature}, "
                f"pero la matriz declara {tuple(sorted(full_backends))}"
            )


validate_backend_compatibility_contract()

def get_backend_compatibility(backend: str) -> dict[str, str] | None:
    """Obtiene compatibilidad por backend aplicando normalización canónica."""
    return BACKEND_COMPATIBILITY.get(normalize_target_name(backend))


def get_backend_compatibility_notes(backend: str) -> dict[str, str] | None:
    """Obtiene notas de compatibilidad por backend con normalización."""
    return BACKEND_COMPATIBILITY_NOTES.get(normalize_target_name(backend))


__all__ = [
    "BACKEND_COMPATIBILITY",
    "MIN_REQUIRED_BACKEND_COMPATIBILITY",
    "COMPATIBILITY_LEVEL_ORDER",
    "BACKEND_COMPATIBILITY_NOTES",
    "CONTRACT_FEATURES",
    "SDK_FULL_BACKENDS",
    "SDK_PARTIAL_BACKENDS",
    "get_backend_compatibility",
    "get_backend_compatibility_notes",
    "validate_backend_compatibility_contract",
]
