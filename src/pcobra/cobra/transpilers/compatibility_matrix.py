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

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.transpilers.runtime_api_matrix import build_runtime_api_matrix
from pcobra.cobra.transpilers.target_utils import normalize_target_name
from pcobra.cobra.config.transpile_targets import TIER1_TARGETS
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
FEATURE_FULL_BACKENDS: Final[dict[str, tuple[str, ...]]] = {
    "holobit": SDK_FULL_BACKENDS,
    "proyectar": SDK_FULL_BACKENDS,
    "transformar": SDK_FULL_BACKENDS,
    "graficar": SDK_FULL_BACKENDS,
    "corelibs": ("python", "rust"),
    "standard_library": ("python", "rust"),
}
OFFICIAL_RUNTIME_BACKENDS: Final[tuple[str, ...]] = PUBLIC_BACKENDS
BEST_EFFORT_RUNTIME_BACKENDS: Final[tuple[str, ...]] = ()
TRANSPILATION_ONLY_BACKENDS: Final[tuple[str, ...]] = ()
_PUBLIC_BACKEND_KEYS: Final[tuple[str, ...]] = PUBLIC_BACKENDS


_BACKEND_COMPATIBILITY_MODEL: Final[dict[str, dict[str, str]]] = {
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
        "corelibs": "full",
        "standard_library": "full",
    },
}

PUBLIC_BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = {
    backend: _BACKEND_COMPATIBILITY_MODEL[backend] for backend in _PUBLIC_BACKEND_KEYS
}

# Alias temporal para no romper consumidores existentes.
BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = PUBLIC_BACKEND_COMPATIBILITY

SDK_PARTIAL_BACKENDS: Final[tuple[str, ...]] = tuple(
    backend
    for backend in PUBLIC_BACKEND_COMPATIBILITY
    if backend not in SDK_FULL_BACKENDS
)


# Piso contractual: nivel mínimo que cada backend debe mantener por feature.
# Si BACKEND_COMPATIBILITY baja por debajo de este umbral, debe considerarse regresión.
_MIN_REQUIRED_BACKEND_COMPATIBILITY_MODEL: Final[dict[str, dict[str, str]]] = {
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
        "corelibs": "full",
        "standard_library": "full",
    },
}

MIN_REQUIRED_BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = {
    backend: _MIN_REQUIRED_BACKEND_COMPATIBILITY_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}

COMPATIBILITY_LEVEL_ORDER: Final[dict[str, int]] = {"none": 0, "partial": 1, "full": 2}

AST_FEATURES: Final[tuple[str, ...]] = (
    "funciones",
    "clases",
    "decoradores",
    "control_flujo",
    "colecciones",
    "async",
    "holobit",
)

LANGUAGE_EQUIVALENCE_PRIORITY_PHASES: Final[dict[str, tuple[str, ...]]] = {
    "fase_1": ("decoradores", "async", "imports_corelibs"),
    "fase_2": ("manejo_errores",),
    "fase_3": ("tipos_compuestos",),
}

# Mapeo explícito feature -> nodos soportados por backend para la hoja de ruta
# de equivalencia versionada (`data/language_equivalence.yml`).
_BACKEND_FEATURE_NODE_SUPPORT_MODEL: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    "python": {
        "decoradores": ("visit_decorador", "visit_funcion"),
        "imports_corelibs": ("visit_usar", "visit_import", "visit_llamada_funcion"),
        "manejo_errores": ("visit_try_catch", "visit_throw"),
        "async": ("visit_funcion", "visit_esperar"),
        "tipos_compuestos": ("visit_lista", "visit_diccionario", "visit_lista_tipo", "visit_diccionario_tipo"),
    },
    "javascript": {
        "decoradores": ("visit_decorador", "visit_funcion"),
        "imports_corelibs": ("visit_import", "visit_llamada_funcion"),
        "manejo_errores": ("visit_try_catch", "visit_throw"),
        "async": ("visit_funcion", "visit_esperar"),
        "tipos_compuestos": ("visit_lista", "visit_diccionario", "visit_lista_tipo", "visit_diccionario_tipo"),
    },
    "rust": {
        "decoradores": ("visit_decorador", "visit_funcion"),
        "imports_corelibs": ("visit_usar", "visit_import", "visit_llamada_funcion"),
        "manejo_errores": ("visit_try_catch", "visit_throw"),
        "async": ("visit_funcion", "visit_esperar"),
        "tipos_compuestos": ("visit_lista", "visit_diccionario"),
    },
}

