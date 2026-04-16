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
    BindingCapabilities,
    BindingRoute,
    resolve_binding,
)

DEFAULT_ABI_VERSION: Final[str] = "1.0"
SUPPORTED_ABI_VERSIONS: Final[dict[BindingRoute, tuple[str, ...]]] = {
    BindingRoute.PYTHON_DIRECT_IMPORT: ("1.0",),
    BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: ("1.0",),
    BindingRoute.RUST_COMPILED_FFI: ("1.0",),
}

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
}


@dataclass(frozen=True, slots=True)
class RuntimeBridgeDescriptor:
    """Describe la implementación de bridge concreta para una ruta contractual."""

    route: BindingRoute
    implementation: str
    security_profile: str
    abi_version: str


class RuntimeManager:
    """Resuelve rutas de binding y centraliza validaciones de seguridad/ABI."""

    _BRIDGES: Final[dict[BindingRoute, RuntimeBridgeDescriptor]] = {
        BindingRoute.PYTHON_DIRECT_IMPORT: RuntimeBridgeDescriptor(
            route=BindingRoute.PYTHON_DIRECT_IMPORT,
            implementation="python_direct_bridge",
            security_profile="same_process_safe_mode",
            abi_version=DEFAULT_ABI_VERSION,
        ),
        BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: RuntimeBridgeDescriptor(
            route=BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE,
            implementation="javascript_controlled_runtime_bridge",
            security_profile="managed_runtime_isolation",
            abi_version=DEFAULT_ABI_VERSION,
        ),
        BindingRoute.RUST_COMPILED_FFI: RuntimeBridgeDescriptor(
            route=BindingRoute.RUST_COMPILED_FFI,
            implementation="rust_compiled_ffi_bridge",
            security_profile="native_ffi_boundary",
            abi_version=DEFAULT_ABI_VERSION,
        ),
    }

    def resolve_runtime(self, language: str) -> tuple[BindingCapabilities, RuntimeBridgeDescriptor]:
        """Resuelve contrato y bridge asociado para un lenguaje."""

        capabilities = resolve_binding(language)
        bridge = self._BRIDGES[capabilities.route]
        return capabilities, bridge

    def validate_security_route(
        self,
        language: str,
        *,
        sandbox: bool = False,
        containerized: bool = False,
        command: str = "run",
    ) -> None:
        """Valida que la ruta elegida cumpla expectativas mínimas de seguridad."""

        normalized_command = (command or "run").strip().lower()
        if normalized_command not in SECURITY_POLICY_BY_COMMAND:
            allowed = ", ".join(sorted(SECURITY_POLICY_BY_COMMAND))
            raise ValueError(f"Comando '{command}' no soportado en política de seguridad. Use: {allowed}.")

        capabilities, _bridge = self.resolve_runtime(language)
        route = capabilities.route

        # Reglas base por tipo de ruta
        if route is BindingRoute.PYTHON_DIRECT_IMPORT and containerized:
            raise ValueError(
                "La ruta python_direct_import no puede marcarse como containerizada. "
                "Use bridge Python directo (mismo proceso) o ruta de runtime gestionado."
            )
        if route is BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE and not (sandbox or containerized):
            raise ValueError(
                "La ruta javascript_runtime_bridge requiere runtime gestionado "
                "(sandbox o contenedor) para mantener aislamiento."
            )
        if route is BindingRoute.RUST_COMPILED_FFI and sandbox:
            raise ValueError(
                "La ruta rust_compiled_ffi usa frontera nativa FFI y no se ejecuta "
                "en sandbox Python directo."
            )

        # Reglas por comando (run/test)
        command_policy = SECURITY_POLICY_BY_COMMAND[normalized_command][route]
        if command_policy["sandbox_required"] and not sandbox:
            raise ValueError(
                f"La política '{normalized_command}' exige sandbox para la ruta {route.value}."
            )
        if command_policy["container_required"] and not containerized:
            raise ValueError(
                f"La política '{normalized_command}' exige contenedor para la ruta {route.value}."
            )

    def validate_abi_route(self, language: str, abi_version: str | None = None) -> str:
        """Valida compatibilidad ABI de la ruta seleccionada."""

        capabilities, bridge = self.resolve_runtime(language)
        negotiated_abi = abi_version or self._resolve_project_abi_for_backend(capabilities.language)
        selected = (negotiated_abi or bridge.abi_version or DEFAULT_ABI_VERSION).strip()
        supported = SUPPORTED_ABI_VERSIONS[capabilities.route]
        if selected not in supported:
            raise ValueError(
                f"ABI '{selected}' no soportada para '{language}'. "
                f"Versiones soportadas: {', '.join(supported)}."
            )
        return selected

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


__all__ = [
    "DEFAULT_ABI_VERSION",
    "SUPPORTED_ABI_VERSIONS",
    "SECURITY_POLICY_BY_COMMAND",
    "RuntimeBridgeDescriptor",
    "RuntimeManager",
]
