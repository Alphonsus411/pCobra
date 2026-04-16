"""Orquestador unificado de backend para flujos de build/compilar."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pcobra.cobra.architecture.capabilities_contract import (
    PROJECT_TYPE_PUBLIC_POLICY,
    PUBLIC_BACKENDS,
    PUBLIC_FALLBACK_POLICY,
    assert_backend_allowed_for_scope,
    validate_capabilities_contract,
)
from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS
from pcobra.cobra.config.transpile_targets import target_metadata
from pcobra.cobra.transpilers.module_map import get_toml_map
from pcobra.cobra.transpilers.target_utils import normalize_target_name


@dataclass(frozen=True)
class BackendResolution:
    backend: str
    reason: str

    def reason_for(self, *, debug: bool) -> str | None:
        """Expone razón solo cuando el flujo se ejecuta en modo debug."""
        return self.reason if debug else None


class BuildOrchestrator:
    """Selecciona backend objetivo con reglas unificadas.

    Orden de decisión:
    1) metadata del módulo,
    2) tipo de proyecto,
    3) capacidades requeridas.

    También acepta una preferencia explícita (ruta legacy) para mantener
    compatibilidad en ``cobra compilar --backend`` / ``--tipo``.
    """

    _PROJECT_TYPE_PRIORITIES: dict[str, tuple[str, ...]] = dict(PROJECT_TYPE_PUBLIC_POLICY)

    def __init__(self) -> None:
        self._validate_public_backend_routes_contract()

    def resolve_backend(
        self,
        *,
        source_file: str,
        preferred_backend: str | None = None,
        required_capabilities: tuple[str, ...] = (),
        route_scope: str = "public",
    ) -> BackendResolution:
        config = get_toml_map()
        normalized_preferred = self._normalize_optional_target(preferred_backend, route_scope=route_scope)
        project_type = self._project_type(config)
        module_meta = self._module_metadata(config, source_file)

        module_target = self._normalize_optional_target(
            module_meta.get("preferred_target")
            or module_meta.get("target")
            or module_meta.get("backend"),
            route_scope="public",
        )

        capabilities = self._collect_capabilities(
            config=config,
            module_meta=module_meta,
            requested=required_capabilities,
        )

        if normalized_preferred is not None and normalized_preferred in INTERNAL_BACKENDS:
            return BackendResolution(
                backend=normalized_preferred,
                reason="preferencia explícita en ruta de migración interna",
            )

        if normalized_preferred is not None:
            return BackendResolution(
                backend=normalized_preferred,
                reason="preferencia explícita (legacy/CLI)",
            )

        ordered_candidates = self._ordered_candidates(
            project_type=project_type,
            module_target=module_target,
        )

        eligible = [backend for backend in ordered_candidates if self._supports_capabilities(backend, capabilities)]
        if not eligible:
            eligible = [
                backend for backend in self._default_priority() if self._supports_capabilities(backend, capabilities)
            ]

        if not eligible:
            # Fallback de seguridad: nunca devolver un backend fuera de política.
            eligible = list(self._default_priority())

        selected = eligible[0]
        reason_parts = [
            f"project_type={project_type}",
            f"module_target={module_target or '∅'}",
            f"capabilities={','.join(capabilities) if capabilities else '∅'}",
        ]
        return BackendResolution(backend=selected, reason="; ".join(reason_parts))

    def _normalize_optional_target(self, value: Any, *, route_scope: str) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        canonical = normalize_target_name(value)
        assert_backend_allowed_for_scope(backend=canonical, scope=route_scope)
        return canonical

    def _validate_public_backend_routes_contract(self) -> None:
        """Asegura que las rutas públicas de selección no usen backends fuera del canon oficial."""
        validate_capabilities_contract()

        official = set(PUBLIC_BACKENDS)
        covered: set[str] = set()
        for project_type, priorities in self._PROJECT_TYPE_PRIORITIES.items():
            invalid = tuple(target for target in priorities if target not in official)
            if invalid:
                raise RuntimeError(
                    "BuildOrchestrator._PROJECT_TYPE_PRIORITIES contiene backends fuera de PUBLIC_BACKENDS. "
                    f"project_type={project_type}; invalid={invalid}; public={PUBLIC_BACKENDS}"
                )
            covered.update(priorities)

        missing = tuple(target for target in PUBLIC_BACKENDS if target not in covered)
        if missing:
            raise RuntimeError(
                "BuildOrchestrator._PROJECT_TYPE_PRIORITIES debe cubrir todos los PUBLIC_BACKENDS. "
                f"missing={missing}; public={PUBLIC_BACKENDS}"
            )

    def _project_type(self, config: dict[str, Any]) -> str:
        project = config.get("project", {}) if isinstance(config, dict) else {}
        if not isinstance(project, dict):
            return "application"
        raw = (
            project.get("type")
            or project.get("project_type")
            or project.get("kind")
            or "application"
        )
        normalized = str(raw).strip().lower()
        if normalized in self._PROJECT_TYPE_PRIORITIES:
            return normalized
        return "application"

    def _module_metadata(self, config: dict[str, Any], source_file: str) -> dict[str, Any]:
        if not isinstance(config, dict):
            return {}
        modulos = config.get("modulos", {})
        if not isinstance(modulos, dict):
            return {}

        source = Path(source_file)
        candidates = (
            str(source),
            source.name,
            source.as_posix(),
        )
        for key in candidates:
            metadata = modulos.get(key)
            if isinstance(metadata, dict):
                return metadata
        return {}

    def _collect_capabilities(
        self,
        *,
        config: dict[str, Any],
        module_meta: dict[str, Any],
        requested: tuple[str, ...],
    ) -> tuple[str, ...]:
        project = config.get("project", {}) if isinstance(config, dict) else {}
        project_caps = project.get("required_capabilities", []) if isinstance(project, dict) else []
        module_caps = module_meta.get("required_capabilities", []) if isinstance(module_meta, dict) else []

        merged: list[str] = []
        for group in (project_caps, module_caps, list(requested)):
            if isinstance(group, (list, tuple)):
                for value in group:
                    if isinstance(value, str):
                        cap = value.strip().lower()
                        if cap and cap not in merged:
                            merged.append(cap)
        return tuple(merged)

    def _ordered_candidates(self, *, project_type: str, module_target: str | None) -> list[str]:
        ordered: list[str] = []
        if module_target is not None:
            ordered.append(module_target)
        for backend in self._PROJECT_TYPE_PRIORITIES.get(project_type, self._default_priority()):
            if backend not in ordered:
                ordered.append(backend)
        for backend in self._default_priority():
            if backend not in ordered:
                ordered.append(backend)
        return ordered

    def _default_priority(self) -> tuple[str, ...]:
        return tuple(PUBLIC_FALLBACK_POLICY)

    def _supports_capabilities(self, backend: str, capabilities: tuple[str, ...]) -> bool:
        if not capabilities:
            return True

        metadata = target_metadata(backend)
        for capability in capabilities:
            if capability in {"sdk", "sdk_full", "holobit_sdk"} and metadata["sdk_contract"] != "full":
                return False
            if capability in {"holobit", "holobit_full"} and metadata["holobit_contract"] != "full":
                return False
            if capability in {"holobit_partial", "holobit_runtime"} and metadata["holobit_contract"] == "none":
                return False
        return True


__all__ = ["BackendResolution", "BuildOrchestrator"]