BACKEND_FEATURE_NODE_SUPPORT: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    backend: _BACKEND_FEATURE_NODE_SUPPORT_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}

# Matriz ejecutable (respaldada por tests) para nodos AST clave por backend.
# Esta tabla se usa como piso contractual para el gate de CI de paridad.
_AST_FEATURE_MINIMUM_CONTRACT_MODEL: Final[dict[str, dict[str, str]]] = {
    "python": {
        "funciones": "full",
        "clases": "full",
        "decoradores": "full",
        "control_flujo": "full",
        "colecciones": "full",
        "async": "full",
        "holobit": "full",
    },
    "javascript": {
        "funciones": "full",
        "clases": "full",
        "decoradores": "full",
        "control_flujo": "full",
        "colecciones": "full",
        "async": "full",
        "holobit": "partial",
    },
    "rust": {
        "funciones": "full",
        "clases": "partial",
        "decoradores": "full",
        "control_flujo": "partial",
        "colecciones": "partial",
        "async": "full",
        "holobit": "partial",
    },
}

AST_FEATURE_MINIMUM_CONTRACT: Final[dict[str, dict[str, str]]] = {
    backend: _AST_FEATURE_MINIMUM_CONTRACT_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}

# Baseline sincronizada con evidencia real de tests parametrizados.
AST_FEATURE_EVIDENCE_BASELINE: Final[dict[str, dict[str, str]]] = AST_FEATURE_MINIMUM_CONTRACT

AST_FEATURE_EVIDENCE_SOURCE: Final[str] = (
    "tests/unit/test_transpiler_feature_parity.py::test_feature_parity_matrix_evidence_matches_contract"
)


LIVE_RUNTIME_API_MATRIX: Final[dict[str, object]] = build_runtime_api_matrix()


_BACKEND_COMPATIBILITY_NOTES_MODEL: Final[dict[str, dict[str, str]]] = {
    "python": {
        "contract": "full",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports Python explícitos (`from corelibs import *`, `from standard_library import *`) y símbolos mínimos invocables en el código generado (`longitud`, `mostrar`). Holobit usa hooks `cobra_*` canónicos; `cobra_holobit` crea `Holobit` real y las primitivas avanzadas fallan con `ModuleNotFoundError` mencionando `holobit_sdk` cuando el entorno incumple la dependencia obligatoria de Python `>=3.10`.",
    },
    "javascript": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports ES module explícitos y una capa adaptadora mantenida por el proyecto (`cobraJsCorelibs`, `cobraJsStandardLibrary`) que hace invocables `longitud` y `mostrar`. Holobit usa hooks `cobra_*` canónicos sobre un objeto runtime propio (`__cobra_tipo__=holobit`): `cobra_holobit` materializa la estructura adaptada; `cobra_proyectar` soporta `1d`/`2d`/`3d`/`vector`; `cobra_transformar` cubre `escalar`, `normalizar`, `mover`/`trasladar` y rotación planar sobre eje `z`; `cobra_graficar` emite una vista textual vía `mostrar`. El backend no depende de `holobit_sdk`; cuando una operación sale del adaptador soportado, falla con error explícito de contrato `partial` y sin fallback silencioso. Sigue siendo `partial` porque no equivale al SDK Python ni cubre toda la semántica avanzada.",
    },
    "rust": {
        "contract": "partial",
        "evidence": "Compatibilidad con `corelibs`/`standard_library` significa imports base más una capa adaptadora Rust mantenida por el proyecto (`longitud`, `mostrar`) generada inline. Holobit usa hooks `cobra_*` canónicos sobre `CobraHolobit`: `cobra_holobit` crea el valor runtime; `cobra_proyectar` devuelve `Result<Vec<f64>, CobraRuntimeError>` para `1d`/`2d`/`3d`/`vector`; `cobra_transformar` devuelve `Result<CobraHolobit, CobraRuntimeError>` con operaciones base (`escalar`, `normalizar`, `mover`, `rotar` planar); `cobra_graficar` devuelve `Result<String, CobraRuntimeError>` y reutiliza `mostrar`. El backend no depende de `holobit_sdk`; cuando la operación no cabe en el adaptador, devuelve `CobraRuntimeError` explícito de contrato `partial` y sin fallback silencioso. El contrato permanece `partial` porque no existe paridad completa con `holobit_sdk`.",
    },
}

