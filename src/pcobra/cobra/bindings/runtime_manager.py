"""Manager unificado para resolver y validar rutas de bindings/runtime."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from pcobra.cobra.bindings.contract import (
    ABI_POLICY_BY_ROUTE,
    BINDINGS_BY_LANGUAGE,
    OFFICIAL_PUBLIC_ROUTE_MATRIX,
    BindingCapabilities,
    BindingRoute,
    resolve_binding,
    validate_public_language,
)

DEFAULT_ABI_VERSION: Final[str] = "1.0"

SECURITY_POLICY_BY_COMMAND: Final[dict[str, dict[BindingRoute, dict[str, bool]]]] = {
    "run": {
        BindingRoute.PYTHON_DIRECT_IMPORT: {"sandbox_required": False, "container_required": False},
        BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: {"sandbox_required": False, "container_required": False},
        BindingRoute.RUST_COMPILED_FFI: {"sandbox_required": False, "container_required": False},
    },
    "test": {
        BindingRoute.PYTHON_DIRECT_IMPORT: {"sandbox_required": True, "container_required": False},
        BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: {"sandbox_required": False, "container_required": True},
        BindingRoute.RUST_COMPILED_FFI: {"sandbox_required": False, "container_required": True},
    },
    "build": {
        BindingRoute.PYTHON_DIRECT_IMPORT: {"sandbox_required": False, "container_required": False},
        BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: {"sandbox_required": False, "container_required": False},
        BindingRoute.RUST_COMPILED_FFI: {"sandbox_required": False, "container_required": False},
    },
}


@dataclass(frozen=True, slots=True)
class RuntimeBridgeDescriptor:
    """Describe la implementación de bridge concreta para una ruta contractual."""

    route: BindingRoute
    implementation: str
    security_profile: str
    abi_version: str
    internal_only: bool = True


class RuntimeManager:
    """Resuelve rutas de binding y centraliza validaciones de seguridad/ABI."""

    _ROUTE_LABEL_BY_ROUTE: Final[dict[BindingRoute, str]] = {
        BindingRoute.PYTHON_DIRECT_IMPORT: "Python direct import",
        BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: "JavaScript runtime bridge",
        BindingRoute.RUST_COMPILED_FFI: "Rust compiled FFI",
    }

    _BRIDGES: Final[dict[BindingRoute, RuntimeBridgeDescriptor]] = {
        BindingRoute.PYTHON_DIRECT_IMPORT: RuntimeBridgeDescriptor(
            route=BindingRoute.PYTHON_DIRECT_IMPORT,
            implementation="python_direct_bridge",
            security_profile="same_process_safe_mode",
            abi_version=ABI_POLICY_BY_ROUTE[BindingRoute.PYTHON_DIRECT_IMPORT].current,
            internal_only=False,
        ),
        BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: RuntimeBridgeDescriptor(
            route=BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE,
            implementation="javascript_controlled_runtime_bridge",
            security_profile="managed_runtime_isolation",
            abi_version=ABI_POLICY_BY_ROUTE[BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE].current,
            internal_only=False,
        ),
        BindingRoute.RUST_COMPILED_FFI: RuntimeBridgeDescriptor(
            route=BindingRoute.RUST_COMPILED_FFI,
            implementation="rust_compiled_ffi_bridge",
            security_profile="native_ffi_boundary",
            abi_version=ABI_POLICY_BY_ROUTE[BindingRoute.RUST_COMPILED_FFI].current,
            internal_only=False,
        ),
    }

    def __init__(self) -> None:
        self._validate_public_contracts()

    def resolve_runtime(self, language: str) -> tuple[BindingCapabilities, RuntimeBridgeDescriptor]:
        """Resuelve contrato, negocia ABI y retorna bridge asociado."""

        capabilities = self._resolve_capabilities(language)
        bridge = self.select_bridge(capabilities)
        self.negotiate_abi(capabilities)
        return capabilities, bridge

    def _resolve_capabilities(self, language: str) -> BindingCapabilities:
        validate_public_language(language)
        return resolve_binding(language)

    def validate_security_route(
        self,
        language: str,
        *,
        sandbox: bool = False,
        containerized: bool = False,
        command: str = "run",
    ) -> None:
        """Valida seguridad por ruta contractual y política del comando."""

        normalized_command = (command or "run").strip().lower()
        if normalized_command not in SECURITY_POLICY_BY_COMMAND:
            allowed = ", ".join(sorted(SECURITY_POLICY_BY_COMMAND))
            raise ValueError(f"Comando '{command}' no soportado en política de seguridad. Use: {allowed}.")

        capabilities = self._resolve_capabilities(language)
        route = capabilities.route

        # Validación base por ruta
        if route is BindingRoute.PYTHON_DIRECT_IMPORT and containerized:
            self._raise_route_error(
                route,
                "la ruta no puede marcarse como containerizada; use ejecución en mismo proceso",
            )
        if route is BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE and not (sandbox or containerized):
            self._raise_route_error(
                route,
                "la ruta requiere runtime gestionado (sandbox o contenedor) para mantener aislamiento",
            )
        if route is BindingRoute.RUST_COMPILED_FFI and sandbox:
            self._raise_route_error(
                route,
                "la ruta usa frontera nativa FFI y no se ejecuta en sandbox Python directo",
            )

        # Validación por comando público
        command_policy = SECURITY_POLICY_BY_COMMAND[normalized_command][route]
        if command_policy["sandbox_required"] and not sandbox:
            raise ValueError(
                f"La política '{normalized_command}' exige sandbox para la ruta {route.value}."
            )
        if command_policy["container_required"] and not containerized:
            raise ValueError(
                f"La política '{normalized_command}' exige contenedor para la ruta {route.value}."
            )

    def negotiate_abi(self, capabilities: BindingCapabilities, abi_version: str | None = None) -> str:
        """Negocia ABI por ruta usando matriz canónica y compatibilidad hacia atrás."""

        policy = ABI_POLICY_BY_ROUTE[capabilities.route]
        project_selected = abi_version or self._resolve_project_abi_for_backend(capabilities.language)
        selected = (project_selected or policy.current or DEFAULT_ABI_VERSION).strip()

        if selected not in policy.supported:
            raise ValueError(
                f"ABI '{selected}' no soportada para '{capabilities.language}'. "
                f"Versiones soportadas: {', '.join(policy.supported)}."
            )

        if selected == policy.current:
            return selected

        if selected in policy.backwards_compatible_with:
            return selected

        raise ValueError(
            f"ABI '{selected}' está soportada pero no es compatible hacia atrás "
            f"con la versión actual '{policy.current}' para '{capabilities.language}'."
        )

    def validate_abi_route(self, language: str, abi_version: str | None = None) -> str:
        """Wrapper público para mantener compatibilidad con llamadas existentes."""

        capabilities = self._resolve_capabilities(language)
        return self.negotiate_abi(capabilities, abi_version)

    def validate_command_runtime(
        self,
        language: str,
        *,
        command: str,
        sandbox: bool = False,
        containerized: bool = False,
        abi_version: str | None = None,
    ) -> tuple[str, BindingCapabilities, RuntimeBridgeDescriptor]:
        """Valida de forma canónica seguridad+ABI para un comando público."""

        capabilities, bridge = self.resolve_runtime(language)
        self.validate_security_route(
            language,
            sandbox=sandbox,
            containerized=containerized,
            command=command,
        )
        negotiated_abi = self.negotiate_abi(capabilities, abi_version)
        return negotiated_abi, capabilities, bridge

    def select_bridge(self, capabilities: BindingCapabilities) -> RuntimeBridgeDescriptor:
        """Selecciona la implementación de bridge para una ruta contractual."""

        return self._BRIDGES[capabilities.route]

    @classmethod
    def _validate_public_contracts(cls) -> None:
        expected_languages = set(OFFICIAL_PUBLIC_ROUTE_MATRIX)
        binding_languages = set(BINDINGS_BY_LANGUAGE)
        if binding_languages != expected_languages:
            extras = sorted(binding_languages - expected_languages)
            missing = sorted(expected_languages - binding_languages)
            raise RuntimeError(
                "Contrato de bindings públicos inválido. "
                f"missing={missing or '∅'}; extras={extras or '∅'}"
            )

        for language, route in OFFICIAL_PUBLIC_ROUTE_MATRIX.items():
            capabilities = BINDINGS_BY_LANGUAGE[language]
            if capabilities.route is not route:
                raise RuntimeError(
                    "Matriz oficial inconsistente entre lenguaje y ruta. "
                    f"language={language}; expected={route.value}; got={capabilities.route.value}"
                )

        for route, descriptor in cls._BRIDGES.items():
            if route in OFFICIAL_PUBLIC_ROUTE_MATRIX.values():
                if descriptor.internal_only:
                    raise RuntimeError(
                        f"Bridge oficial '{descriptor.implementation}' no puede ser internal_only."
                    )
                continue
            if not descriptor.internal_only:
                raise RuntimeError(
                    "Bridge no oficial expuesto sin bandera internal_only. "
                    f"route={route.value}; implementation={descriptor.implementation}"
                )

    def _raise_route_error(self, route: BindingRoute, detail: str) -> None:
        route_label = self._ROUTE_LABEL_BY_ROUTE[route]
        raise ValueError(f"[{route_label}] {detail}.")

    def _resolve_project_abi_for_backend(self, backend: str) -> str | None:
        """Obtiene ABI negociada por backend desde cobra.toml/pcobra.toml."""

        normalized_backend = (backend or "").strip().lower()
        if not normalized_backend:
            return None

        for config_path in self._project_config_candidates():
            data = self._load_toml(config_path)
            if not isinstance(data, dict):
                continue
            project = data.get("project")
            if not isinstance(project, dict):
                continue

            for key in ("abi_by_backend", "backend_abi"):
                mapping = project.get(key)
                if not isinstance(mapping, dict):
                    continue
                abi_value = mapping.get(normalized_backend)
                if isinstance(abi_value, str) and abi_value.strip():
                    return abi_value.strip()
        return None

    def _project_config_candidates(self) -> tuple[Path, ...]:
        root = Path.cwd()
        cobra = Path(os.environ.get("COBRA_TOML", str(root / "cobra.toml")))
        pcobra = Path(os.environ.get("PCOBRA_CONFIG", str(root / "pcobra.toml")))
        return cobra, pcobra

    @staticmethod
    def _load_toml(path: Path) -> dict:
        if not path.exists() or not path.is_file():
            return {}
        try:
            with path.open("rb") as handle:
                data = tomllib.load(handle)
                return data if isinstance(data, dict) else {}
        except (OSError, tomllib.TOMLDecodeError):
            return {}


SUPPORTED_ABI_VERSIONS: Final[dict[BindingRoute, tuple[str, ...]]] = {
    route: policy.supported for route, policy in ABI_POLICY_BY_ROUTE.items()
}

__all__ = [
    "DEFAULT_ABI_VERSION",
    "SUPPORTED_ABI_VERSIONS",
    "SECURITY_POLICY_BY_COMMAND",
    "RuntimeBridgeDescriptor",
    "RuntimeManager",
]
