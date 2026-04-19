"""Orquestador unificado de backend para flujos de build/compilar."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pcobra.cobra.config.transpile_targets import OFFICIAL_TARGETS, target_metadata
from pcobra.cobra.transpilers.module_map import get_toml_map
from pcobra.cobra.transpilers.target_utils import normalize_target_name


@dataclass(frozen=True)
class BackendResolution:
    backend: str
    reason: str


class BuildOrchestrator:
    """Selecciona backend objetivo con reglas unificadas.

    Orden de decisión:
    1) metadata del módulo,
    2) tipo de proyecto,
    3) capacidades requeridas.

    También acepta una preferencia explícita (ruta legacy) para mantener
    compatibilidad en ``cobra compilar --backend`` / ``--tipo``.
    """

    _PROJECT_TYPE_PRIORITIES: dict[str, tuple[str, ...]] = {
        "library": ("python", "rust", "javascript"),
        "web": ("javascript", "python", "rust"),
        "systems": ("rust", "python", "javascript"),
        "embedded": ("rust", "python", "javascript"),
        "application": ("python", "javascript", "rust"),
    }

    def resolve_backend(
        self,
        *,
        source_file: str,
        preferred_backend: str | None = None,
        required_capabilities: tuple[str, ...] = (),
    ) -> BackendResolution:
        config = get_toml_map()
        normalized_preferred = self._normalize_optional_target(preferred_backend)

        if normalized_preferred is not None:
            return BackendResolution(
                backend=normalized_preferred,
                reason="preferencia explícita (legacy/CLI)",
            )

        project_type = self._project_type(config)
        module_meta = self._module_metadata(config, source_file)
        module_target = self._normalize_optional_target(
            module_meta.get("preferred_target")
            or module_meta.get("target")
            or module_meta.get("backend")
        )
        capabilities = self._collect_capabilities(
            config=config,
            module_meta=module_meta,
            requested=required_capabilities,
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

    def _normalize_optional_target(self, value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        canonical = normalize_target_name(value)
        if canonical not in OFFICIAL_TARGETS:
            raise ValueError(
                f"Backend no permitido: {value}. Permitidos: {', '.join(OFFICIAL_TARGETS)}"
            )
        return canonical

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
        weighted = sorted(
            OFFICIAL_TARGETS,
            key=lambda backend: target_metadata(backend)["release_priority"],
        )
        return tuple(weighted)

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