BACKEND_COMPATIBILITY_NOTES: Final[dict[str, dict[str, str]]] = {
    backend: _BACKEND_COMPATIBILITY_NOTES_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}

_BACKEND_FEATURE_GAPS_MODEL: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    "python": {
        "holobit": (),
        "proyectar": (),
        "transformar": (),
        "graficar": (),
        "corelibs": (),
        "standard_library": (),
    },
    "javascript": {
        "holobit": ("No replica paridad SDK Python completa.",),
        "proyectar": ("Limitado a modos 1d/2d/3d/vector del adaptador oficial.",),
        "transformar": ("Rotación soportada solo sobre eje z.",),
        "graficar": ("Solo vista textual via `mostrar`.",),
        "corelibs": ("Cobertura parcial mediante capa adaptadora JS.",),
        "standard_library": ("Cobertura parcial mediante capa adaptadora JS.",),
    },
    "rust": {
        "holobit": ("No replica paridad SDK Python completa.",),
        "proyectar": ("Limitado a modos 1d/2d/3d/vector del adaptador oficial.",),
        "transformar": ("Rotación soportada solo sobre eje z y parámetros parseados en runtime.",),
        "graficar": ("Solo vista textual via `mostrar`.",),
        "corelibs": (),
        "standard_library": (),
    },
}

BACKEND_FEATURE_GAPS: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    backend: _BACKEND_FEATURE_GAPS_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}

HOLOBIT_SDK_CAPABILITIES: Final[tuple[str, ...]] = (
    "runtime",
    "serializacion",
    "ipc",
    "modulos_nativos",
    "import_hooks",
)

VALID_HOLOBIT_CAPABILITY_STATUSES: Final[tuple[str, ...]] = (
    "full",
    "partial",
    "none",
)

CRITICAL_HOLOBIT_CAPABILITIES: Final[tuple[str, ...]] = (
    "runtime",
    "import_hooks",
)

# Matriz operativa de capacidades Holobit por target oficial.
# Se usa para documentación versionada y para gate de release sobre Tier 1.
_BACKEND_HOLOBIT_SDK_CAPABILITIES_MODEL: Final[dict[str, dict[str, str]]] = {
    "python": {
        "runtime": "full",
        "serializacion": "full",
        "ipc": "full",
        "modulos_nativos": "full",
        "import_hooks": "full",
    },
    "javascript": {
        "runtime": "partial",
        "serializacion": "partial",
        "ipc": "none",
        "modulos_nativos": "partial",
        "import_hooks": "full",
    },
    "rust": {
        "runtime": "partial",
        "serializacion": "partial",
        "ipc": "none",
        "modulos_nativos": "partial",
        "import_hooks": "full",
    },
}

BACKEND_HOLOBIT_SDK_CAPABILITIES: Final[dict[str, dict[str, str]]] = {
    backend: _BACKEND_HOLOBIT_SDK_CAPABILITIES_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}

# Piso crítico: si Tier 1 baja de este mínimo, se bloquea el release.
MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES: Final[dict[str, dict[str, str]]] = {
    "python": {
        "runtime": "full",
        "import_hooks": "full",
    },
    "javascript": {
        "runtime": "partial",
        "import_hooks": "full",
    },
    "rust": {
        "runtime": "partial",
        "import_hooks": "full",
    },
}

