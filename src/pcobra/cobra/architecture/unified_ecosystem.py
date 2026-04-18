"""Plano arquitectónico para el ecosistema unificado de Cobra.

Fuente canónica contractual única (junto con backend_policy/contracts) para
blueprints de ejecución y retiro legacy del ecosistema.

Este módulo no altera el front-end del lenguaje ni los transpilers existentes.
Su propósito es concentrar decisiones de arquitectura y un plan de ejecución
seguro para migración incremental.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS, PUBLIC_BACKENDS


OFFICIAL_USER_LANGUAGE: Final[str] = "cobra"
OFFICIAL_EXECUTION_BACKENDS: Final[tuple[str, ...]] = PUBLIC_BACKENDS

# Inventario de legados que se conservan solo para compatibilidad interna.
LEGACY_BACKEND_REMOVAL_CANDIDATES: Final[dict[str, str]] = {
    "go": "Desalineado del contrato oficial (python/javascript/rust)",
    "cpp": "Fuera del ecosistema oficial de runtime y stdlib",
    "java": "Solo aplica para reverse transpile histórico, no para salida oficial",
    "wasm": "No participa en bindings oficiales del runtime actual",
    "asm": "Sin cobertura del contrato público ni de stdlib",
}


@dataclass(frozen=True, slots=True)
class StdlibBlueprint:
    """Describe la orientación de un módulo público de stdlib."""

    module: str
    api_contract: tuple[str, ...]
    primary_backend: str
    fallback_backends: tuple[str, ...]
    rationale: str


@dataclass(frozen=True, slots=True)
class ImportPolicyBlueprint:
    """Contrato de resolución para `importar` en Cobra."""

    resolution_order: tuple[str, ...]
    conflict_policy: str
    adapter_injection: str


@dataclass(frozen=True, slots=True)
class BindingRouteBlueprint:
    """Especificación de integración entre Cobra y un runtime externo."""

    backend: str
    route: str
    adapter: str
    abi_contract: str


@dataclass(frozen=True, slots=True)
class RefactorTask:
    """Tarea atómica del plan de refactor incremental."""

    id: str
    area: str
    objective: str
    changes: tuple[str, ...]
    safe_checks: tuple[str, ...]


STDLIB_BLUEPRINTS: Final[tuple[StdlibBlueprint, ...]] = (
    StdlibBlueprint(
        module="cobra.core",
        api_contract=("numeros", "texto", "logica"),
        primary_backend="python",
        fallback_backends=("rust", "javascript"),
        rationale="Base transversal y estable para ejecución general.",
    ),
    StdlibBlueprint(
        module="cobra.datos",
        api_contract=("tablas", "columnas", "series"),
        primary_backend="python",
        fallback_backends=("javascript",),
        rationale="Ecosistema de datos y puentes de librerías Python.",
    ),
    StdlibBlueprint(
        module="cobra.web",
        api_contract=("http", "json", "clientes"),
        primary_backend="javascript",
        fallback_backends=("python",),
        rationale="Aprovecha el runtime JS para integración web y APIs.",
    ),
    StdlibBlueprint(
        module="cobra.system",
        api_contract=("archivos", "procesos", "entorno"),
        primary_backend="python",
        fallback_backends=("rust", "javascript"),
        rationale="Operaciones de sistema con ruta híbrida Python/Rust.",
    ),
)


IMPORT_POLICY_BLUEPRINT: Final[ImportPolicyBlueprint] = ImportPolicyBlueprint(
    resolution_order=("stdlib", "project", "python_bridge", "hybrid"),
    conflict_policy="namespace_required para producción; warn en modo migración",
    adapter_injection=(
        "Inyección automática de backend_adapter + metadata __cobra_resolution_metadata__"
    ),
)


BINDING_BLUEPRINTS: Final[tuple[BindingRouteBlueprint, ...]] = (
    BindingRouteBlueprint(
        backend="python",
        route="python_direct_import",
        adapter="python_direct_bridge",
        abi_contract="abi-python-v1",
    ),
    BindingRouteBlueprint(
        backend="javascript",
        route="javascript_runtime_bridge",
        adapter="javascript_controlled_runtime_bridge",
        abi_contract="abi-js-v1",
    ),
    BindingRouteBlueprint(
        backend="rust",
        route="rust_compiled_ffi",
        adapter="rust_compiled_ffi_bridge",
        abi_contract="abi-rust-v1",
    ),
)


def build_refactor_workplan() -> tuple[RefactorTask, ...]:
    """Devuelve tareas estructuradas para implementar la transición.

    Las tareas están ordenadas por riesgo y dependencia, para ejecutarse de forma
    incremental sin romper funcionalidad existente.
    """

    return (
        RefactorTask(
            id="T1",
            area="core-alignment",
            objective="Alinear módulos core con el contrato de 3 backends oficiales.",
            changes=(
                "Reusar PUBLIC_BACKENDS como única fuente en rutas públicas.",
                "Conservar INTERNAL_BACKENDS solo para compatibilidad temporal.",
            ),
            safe_checks=(
                "pytest tests/integration/test_cli_public_help_contract.py",
                "pytest tests/integration/transpilers/test_official_backends_tier2.py",
            ),
        ),
        RefactorTask(
            id="T2",
            area="cli-simplification",
            objective="Consolidar UX en run/build/test/mod sin exposición de transpilers.",
            changes=(
                "Mantener comandos v2 como interfaz por defecto.",
                "Encapsular decisiones de backend en build.backend_pipeline.",
            ),
            safe_checks=(
                "pytest tests/integration/test_cli_ui_v2.py",
                "pytest tests/integration/test_cli_public_help_contract.py",
            ),
        ),
        RefactorTask(
            id="T3",
            area="stdlib-contract",
            objective="Operar stdlib pública por contratos cobra.core/datos/web/system.",
            changes=(
                "Mantener manifest único en pcobra.cobra.stdlib_contract.",
                "Declarar backend primario + fallbacks por módulo.",
            ),
            safe_checks=(
                "python scripts/ci/audit_stdlib_parity.py",
                "pytest tests/integration/test_standard_library_async.py",
            ),
        ),
        RefactorTask(
            id="T4",
            area="imports-bindings",
            objective="Formalizar resolución de imports + bridges de runtime.",
            changes=(
                "Aplicar orden stdlib > proyecto > python_bridge > hybrid.",
                "Inyectar adapters por módulo resuelto en tiempo de carga.",
            ),
            safe_checks=(
                "pytest tests/integration/test_cli_import.py",
                "pytest tests/integration/transpilers/test_backend_runtime_imports_minimal.py",
            ),
        ),
        RefactorTask(
            id="T5",
            area="legacy-removal",
            objective="Retirar componentes legacy no oficiales de forma segura.",
            changes=(
                "Marcar go/cpp/java/wasm/asm como candidatos de retiro.",
                "Eliminar comandos y scripts de backends retirados después de auditoría.",
            ),
            safe_checks=(
                "python scripts/audit_retired_targets.py",
                "python scripts/ci/validate_targets.py",
            ),
        ),
    )


def validate_unified_ecosystem_contract() -> None:
    """Garantiza que el blueprint siga alineado al contrato público actual."""
    if OFFICIAL_USER_LANGUAGE != "cobra":
        raise RuntimeError("La interfaz pública debe ser exclusivamente 'cobra'.")

    if OFFICIAL_EXECUTION_BACKENDS != PUBLIC_BACKENDS:
        raise RuntimeError(
            "El blueprint unificado debe usar exactamente PUBLIC_BACKENDS "
            f"({PUBLIC_BACKENDS}), actual={OFFICIAL_EXECUTION_BACKENDS}."
        )

    # Evita que el inventario de retiro diverja de los legados declarados.
    missing = tuple(sorted(set(INTERNAL_BACKENDS) - set(LEGACY_BACKEND_REMOVAL_CANDIDATES)))
    extras = tuple(sorted(set(LEGACY_BACKEND_REMOVAL_CANDIDATES) - set(INTERNAL_BACKENDS)))
    if missing or extras:
        raise RuntimeError(
            "Inventario legacy inconsistente. "
            f"missing={missing or '∅'} extras={extras or '∅'}"
        )


validate_unified_ecosystem_contract()


__all__ = [
    "OFFICIAL_USER_LANGUAGE",
    "OFFICIAL_EXECUTION_BACKENDS",
    "LEGACY_BACKEND_REMOVAL_CANDIDATES",
    "STDLIB_BLUEPRINTS",
    "IMPORT_POLICY_BLUEPRINT",
    "BINDING_BLUEPRINTS",
    "RefactorTask",
    "StdlibBlueprint",
    "ImportPolicyBlueprint",
    "BindingRouteBlueprint",
    "build_refactor_workplan",
    "validate_unified_ecosystem_contract",
]
