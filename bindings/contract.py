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


OFFICIAL_PUBLIC_LANGUAGES: Final[tuple[str, ...]] = ("python", "javascript", "rust")
PUBLIC_RUNTIME_COMMANDS: Final[tuple[str, ...]] = ("run", "build", "test")
EVENT_VALIDATION_FIELDS: Final[tuple[str, ...]] = (
    "language",
    "route",
    "bridge",
    "abi_version",
    "sandbox",
    "containerized",
)

OFFICIAL_PUBLIC_ROUTE_MATRIX: Final[dict[str, BindingRoute]] = {
    "python": BindingRoute.PYTHON_DIRECT_IMPORT,
    "javascript": BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE,
    "rust": BindingRoute.RUST_COMPILED_FFI,
}


@dataclass(frozen=True, slots=True)
class BindingCapabilities:
    """Describe capacidades y restricciones contractuales por ruta."""

    route: BindingRoute
    language: str
    import_strategy: str
    execution_boundary: str
    abi_contract: str
    managed_runtime: bool


@dataclass(frozen=True, slots=True)
class AbiCompatibilityPolicy:
    """Matriz ABI por ruta y política explícita de compatibilidad."""

    current: str
    supported: tuple[str, ...]
    backwards_compatible_with: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RouteOperationalLimits:
    """Límites operativos contractuales por ruta de binding."""

    process_model: str
    isolation_boundary: str
    ffi_boundary: str
    sandbox_support: str
    container_support: str


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

ABI_POLICY_BY_ROUTE: Final[dict[BindingRoute, AbiCompatibilityPolicy]] = {
    BindingRoute.PYTHON_DIRECT_IMPORT: AbiCompatibilityPolicy(
        current="1.0",
        supported=("1.0",),
        backwards_compatible_with=("1.0",),
    ),
    BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: AbiCompatibilityPolicy(
        current="1.1",
        supported=("1.1", "1.0"),
        backwards_compatible_with=("1.0",),
    ),
    BindingRoute.RUST_COMPILED_FFI: AbiCompatibilityPolicy(
        current="2.0",
        supported=("2.0", "1.1", "1.0"),
        backwards_compatible_with=("1.1", "1.0"),
    ),
}

ROUTE_OPERATIONAL_LIMITS: Final[dict[BindingRoute, RouteOperationalLimits]] = {
    BindingRoute.PYTHON_DIRECT_IMPORT: RouteOperationalLimits(
        process_model="Mismo proceso del runtime principal",
        isolation_boundary="Sin aislamiento de proceso; depende de safe_mode/validadores",
        ffi_boundary="No aplica (sin frontera FFI nativa)",
        sandbox_support="Soportado en sandbox Python",
        container_support="No soportado como ruta directa",
    ),
    BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE: RouteOperationalLimits(
        process_model="Proceso/VM de runtime JS gestionado",
        isolation_boundary="Aislamiento obligatorio (sandbox JS o contenedor)",
        ffi_boundary="No usa FFI nativa; IPC/mensajería versionada",
        sandbox_support="Soportado en sandbox de runtime gestionado",
        container_support="Soportado y recomendado para pruebas reproducibles",
    ),
    BindingRoute.RUST_COMPILED_FFI: RouteOperationalLimits(
        process_model="Proceso principal + librería nativa cargada",
        isolation_boundary="Frontera nativa por ABI/FFI",
        ffi_boundary="Requiere ABI explícita y artefactos compilados",
        sandbox_support="No soportado en sandbox Python",
        container_support="Soportado para aislamiento operativo",
    ),
}

COMMAND_EVENT_SCHEMA: Final[dict[str, str]] = {
    command: f"runtime.command.validation.{command}" for command in PUBLIC_RUNTIME_COMMANDS
}


def resolve_binding(language: str) -> BindingCapabilities:
    """Resuelve el contrato de bindings para un lenguaje canónico."""

    key = validate_public_language(language)
    try:
        return BINDINGS_BY_LANGUAGE[key]
    except KeyError as exc:
        raise ValueError(
            f"No existe contrato de bindings para '{language}'. "
            f"Lenguajes soportados: {', '.join(sorted(BINDINGS_BY_LANGUAGE))}."
        ) from exc


def validate_public_language(language: str) -> str:
    """Valida temprano que el lenguaje pertenezca a la superficie pública oficial."""

    key = (language or "").strip().lower()
    if key in OFFICIAL_PUBLIC_LANGUAGES:
        return key

    raise ValueError(
        "Lenguaje no permitido en rutas públicas de bindings: "
        f"'{language}'. Lenguajes oficiales: {', '.join(OFFICIAL_PUBLIC_LANGUAGES)}."
    )


def route_matrix_markdown() -> str:
    """Documenta la matriz oficial de rutas públicas de bindings."""

    return "\n".join(
        (
            "| Lenguaje | Ruta oficial |", 
            "| --- | --- |",
            "| Python | direct import bridge |",
            "| JavaScript | runtime bridge |",
            "| Rust | compiled FFI |",
        )
    )


def resolve_command_event(command: str) -> str:
    """Resuelve el nombre de evento canónico por comando público."""

    key = (command or "").strip().lower()
    try:
        return COMMAND_EVENT_SCHEMA[key]
    except KeyError as exc:
        raise ValueError(
            "Comando no soportado para eventos contractuales: "
            f"'{command}'. Comandos oficiales: {', '.join(PUBLIC_RUNTIME_COMMANDS)}."
        ) from exc


__all__ = [
    "AbiCompatibilityPolicy",
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "OFFICIAL_PUBLIC_LANGUAGES",
    "PUBLIC_RUNTIME_COMMANDS",
    "OFFICIAL_PUBLIC_ROUTE_MATRIX",
    "ABI_POLICY_BY_ROUTE",
    "COMMAND_EVENT_SCHEMA",
    "EVENT_VALIDATION_FIELDS",
    "ROUTE_OPERATIONAL_LIMITS",
    "RouteOperationalLimits",
    "JAVASCRIPT_BINDING",
    "PYTHON_BINDING",
    "RUST_BINDING",
    "route_matrix_markdown",
    "resolve_command_event",
    "validate_public_language",
    "resolve_binding",
]