_HOLOBIT_CAPABILITY_FALLBACKS_MODEL: Final[dict[str, dict[str, str]]] = {
    "python": {
        "runtime": "Sin fallback automático: exige `holobit_sdk` y falla explícitamente con ModuleNotFoundError.",
        "serializacion": "Usar objetos `Holobit` del SDK como formato canónico de intercambio.",
        "ipc": "Reusar runtime Python y tipado `Holobit` en procesos/hilos Python.",
        "modulos_nativos": "Usar `corelibs`/`standard_library` con implementación oficial Python.",
        "import_hooks": "Sin fallback: hooks canónicos `cobra_*` se consideran obligatorios.",
    },
    "javascript": {
        "runtime": "Fallback oficial: adaptador runtime JS del proyecto con errores `partial` explícitos.",
        "serializacion": "Fallback oficial: proyecciones 1d/2d/3d/vector y vista textual `Holobit(...)`.",
        "ipc": "No soportado: delegar IPC a procesos externos y pasar payload serializado simple.",
        "modulos_nativos": "Fallback oficial: capa `cobraJsCorelibs` y `cobraJsStandardLibrary`.",
        "import_hooks": "Hooks `cobra_*` obligatorios en codegen; sin fallback silencioso.",
    },
    "rust": {
        "runtime": "Fallback oficial: adaptador `CobraHolobit` con `Result` y `CobraRuntimeError` explícito.",
        "serializacion": "Fallback oficial: `Vec<f64>` y parsing controlado en runtime.",
        "ipc": "No soportado: usar integración externa y pasar datos serializados simples.",
        "modulos_nativos": "Fallback oficial: helpers inline del backend (`longitud`, `mostrar`).",
        "import_hooks": "Hooks `cobra_*` obligatorios en codegen; sin fallback silencioso.",
    },
}

HOLOBIT_CAPABILITY_FALLBACKS: Final[dict[str, dict[str, str]]] = {
    backend: _HOLOBIT_CAPABILITY_FALLBACKS_MODEL[backend]
    for backend in PUBLIC_BACKEND_COMPATIBILITY
}


