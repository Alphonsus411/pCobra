"""Resolvedor de imports Cobra con estrategia determinista por origen."""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping

from pcobra.cobra.backends.resolver import resolve_backend
from pcobra.cobra.transpilers.module_map import get_stdlib_contracts, resolve_backend_for_module


class ImportResolutionError(RuntimeError):
    """Error base al resolver imports Cobra."""


class AmbiguousImportError(ImportResolutionError):
    """Error determinista para imports ambiguos sin calificación de namespace."""


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



_SOURCE_PRIORITY: dict[str, int] = {
    "local": 1,
    "stdlib": 2,
    "python_bridge": 3,
    "hybrid": 4,
}

class CobraImportResolver:
    """Resuelve imports con prioridad fija y conflictos explícitos."""

    def __init__(
        self,
        *,
        project_root: str | Path | None = None,
        hybrid_modules: Mapping[str, HybridModuleSpec | Mapping[str, Any]] | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve() if project_root else None
        self.hybrid_modules = self._normalize_hybrid_modules(hybrid_modules or {})
        self.stdlib_modules = self._load_stdlib_modules()

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
    def _load_stdlib_modules() -> set[str]:
        contracts = get_stdlib_contracts()
        return {name for name in contracts if name.startswith("cobra.")}

    def resolve(self, module_name: str) -> ResolutionResult:
        name = (module_name or "").strip()
        if not name:
            raise ImportResolutionError("Nombre de módulo vacío")

        candidates: list[ResolutionResult] = []

        local_candidate = self._resolve_local_module(name)
        if local_candidate is not None:
            candidates.append(local_candidate)

        stdlib_candidate = self._resolve_stdlib_module(name)
        if stdlib_candidate is not None:
            candidates.append(stdlib_candidate)

        python_candidate = self._resolve_python_bridge(name)
        if python_candidate is not None:
            candidates.append(python_candidate)

        hybrid_candidate = self._resolve_hybrid_module(name)
        if hybrid_candidate is not None:
            candidates.append(hybrid_candidate)

        if not candidates:
            raise ImportResolutionError(f"No se encontró módulo para '{name}'")

        sorted_candidates = sorted(candidates, key=lambda c: _SOURCE_PRIORITY[c.source])
        top_priority = _SOURCE_PRIORITY[sorted_candidates[0].source]
        top_candidates = [
            candidate
            for candidate in sorted_candidates
            if _SOURCE_PRIORITY[candidate.source] == top_priority
        ]

        if "." not in name and len(sorted_candidates) > 1:
            has_local = any(candidate.source == "local" for candidate in sorted_candidates)
            if not has_local or len(top_candidates) > 1:
                details = ", ".join(
                    f"{c.source}:{c.resolved_name}" for c in sorted_candidates
                )
                raise AmbiguousImportError(
                    f"Import ambiguo sin namespace para '{name}'. "
                    f"Use un nombre calificado. Candidatos: {details}"
                )

        return sorted_candidates[0]

    def load_module(self, module_name: str, fallback_backend: str = "python") -> tuple[ResolutionResult, ModuleType | None]:
        """Carga módulo Python cuando aplique e inyecta adapter de backend."""

        resolution = self.resolve(module_name)
        if resolution.import_path is None:
            return resolution, None

        module = importlib.import_module(resolution.import_path)
        backend = resolution.backend or fallback_backend
        backend = resolve_backend_for_module(resolution.resolved_name, backend)
        adapter = resolve_backend(backend)
        setattr(module, "__cobra_backend__", backend)
        setattr(module, "__cobra_backend_adapter__", adapter)
        return resolution, module

    def _resolve_local_module(self, name: str) -> ResolutionResult | None:
        if self.project_root is None:
            return None
        if name.startswith("cobra."):
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
                    source="local",
                    resolved_name=name,
                )
        return None

    def _resolve_stdlib_module(self, name: str) -> ResolutionResult | None:
        if name.startswith("cobra."):
            if name in self.stdlib_modules:
                return ResolutionResult(
                    request=name,
                    source="stdlib",
                    resolved_name=name,
                    import_path=self._cobra_stdlib_to_python(name),
                )
            return None

        qualified = f"cobra.{name}"
        if qualified in self.stdlib_modules:
            return ResolutionResult(
                request=name,
                source="stdlib",
                resolved_name=qualified,
                import_path=self._cobra_stdlib_to_python(qualified),
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
