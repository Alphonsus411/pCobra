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
from pcobra.cobra.transpilers.module_map import (
    get_stdlib_contracts,
    get_toml_map,
    resolve_backend_for_module,
)


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


_SOURCE_ORDER: tuple[str, ...] = ("stdlib", "project", "python_bridge", "hybrid")


class CobraImportResolver:
    """Resuelve imports con prioridad fija y conflictos explícitos."""

    def __init__(
        self,
        *,
        project_root: str | Path | None = None,
        hybrid_modules: Mapping[str, HybridModuleSpec | Mapping[str, Any]] | None = None,
        default_backend: str = "python",
        strict_ambiguous_imports: bool = False,
    ) -> None:
        self.project_root = Path(project_root).resolve() if project_root else None
        self.hybrid_modules = self._normalize_hybrid_modules(hybrid_modules or {})
        self.default_backend = default_backend
        self.strict_ambiguous_imports = strict_ambiguous_imports
        self.stdlib_modules = self._load_stdlib_modules()
        self.project_modules = self._load_project_modules()

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
        for source in _SOURCE_ORDER:
            candidate = self._build_candidate(source, name)
            if candidate is not None:
                candidates.append(candidate)

        if not candidates:
            raise ImportResolutionError(f"No se encontró módulo para '{name}'")

        if "." not in name and len(candidates) > 1:
            details = ", ".join(f"{c.source}:{c.resolved_name}" for c in candidates)
            message = (
                f"Colisión de import para '{name}'. Se aplica precedencia fija "
                f"({_SOURCE_ORDER[0]} > {_SOURCE_ORDER[1]} > {_SOURCE_ORDER[2]} > {_SOURCE_ORDER[3]}). "
                f"Seleccionado: {candidates[0].resolved_name}. Candidatos: {details}. "
                f"Recomendación: usa prefijo explícito ('cobra.{name}') para stdlib o namespace de proyecto "
                f"(por ejemplo 'app.{name}')."
            )
            if self.strict_ambiguous_imports:
                raise ImportResolutionError(f"{message} Activa resolución explícita en strict mode.")
            warnings.warn(message, category=UserWarning, stacklevel=2)

        return self._attach_backend_adapter(candidates[0])

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

    @staticmethod
    def _attach_module_metadata(module: ModuleType, resolution: ResolutionResult) -> None:
        metadata = {
            "request": resolution.request,
            "source": resolution.source,
            "resolved_name": resolution.resolved_name,
            "backend": resolution.backend,
            "import_path": resolution.import_path,
        }
        setattr(module, "__cobra_resolution_source__", resolution.source)
        setattr(module, "__cobra_backend_injected__", resolution.backend)
        setattr(module, "__cobra_resolution_metadata__", metadata)

    def _attach_backend_adapter(self, resolution: ResolutionResult) -> ResolutionResult:
        base_backend = resolution.backend or self.default_backend
        effective_backend = resolve_backend_for_module(resolution.resolved_name, base_backend)
        adapter = resolve_backend(effective_backend)
        return ResolutionResult(
            request=resolution.request,
            source=resolution.source,
            resolved_name=resolution.resolved_name,
            import_path=resolution.import_path,
            backend=effective_backend,
            backend_adapter=adapter,
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