def _validate_contract_shape(name: str, matrix: dict[str, dict[str, str]]) -> None:
    missing_backends = [backend for backend in PUBLIC_BACKENDS if backend not in matrix]
    if missing_backends:
        raise RuntimeError(
            f"{name} no define compatibilidad para backends oficiales: {missing_backends}"
        )

    extra_backends = sorted(set(matrix) - set(PUBLIC_BACKENDS))
    if extra_backends:
        raise RuntimeError(
            f"{name} contiene backends no oficiales, legacy o sin registrar: {extra_backends}"
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

    for backend in PUBLIC_BACKENDS:
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
            for backend in PUBLIC_BACKENDS
            if BACKEND_COMPATIBILITY[backend][feature] == "full"
        }
        expected_full_backends = set(FEATURE_FULL_BACKENDS[feature])
        if full_backends != expected_full_backends:
            raise RuntimeError(
                "Promoción contractual inválida: "
                f"solo {tuple(sorted(expected_full_backends))} puede figurar como 'full' para {feature}, "
                f"pero la matriz declara {tuple(sorted(full_backends))}"
            )

    full_set = set(SDK_FULL_BACKENDS)
    partial_set = set(SDK_PARTIAL_BACKENDS)
    official_set = set(PUBLIC_BACKENDS)
    if full_set & partial_set:
        raise RuntimeError(
            "SDK_FULL_BACKENDS y SDK_PARTIAL_BACKENDS no deben solaparse: "
            f"{tuple(sorted(full_set & partial_set))}"
        )
    if full_set | partial_set != official_set:
        raise RuntimeError(
            "SDK_FULL_BACKENDS + SDK_PARTIAL_BACKENDS deben cubrir exactamente PUBLIC_BACKENDS: "
            f"faltan={tuple(sorted(official_set - (full_set | partial_set)))} "
            f"extras={tuple(sorted((full_set | partial_set) - official_set))}"
        )
    runtime_set = set(OFFICIAL_RUNTIME_BACKENDS)
    best_effort_set = set(BEST_EFFORT_RUNTIME_BACKENDS)
    transpilation_only_set = set(TRANSPILATION_ONLY_BACKENDS)
    if runtime_set & best_effort_set:
        raise RuntimeError(
            "OFFICIAL_RUNTIME_BACKENDS y BEST_EFFORT_RUNTIME_BACKENDS no deben solaparse: "
            f"{tuple(sorted(runtime_set & best_effort_set))}"
        )
    if runtime_set & transpilation_only_set:
        raise RuntimeError(
            "OFFICIAL_RUNTIME_BACKENDS y TRANSPILATION_ONLY_BACKENDS no deben solaparse: "
            f"{tuple(sorted(runtime_set & transpilation_only_set))}"
        )
    if best_effort_set & transpilation_only_set:
        raise RuntimeError(
            "BEST_EFFORT_RUNTIME_BACKENDS y TRANSPILATION_ONLY_BACKENDS no deben solaparse: "
            f"{tuple(sorted(best_effort_set & transpilation_only_set))}"
        )
    if runtime_set | best_effort_set | transpilation_only_set != official_set:
        raise RuntimeError(
            "Las categorías de runtime deben particionar PUBLIC_BACKENDS exactamente: "
            f"runtime={OFFICIAL_RUNTIME_BACKENDS}; best_effort={BEST_EFFORT_RUNTIME_BACKENDS}; "
            f"transpilation_only={TRANSPILATION_ONLY_BACKENDS}; official={PUBLIC_BACKENDS}"
        )

    missing_notes_backends = [backend for backend in PUBLIC_BACKENDS if backend not in BACKEND_COMPATIBILITY_NOTES]
    if missing_notes_backends:
        raise RuntimeError(
            f"BACKEND_COMPATIBILITY_NOTES no define backends oficiales: {missing_notes_backends}"
        )
    extra_notes_backends = sorted(set(BACKEND_COMPATIBILITY_NOTES) - set(PUBLIC_BACKENDS))
    if extra_notes_backends:
        raise RuntimeError(
            f"BACKEND_COMPATIBILITY_NOTES contiene backends no oficiales: {extra_notes_backends}"
        )
    for backend in PUBLIC_BACKENDS:
        notes = BACKEND_COMPATIBILITY_NOTES[backend]
        if notes.get("contract") not in VALID_COMPATIBILITY_LEVELS:
            raise RuntimeError(
                f"BACKEND_COMPATIBILITY_NOTES[{backend}].contract tiene nivel inválido: {notes.get('contract')!r}"
            )
        if notes.get("contract") != "full" and backend in SDK_FULL_BACKENDS:
            raise RuntimeError(
                f"BACKEND_COMPATIBILITY_NOTES[{backend}] debe declarar contract='full' para backend SDK_FULL"
            )
        if notes.get("contract") == "full" and backend in SDK_PARTIAL_BACKENDS:
            raise RuntimeError(
                f"BACKEND_COMPATIBILITY_NOTES[{backend}] no puede declarar contract='full' para backend SDK_PARTIAL"
            )
        evidence = notes.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            raise RuntimeError(
                f"BACKEND_COMPATIBILITY_NOTES[{backend}] debe declarar evidence no vacío"
            )

    missing_gaps_backends = [backend for backend in PUBLIC_BACKENDS if backend not in BACKEND_FEATURE_GAPS]
    if missing_gaps_backends:
        raise RuntimeError(
            f"BACKEND_FEATURE_GAPS no define backends oficiales: {missing_gaps_backends}"
        )
    extra_gaps_backends = sorted(set(BACKEND_FEATURE_GAPS) - set(PUBLIC_BACKENDS))
    if extra_gaps_backends:
        raise RuntimeError(
            f"BACKEND_FEATURE_GAPS contiene backends no oficiales: {extra_gaps_backends}"
        )
    for backend in PUBLIC_BACKENDS:
        missing_features = [
            feature for feature in CONTRACT_FEATURES if feature not in BACKEND_FEATURE_GAPS[backend]
        ]
        if missing_features:
            raise RuntimeError(
                f"BACKEND_FEATURE_GAPS[{backend}] no define features requeridas: {missing_features}"
            )
        for feature in CONTRACT_FEATURES:
            gaps = BACKEND_FEATURE_GAPS[backend][feature]
            if not isinstance(gaps, tuple):
                raise RuntimeError(
                    f"BACKEND_FEATURE_GAPS[{backend}][{feature}] debe ser tuple[str, ...], recibido={type(gaps).__name__}"
                )
            level = BACKEND_COMPATIBILITY[backend][feature]
            if level == "full" and gaps:
                raise RuntimeError(
                    f"BACKEND_FEATURE_GAPS[{backend}][{feature}] no debe declarar gaps cuando el nivel es full"
                )
            if level == "partial" and not gaps:
                raise RuntimeError(
                    f"BACKEND_FEATURE_GAPS[{backend}][{feature}] debe declarar al menos un gap para contrato partial"
                )

    missing_capability_backends = [
        backend for backend in PUBLIC_BACKENDS if backend not in BACKEND_HOLOBIT_SDK_CAPABILITIES
    ]
    if missing_capability_backends:
        raise RuntimeError(
            "BACKEND_HOLOBIT_SDK_CAPABILITIES no define backends oficiales: "
            f"{missing_capability_backends}"
        )
    extra_capability_backends = sorted(
        set(BACKEND_HOLOBIT_SDK_CAPABILITIES) - set(PUBLIC_BACKENDS)
    )
    if extra_capability_backends:
        raise RuntimeError(
            "BACKEND_HOLOBIT_SDK_CAPABILITIES contiene backends no oficiales: "
            f"{extra_capability_backends}"
        )

    for backend in PUBLIC_BACKENDS:
        capabilities = BACKEND_HOLOBIT_SDK_CAPABILITIES[backend]
        missing_capabilities = [
            capability
            for capability in HOLOBIT_SDK_CAPABILITIES
            if capability not in capabilities
        ]
        if missing_capabilities:
            raise RuntimeError(
                f"BACKEND_HOLOBIT_SDK_CAPABILITIES[{backend}] no define capacidades requeridas: {missing_capabilities}"
            )
        extra_capabilities = sorted(
            set(capabilities) - set(HOLOBIT_SDK_CAPABILITIES)
        )
        if extra_capabilities:
            raise RuntimeError(
                f"BACKEND_HOLOBIT_SDK_CAPABILITIES[{backend}] contiene capacidades no reconocidas: {extra_capabilities}"
            )
        for capability in HOLOBIT_SDK_CAPABILITIES:
            status = capabilities[capability]
            if status not in VALID_HOLOBIT_CAPABILITY_STATUSES:
                raise RuntimeError(
                    f"BACKEND_HOLOBIT_SDK_CAPABILITIES[{backend}][{capability}] tiene estado inválido: {status!r}"
                )

    validate_tier1_holobit_release_gate(BACKEND_HOLOBIT_SDK_CAPABILITIES)

    missing_fallback_backends = [
        backend for backend in PUBLIC_BACKENDS if backend not in HOLOBIT_CAPABILITY_FALLBACKS
    ]
    if missing_fallback_backends:
        raise RuntimeError(
            f"HOLOBIT_CAPABILITY_FALLBACKS no define backends oficiales: {missing_fallback_backends}"
        )
    for backend in PUBLIC_BACKENDS:
        fallback_map = HOLOBIT_CAPABILITY_FALLBACKS[backend]
        for capability in HOLOBIT_SDK_CAPABILITIES:
            fallback = fallback_map.get(capability, "")
            if not isinstance(fallback, str) or not fallback.strip():
                raise RuntimeError(
                    f"HOLOBIT_CAPABILITY_FALLBACKS[{backend}][{capability}] debe tener documentación explícita de fallback"
                )


