"""Resolvedor de imports Cobra con estrategia determinista por origen."""

from __future__ import annotations

import importlib
import importlib.util
import warnings
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping

from pcobra.cobra.backends.resolver import resolve_backend
from pcobra.cobra.architecture.contracts import assert_backend_allowed_for_scope
from pcobra.cobra.imports._module_map_api import get_toml_map, resolve_backend_for_module
from pcobra.cobra.stdlib_contract import get_public_stdlib_module_contracts


class ImportResolutionError(RuntimeError):
    """Error base al resolver imports Cobra."""


@dataclass(frozen=True)
class HybridModuleSpec:
    """Declaración de módulo híbrido."""

    module: str
    import_path: str
    backend: str | None = None


@dataclass(frozen=True)
class ResolutionResult:
    """Resultado de resolución de un import Cobra."""

    request: str
    source: str
    resolved_name: str
    import_path: str | None = None
    backend: str | None = None
    backend_adapter: object | None = None
    precedence_reason: str | None = None


API_CONTRACT_VERSION = "2026-04-import-resolution-v1"
RESOLUTION_SOURCE_ORDER: tuple[str, ...] = ("stdlib", "project", "python_bridge", "hybrid")
DEFAULT_COLLISION_POLICY = "namespace_required"
# Backward-compatible alias (internal histórico).
_SOURCE_ORDER: tuple[str, ...] = RESOLUTION_SOURCE_ORDER
_SUPPORTED_COLLISION_POLICIES: frozenset[str] = frozenset(
    {"warn", "strict_error", "namespace_required"}
)


