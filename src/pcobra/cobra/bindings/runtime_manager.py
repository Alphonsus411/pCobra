"""Manager unificado para resolver y validar rutas de bindings/runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

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
    ) -> None:
        """Valida que la ruta elegida cumpla expectativas mínimas de seguridad."""

        capabilities, _bridge = self.resolve_runtime(language)
        route = capabilities.route

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

    def validate_abi_route(self, language: str, abi_version: str | None = None) -> str:
        """Valida compatibilidad ABI de la ruta seleccionada."""

        capabilities, bridge = self.resolve_runtime(language)
        selected = (abi_version or bridge.abi_version or DEFAULT_ABI_VERSION).strip()
        supported = SUPPORTED_ABI_VERSIONS[capabilities.route]
        if selected not in supported:
            raise ValueError(
                f"ABI '{selected}' no soportada para '{language}'. "
                f"Versiones soportadas: {', '.join(supported)}."
            )
        return selected


__all__ = [
    "DEFAULT_ABI_VERSION",
    "SUPPORTED_ABI_VERSIONS",
    "RuntimeBridgeDescriptor",
    "RuntimeManager",
]