def validate_tier1_holobit_release_gate(
    capabilities_by_backend: dict[str, dict[str, str]],
) -> None:
    """Bloquea release si Tier 1 rompe capacidades críticas Holobit."""
    for backend in TIER1_TARGETS:
        if backend not in MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES:
            raise RuntimeError(
                f"MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES no define backend Tier 1: {backend}"
            )
        if backend not in capabilities_by_backend:
            raise RuntimeError(
                f"BACKEND_HOLOBIT_SDK_CAPABILITIES no define backend Tier 1: {backend}"
            )
        for capability in CRITICAL_HOLOBIT_CAPABILITIES:
            required = MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES[backend].get(capability)
            if required not in VALID_HOLOBIT_CAPABILITY_STATUSES:
                raise RuntimeError(
                    f"MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES[{backend}][{capability}] inválido: {required!r}"
                )
            current = capabilities_by_backend[backend].get(capability)
            if current not in VALID_HOLOBIT_CAPABILITY_STATUSES:
                raise RuntimeError(
                    f"BACKEND_HOLOBIT_SDK_CAPABILITIES[{backend}][{capability}] inválido: {current!r}"
                )
            if COMPATIBILITY_LEVEL_ORDER[current] < COMPATIBILITY_LEVEL_ORDER[required]:
                raise RuntimeError(
                    "Regresión crítica Holobit en Tier 1: "
                    f"{backend}.{capability}={current} < mínimo requerido {required}. "
                    "El release debe bloquearse."
                )


