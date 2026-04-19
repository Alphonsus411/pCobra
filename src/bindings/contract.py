"""Contrato técnico canónico de rutas de bindings entre Cobra y runtimes externos."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class BindingRoute(str, Enum):
    """Rutas soportadas por el bridge canónico de bindings."""

    PYTHON_DIRECT_IMPORT = "python_direct_import"
    JAVASCRIPT_RUNTIME_BRIDGE = "javascript_runtime_bridge"
    RUST_COMPILED_FFI = "rust_compiled_ffi"


@dataclass(frozen=True, slots=True)
class BindingCapabilities:
    """Describe capacidades y restricciones contractuales por ruta."""

    route: BindingRoute
    language: str
    import_strategy: str
    execution_boundary: str
    abi_contract: str
    managed_runtime: bool


PYTHON_BINDING: Final[BindingCapabilities] = BindingCapabilities(
    route=BindingRoute.PYTHON_DIRECT_IMPORT,
    language="python",
    import_strategy="Import bridge directo sobre módulos Python canónicos",
    execution_boundary="Mismo proceso del intérprete Cobra",
    abi_contract="Contrato Python estable por API pública y typing",
    managed_runtime=False,
)

JAVASCRIPT_BINDING: Final[BindingCapabilities] = BindingCapabilities(
    route=BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE,
    language="javascript",
    import_strategy="Bridge de runtime sobre proceso/VM controlada",
    execution_boundary="Aislado en runtime JS dedicado (proceso o VM)",
    abi_contract="Contrato de mensajes/IPC versionado",
    managed_runtime=True,
)

RUST_BINDING: Final[BindingCapabilities] = BindingCapabilities(
    route=BindingRoute.RUST_COMPILED_FFI,
    language="rust",
    import_strategy="Bindings compilados sobre capa FFI",
    execution_boundary="Frontera nativa vía librería compartida",
    abi_contract="ABI estable y versionada",
    managed_runtime=False,
)

BINDINGS_BY_LANGUAGE: Final[dict[str, BindingCapabilities]] = {
    "python": PYTHON_BINDING,
    "javascript": JAVASCRIPT_BINDING,
    "rust": RUST_BINDING,
}


def resolve_binding(language: str) -> BindingCapabilities:
    """Resuelve el contrato de bindings para un lenguaje canónico."""

    key = (language or "").strip().lower()
    try:
        return BINDINGS_BY_LANGUAGE[key]
    except KeyError as exc:
        raise ValueError(
            f"No existe contrato de bindings para '{language}'. "
            f"Lenguajes soportados: {', '.join(sorted(BINDINGS_BY_LANGUAGE))}."
        ) from exc


__all__ = [
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "JAVASCRIPT_BINDING",
    "PYTHON_BINDING",
    "RUST_BINDING",
    "resolve_binding",
]
