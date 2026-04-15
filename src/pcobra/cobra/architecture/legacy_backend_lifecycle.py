"""Metadata contractual del ciclo de vida de backends legacy internos.

Este módulo centraliza el estado de retiro de cada backend **interno** para que
CLI y documentación compartan el mismo inventario.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS

LegacyLifecycleStatus = Literal["active-migration", "frozen", "removal-candidate"]


@dataclass(frozen=True, slots=True)
class LegacyBackendLifecycle:
    """Describe el estado de retiro de un backend interno."""

    status: LegacyLifecycleStatus
    recommended_public_target: str
    owner_track: str
    notes: str


LEGACY_BACKEND_LIFECYCLE: Final[dict[str, LegacyBackendLifecycle]] = {
    "go": LegacyBackendLifecycle(
        status="active-migration",
        recommended_public_target="rust",
        owner_track="runtime-migration",
        notes="Backend interno con uso residual en migración activa de pipelines.",
    ),
    "cpp": LegacyBackendLifecycle(
        status="active-migration",
        recommended_public_target="rust",
        owner_track="runtime-migration",
        notes="Se mantiene temporalmente por compatibilidad de integraciones históricas.",
    ),
    "java": LegacyBackendLifecycle(
        status="active-migration",
        recommended_public_target="javascript",
        owner_track="runtime-migration",
        notes="Uso interno controlado durante el retiro de rutas no públicas.",
    ),
    "wasm": LegacyBackendLifecycle(
        status="frozen",
        recommended_public_target="javascript",
        owner_track="maintenance-only",
        notes="Congelado: solo correcciones críticas sin expansión funcional.",
    ),
    "asm": LegacyBackendLifecycle(
        status="removal-candidate",
        recommended_public_target="python",
        owner_track="decommission",
        notes="Candidato explícito a retiro; mantener únicamente para diagnóstico acotado.",
    ),
}


def _validate_legacy_lifecycle_contract() -> None:
    configured = tuple(LEGACY_BACKEND_LIFECYCLE)
    missing = tuple(target for target in INTERNAL_BACKENDS if target not in configured)
    extras = tuple(target for target in configured if target not in INTERNAL_BACKENDS)
    if missing or extras:
        raise RuntimeError(
            "LEGACY_BACKEND_LIFECYCLE debe cubrir exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"configured={configured}; expected={INTERNAL_BACKENDS}"
        )


_validate_legacy_lifecycle_contract()


def lifecycle_status_for_backend(target: str) -> LegacyLifecycleStatus:
    """Devuelve el estado de retiro para un backend interno."""
    return LEGACY_BACKEND_LIFECYCLE[target].status


def legacy_backend_warning_message(*, target: str, route: str) -> str:
    """Mensaje único para advertencias de uso por rutas no públicas."""
    metadata = LEGACY_BACKEND_LIFECYCLE[target]
    return (
        f"[INTERNAL LEGACY BACKEND] '{target}' usado vía ruta no pública ({route}). "
        f"estado={metadata.status}; destino público recomendado={metadata.recommended_public_target}; "
        "uso permitido solo para migración interna temporal."
    )


def iter_legacy_backend_lifecycle_rows() -> tuple[tuple[str, LegacyBackendLifecycle], ...]:
    """Filas ordenadas para consumo en CLI/docs."""
    return tuple((backend, LEGACY_BACKEND_LIFECYCLE[backend]) for backend in INTERNAL_BACKENDS)