def validate_ast_feature_parity_release_gate(
    evidence_by_backend: dict[str, dict[str, str]],
) -> None:
    """Bloquea release si la evidencia baja bajo el mínimo contractual AST."""
    for backend in PUBLIC_BACKENDS:
        if backend not in AST_FEATURE_MINIMUM_CONTRACT:
            raise RuntimeError(
                f"AST_FEATURE_MINIMUM_CONTRACT no define backend oficial: {backend}"
            )
        if backend not in evidence_by_backend:
            raise RuntimeError(
                "Evidencia AST incompleta: falta backend "
                f"{backend} (fuente: {AST_FEATURE_EVIDENCE_SOURCE})"
            )
        expected_features = AST_FEATURE_MINIMUM_CONTRACT[backend]
        actual_features = evidence_by_backend[backend]
        for feature in AST_FEATURES:
            required = expected_features.get(feature)
            if required not in VALID_COMPATIBILITY_LEVELS:
                raise RuntimeError(
                    f"AST_FEATURE_MINIMUM_CONTRACT[{backend}][{feature}] inválido: {required!r}"
                )
            current = actual_features.get(feature)
            if current not in VALID_COMPATIBILITY_LEVELS:
                raise RuntimeError(
                    "Evidencia AST inválida en "
                    f"{backend}.{feature}: {current!r} (fuente: {AST_FEATURE_EVIDENCE_SOURCE})"
                )
            if COMPATIBILITY_LEVEL_ORDER[current] < COMPATIBILITY_LEVEL_ORDER[required]:
                raise RuntimeError(
                    "Regresión AST contractual en "
                    f"{backend}.{feature}: {current} < mínimo {required} "
                    f"(fuente: {AST_FEATURE_EVIDENCE_SOURCE})"
                )


validate_backend_compatibility_contract()


_AST_FEATURE_NODE_SUPPORT_MAP: Final[dict[str, str]] = {
    "decoradores": "decoradores",
    "async": "async",
    "colecciones": "tipos_compuestos",
}