class CobraImportResolver:
    """Resuelve imports con prioridad fija y conflictos explícitos."""
    resolution_source_order = RESOLUTION_SOURCE_ORDER
    default_collision_policy = DEFAULT_COLLISION_POLICY
    api_contract_version = API_CONTRACT_VERSION

    def __init__(
        self,
        *,
        project_root: str | Path | None = None,
        hybrid_modules: Mapping[str, HybridModuleSpec | Mapping[str, Any]] | None = None,
        default_backend: str = "python",
        strict_ambiguous_imports: bool = False,
        collision_policy: str | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve() if project_root else None
        config = get_toml_map()
        self.hybrid_modules = self._load_hybrid_modules(config, hybrid_modules)
        assert_backend_allowed_for_scope(backend=default_backend, scope="public")
        self.default_backend = default_backend
        self.collision_policy = self._resolve_collision_policy(
            config=config,
            strict_ambiguous_imports=strict_ambiguous_imports,
            explicit_policy=collision_policy,
        )
        self.stdlib_modules = self._load_stdlib_modules()
        self.project_modules = self._load_project_modules()

    def _load_hybrid_modules(
        self,
        config: Mapping[str, Any],
        explicit_modules: Mapping[str, HybridModuleSpec | Mapping[str, Any]] | None,
    ) -> dict[str, HybridModuleSpec]:
        declared_in_config = self._hybrid_modules_from_config(config)
        declared_explicit = self._normalize_hybrid_modules(explicit_modules or {})
        declared_in_config.update(declared_explicit)
        return declared_in_config

    @staticmethod
    def _hybrid_modules_from_config(config: Mapping[str, Any]) -> dict[str, HybridModuleSpec]:
        imports_section = config.get("imports", {})
        if not isinstance(imports_section, Mapping):
            return {}
        raw_hybrid = imports_section.get("hybrid_modules", {})
        if not isinstance(raw_hybrid, Mapping):
            return {}
        return CobraImportResolver._normalize_hybrid_modules(raw_hybrid)

    @staticmethod
    def _resolve_collision_policy(
        *,
        config: Mapping[str, Any],
        strict_ambiguous_imports: bool,
        explicit_policy: str | None,
    ) -> str:
        if strict_ambiguous_imports:
            return "strict_error"

        configured_policy = CobraImportResolver._collision_policy_from_config(config)
        migration_policy = (
            "warn" if CobraImportResolver._is_migration_mode_enabled(config) else None
        )
        chosen = explicit_policy or configured_policy or migration_policy or DEFAULT_COLLISION_POLICY
        if chosen not in _SUPPORTED_COLLISION_POLICIES:
            raise ImportResolutionError(
                "Política de colisiones inválida. "
                "Usa 'warn', 'strict_error' o 'namespace_required'."
            )
        return chosen

    @staticmethod
    def _collision_policy_from_config(config: Mapping[str, Any]) -> str | None:
        imports_section = config.get("imports", {})
        if not isinstance(imports_section, Mapping):
            return None
        policy = imports_section.get("collision_policy")
        if isinstance(policy, str):
            return policy.strip()
        return None

    @staticmethod
    def _is_migration_mode_enabled(config: Mapping[str, Any]) -> bool:
        imports_section = config.get("imports", {})
        if not isinstance(imports_section, Mapping):
            return False
        migration_mode = imports_section.get("migration_mode")
        return migration_mode is True

    @staticmethod
    def _normalize_hybrid_modules(
        modules: Mapping[str, HybridModuleSpec | Mapping[str, Any]],
    ) -> dict[str, HybridModuleSpec]:
        normalized: dict[str, HybridModuleSpec] = {}
        for name, raw in modules.items():
            if isinstance(raw, HybridModuleSpec):
                normalized[name] = raw
                continue
            import_path = str(raw.get("import_path", name))
            backend = raw.get("backend")
            normalized[name] = HybridModuleSpec(
                module=str(raw.get("module", name)),
                import_path=import_path,
                backend=str(backend) if isinstance(backend, str) else None,
            )
        return normalized

    @staticmethod
    def _load_stdlib_modules() -> dict[str, dict[str, object]]:
        contracts = get_public_stdlib_module_contracts()
        return {name: metadata for name, metadata in contracts.items() if name.startswith("cobra.")}

    @staticmethod
    def _load_project_modules() -> set[str]:
        config = get_toml_map()
        if not isinstance(config, dict):
            return set()
        modulos = config.get("modulos", {})
        if not isinstance(modulos, dict):
            return set()
        return {name for name, value in modulos.items() if isinstance(name, str) and isinstance(value, dict)}

    def resolve(self, module_name: str) -> ResolutionResult:
        name = (module_name or "").strip()
        if not name:
            raise ImportResolutionError("Nombre de módulo vacío")

        candidates: list[ResolutionResult] = []
        for source in RESOLUTION_SOURCE_ORDER:
            candidate = self._build_candidate(source, name)
            if candidate is not None:
                candidates.append(candidate)

        if not candidates:
            raise ImportResolutionError(f"No se encontró módulo para '{name}'")

        precedence_reason = (
            f"unique_source:{candidates[0].source}"
            if len(candidates) == 1
            else f"source_order:{' > '.join(RESOLUTION_SOURCE_ORDER)}"
        )

        if "." not in name and len(candidates) > 1:
            details = ", ".join(f"{c.source}:{c.resolved_name}" for c in candidates)
            message = (
                f"Colisión de import para '{name}'. Se aplica precedencia fija "
                f"({RESOLUTION_SOURCE_ORDER[0]} > {RESOLUTION_SOURCE_ORDER[1]} > "
                f"{RESOLUTION_SOURCE_ORDER[2]} > {RESOLUTION_SOURCE_ORDER[3]}). "
                f"Seleccionado: {candidates[0].resolved_name}. Candidatos: {details}. "
                f"Conflicto potencial: comando/import corto como 'importar {name}' puede colisionar "
                f"con módulo local '{name}'. Recomendación explícita: usa 'cobra.{name}' para stdlib "
                f"o 'app.{name}' para módulo de proyecto."
            )
            if self.collision_policy in {"strict_error", "namespace_required"}:
                suffix = (
                    " Modo namespace_required: debes importar con namespace explícito."
                    if self.collision_policy == "namespace_required"
                    else " Activa resolución explícita en strict mode."
                )
                raise ImportResolutionError(f"{message}{suffix}")
            warnings.warn(message, category=UserWarning, stacklevel=2)

        selected = ResolutionResult(
            request=candidates[0].request,
            source=candidates[0].source,
            resolved_name=candidates[0].resolved_name,
            import_path=candidates[0].import_path,
            backend=candidates[0].backend,
            backend_adapter=candidates[0].backend_adapter,
            precedence_reason=precedence_reason,
        )
        return self._attach_backend_adapter(selected)

    def load_module(
        self,
        module_name: str,
        fallback_backend: str = "python",
    ) -> tuple[ResolutionResult, ModuleType | None]:
        """Carga módulo Python cuando aplique usando el resultado resuelto."""

        resolution = self.resolve(module_name)
        if resolution.import_path is None:
            return resolution, None

        module = importlib.import_module(resolution.import_path)
        if resolution.backend:
            setattr(module, "__cobra_backend__", resolution.backend)
        if resolution.backend_adapter is not None:
            setattr(module, "__cobra_backend_adapter__", resolution.backend_adapter)
        elif fallback_backend:
            effective_backend = resolve_backend_for_module(
                resolution.resolved_name,
                fallback_backend,
            )
            adapter = resolve_backend(effective_backend)
            setattr(module, "__cobra_backend__", effective_backend)
            setattr(module, "__cobra_backend_adapter__", adapter)
        self._attach_module_metadata(module, resolution)
        return resolution, module

    def _attach_module_metadata(self, module: ModuleType, resolution: ResolutionResult) -> None:
        metadata = {
            "api_contract_version": API_CONTRACT_VERSION,
            "resolution_source_order": list(RESOLUTION_SOURCE_ORDER),
            "collision_policy": self.collision_policy,
            "request": resolution.request,
            "source": resolution.source,
            "resolved_name": resolution.resolved_name,
            "backend": resolution.backend,
            "import_path": resolution.import_path,
            "precedence_reason": resolution.precedence_reason,
        }
        setattr(module, "__cobra_resolution_source__", resolution.source)
        setattr(module, "__cobra_backend_injected__", resolution.backend)
        setattr(module, "__cobra_resolution_metadata__", metadata)

    def _attach_backend_adapter(self, resolution: ResolutionResult) -> ResolutionResult:
        base_backend = resolution.backend or self.default_backend
        effective_backend = resolve_backend_for_module(resolution.resolved_name, base_backend)
        assert_backend_allowed_for_scope(backend=effective_backend, scope="public")
        adapter = resolve_backend(effective_backend)
        return ResolutionResult(
            request=resolution.request,
            source=resolution.source,
            resolved_name=resolution.resolved_name,
            import_path=resolution.import_path,
            backend=effective_backend,
            backend_adapter=adapter,
            precedence_reason=resolution.precedence_reason,
        )

    def _build_candidate(self, source: str, name: str) -> ResolutionResult | None:
        if source == "stdlib":
            return self._resolve_stdlib_module(name)
        if source == "project":
            return self._resolve_project_module(name)
        if source == "python_bridge":
            return self._resolve_python_bridge(name)
        if source == "hybrid":
            return self._resolve_hybrid_module(name)
        return None

    def _resolve_project_module(self, name: str) -> ResolutionResult | None:
        if name in self.project_modules:
            return ResolutionResult(request=name, source="project", resolved_name=name)

        file_candidate = self._resolve_local_file_module(name)
        if file_candidate is not None:
            return file_candidate
        return None

    def _resolve_local_file_module(self, name: str) -> ResolutionResult | None:
        if self.project_root is None:
            return None

        relative = Path(*name.split("."))
        local_patterns = (
            relative.with_suffix(".co"),
            relative.with_suffix(".cobra"),
            relative / "__init__.co",
            relative / "__init__.cobra",
        )
        for pattern in local_patterns:
            if (self.project_root / pattern).exists():
                return ResolutionResult(
                    request=name,
                    source="project",
                    resolved_name=name,
                )
        return None

    def _resolve_stdlib_module(self, name: str) -> ResolutionResult | None:
        if name.startswith("cobra."):
            metadata = self.stdlib_modules.get(name)
            if metadata is not None:
                return ResolutionResult(
                    request=name,
                    source="stdlib",
                    resolved_name=name,
                    import_path=self._cobra_stdlib_to_python(name),
                    backend=(
                        str(metadata["backend_preferido"])
                        if isinstance(metadata.get("backend_preferido"), str)
                        else None
                    ),
                )
            return None

        qualified = f"cobra.{name}"
        metadata = self.stdlib_modules.get(qualified)
        if metadata is not None:
            return ResolutionResult(
                request=name,
                source="stdlib",
                resolved_name=qualified,
                import_path=self._cobra_stdlib_to_python(qualified),
                backend=(
                    str(metadata["backend_preferido"])
                    if isinstance(metadata.get("backend_preferido"), str)
                    else None
                ),
            )
        return None

    @staticmethod
    def _cobra_stdlib_to_python(qualified_name: str) -> str:
        tail = qualified_name.removeprefix("cobra.")
        return f"pcobra.standard_library.{tail}"

    @staticmethod
    def _resolve_python_bridge(name: str) -> ResolutionResult | None:
        if name.startswith("cobra."):
            return None
        if importlib.util.find_spec(name) is None:
            return None
        return ResolutionResult(
            request=name,
            source="python_bridge",
            resolved_name=name,
            import_path=name,
        )

    def _resolve_hybrid_module(self, name: str) -> ResolutionResult | None:
        spec = self.hybrid_modules.get(name)
        if spec is None:
            return None
        return ResolutionResult(
            request=name,
            source="hybrid",
            resolved_name=spec.module,
            import_path=spec.import_path,
            backend=spec.backend,
        )