def build_feature_gap_report(
    expected_contract: dict[str, dict[str, str]] | None = None,
    evidence_baseline: dict[str, dict[str, str]] | None = None,
    backend_node_support: dict[str, dict[str, tuple[str, ...]]] | None = None,
) -> dict[str, list[dict[str, object]]]:
    """Construye un reporte explícito de gaps AST por backend."""

    expected = expected_contract or AST_FEATURE_MINIMUM_CONTRACT
    evidence = evidence_baseline or AST_FEATURE_EVIDENCE_BASELINE
    node_support = backend_node_support or BACKEND_FEATURE_NODE_SUPPORT
    reference_backend = "python"
    report: dict[str, list[dict[str, object]]] = {}

    for backend in PUBLIC_BACKENDS:
        backend_expected = expected.get(backend, {})
        backend_actual = evidence.get(backend, {})
        backend_rows: list[dict[str, object]] = []

        for feature in AST_FEATURES:
            expected_level = backend_expected.get(feature, "none")
            actual_level = backend_actual.get(feature, "none")
            if (
                expected_level not in COMPATIBILITY_LEVEL_ORDER
                or actual_level not in COMPATIBILITY_LEVEL_ORDER
            ):
                continue
            if COMPATIBILITY_LEVEL_ORDER[actual_level] >= COMPATIBILITY_LEVEL_ORDER[expected_level]:
                continue

            missing_nodes: tuple[str, ...] | None = None
            support_key = _AST_FEATURE_NODE_SUPPORT_MAP.get(feature)
            if support_key:
                required_nodes = set(
                    node_support.get(reference_backend, {}).get(support_key, ())
                )
                current_nodes = set(node_support.get(backend, {}).get(support_key, ()))
                missing_nodes = tuple(sorted(required_nodes - current_nodes))

            backend_rows.append(
                {
                    "feature": feature,
                    "expected_level": expected_level,
                    "actual_level": actual_level,
                    "missing_nodes": list(missing_nodes or ()),
                }
            )

        report[backend] = backend_rows

    return report

def get_backend_compatibility(backend: str) -> dict[str, str] | None:
    """Obtiene compatibilidad por backend aplicando normalización canónica."""
    return BACKEND_COMPATIBILITY.get(normalize_target_name(backend))


def get_backend_compatibility_notes(backend: str) -> dict[str, str] | None:
    """Obtiene notas de compatibilidad por backend con normalización."""
    return BACKEND_COMPATIBILITY_NOTES.get(normalize_target_name(backend))


def get_backend_feature_gaps(backend: str) -> dict[str, tuple[str, ...]] | None:
    """Obtiene gaps explícitos por feature para un backend."""
    return BACKEND_FEATURE_GAPS.get(normalize_target_name(backend))


__all__ = [
    "PUBLIC_BACKEND_COMPATIBILITY",
    "BACKEND_COMPATIBILITY",
    "MIN_REQUIRED_BACKEND_COMPATIBILITY",
    "COMPATIBILITY_LEVEL_ORDER",
    "BACKEND_COMPATIBILITY_NOTES",
    "BACKEND_FEATURE_GAPS",
    "BACKEND_HOLOBIT_SDK_CAPABILITIES",
    "HOLOBIT_SDK_CAPABILITIES",
    "VALID_HOLOBIT_CAPABILITY_STATUSES",
    "CRITICAL_HOLOBIT_CAPABILITIES",
    "MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES",
    "HOLOBIT_CAPABILITY_FALLBACKS",
    "CONTRACT_FEATURES",
    "SDK_FULL_BACKENDS",
    "SDK_PARTIAL_BACKENDS",
    "OFFICIAL_RUNTIME_BACKENDS",
    "BEST_EFFORT_RUNTIME_BACKENDS",
    "TRANSPILATION_ONLY_BACKENDS",
    "AST_FEATURES",
    "AST_FEATURE_MINIMUM_CONTRACT",
    "AST_FEATURE_EVIDENCE_BASELINE",
    "AST_FEATURE_EVIDENCE_SOURCE",
    "build_feature_gap_report",
    "get_backend_compatibility",
    "get_backend_compatibility_notes",
    "get_backend_feature_gaps",
    "validate_tier1_holobit_release_gate",
    "validate_ast_feature_parity_release_gate",
    "validate_backend_compatibility_contract",
]


def get_live_runtime_api_matrix() -> dict[str, object]:
    """Devuelve una copia ligera de la matriz viva de API runtime por backend."""

    return LIVE_RUNTIME_API_MATRIX





