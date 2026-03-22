"""Políticas centralizadas de targets para comandos CLI."""

from __future__ import annotations

from argparse import ArgumentTypeError
from typing import Literal

from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    build_target_help_by_tier,
    format_target_sequence,
    normalize_target_name,
    require_official_target_subset,
    target_cli_choices,
)

RenderMarkup = Literal["plain", "markdown", "rst"]

# Todos los destinos oficiales de generación/transpilación.
OFFICIAL_TRANSPILATION_TARGETS = tuple(OFFICIAL_TARGETS)

# Targets oficiales con tooling oficial de ejecución en contenedor/sandbox Docker.
OFFICIAL_RUNTIME_TARGETS = target_cli_choices(("python", "javascript", "cpp", "rust"))

# Targets oficiales que hoy son solo de generación y no prometen runtime oficial.
TRANSPILATION_ONLY_TARGETS = tuple(
    target for target in OFFICIAL_TRANSPILATION_TARGETS if target not in OFFICIAL_RUNTIME_TARGETS
)

# Targets best-effort conservados fuera del contrato oficial de runtime.
BEST_EFFORT_RUNTIME_TARGETS = target_cli_choices(("go", "java"))

# Targets sin runtime automatizado en la CLI/suite actual.
NO_RUNTIME_TARGETS = tuple(
    target for target in TRANSPILATION_ONLY_TARGETS if target not in BEST_EFFORT_RUNTIME_TARGETS
)

# Alias semántico conservado para la UX existente.
DOCKER_EXECUTABLE_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Backend runtime que espera ``core.sandbox.ejecutar_en_contenedor``.
DOCKER_RUNTIME_BY_TARGET: dict[str, str] = {target: target for target in OFFICIAL_RUNTIME_TARGETS}

# Targets oficiales cuyo runtime también puede verificarse ejecutando realmente
# el código generado desde la CLI/suite actual.
VERIFICATION_EXECUTABLE_TARGETS = target_cli_choices(("python", "javascript", "cpp", "rust"))

# Targets con soporte oficial de librerías base (`corelibs`/`standard_library`)
# a nivel de runtime mantenido y verificable por el proyecto.
OFFICIAL_STANDARD_LIBRARY_TARGETS = target_cli_choices(("python", "javascript", "cpp", "rust"))

# Targets con adaptador Holobit mantenido oficialmente por el proyecto.
# Esto no equivale a compatibilidad SDK total: fuera de Python sigue siendo
# compatibilidad parcial según ``compatibility_matrix.py``.
ADVANCED_HOLOBIT_RUNTIME_TARGETS = target_cli_choices(("python", "javascript", "cpp", "rust"))

# Compatibilidad SDK completa: hoy solo Python puede prometerla públicamente.
SDK_COMPATIBLE_TARGETS = target_cli_choices(("python",))

require_official_target_subset(
    OFFICIAL_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.OFFICIAL_RUNTIME_TARGETS",
)
require_official_target_subset(
    VERIFICATION_EXECUTABLE_TARGETS,
    context="pcobra.cobra.cli.target_policies.VERIFICATION_EXECUTABLE_TARGETS",
)
require_official_target_subset(
    BEST_EFFORT_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.BEST_EFFORT_RUNTIME_TARGETS",
)
require_official_target_subset(
    NO_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.NO_RUNTIME_TARGETS",
)
require_official_target_subset(
    OFFICIAL_STANDARD_LIBRARY_TARGETS,
    context="pcobra.cobra.cli.target_policies.OFFICIAL_STANDARD_LIBRARY_TARGETS",
)
require_official_target_subset(
    ADVANCED_HOLOBIT_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.ADVANCED_HOLOBIT_RUNTIME_TARGETS",
)
require_official_target_subset(
    SDK_COMPATIBLE_TARGETS,
    context="pcobra.cobra.cli.target_policies.SDK_COMPATIBLE_TARGETS",
)

OFFICIAL_TRANSPILATION_TARGETS_HELP = build_target_help_by_tier(OFFICIAL_TRANSPILATION_TARGETS)
OFFICIAL_RUNTIME_TARGETS_HELP = build_target_help_by_tier(OFFICIAL_RUNTIME_TARGETS)
VERIFICATION_EXECUTABLE_TARGETS_HELP = build_target_help_by_tier(VERIFICATION_EXECUTABLE_TARGETS)


def official_transpilation_targets_text() -> str:
    return ", ".join(OFFICIAL_TRANSPILATION_TARGETS)


def official_runtime_targets_text() -> str:
    return ", ".join(OFFICIAL_RUNTIME_TARGETS)


def verification_runtime_targets_text() -> str:
    return ", ".join(VERIFICATION_EXECUTABLE_TARGETS)


def official_standard_library_targets_text() -> str:
    return ", ".join(OFFICIAL_STANDARD_LIBRARY_TARGETS)


def advanced_holobit_runtime_targets_text() -> str:
    return ", ".join(ADVANCED_HOLOBIT_RUNTIME_TARGETS)


def sdk_compatible_targets_text() -> str:
    return ", ".join(SDK_COMPATIBLE_TARGETS)


def transpilation_only_targets_text() -> str:
    return ", ".join(TRANSPILATION_ONLY_TARGETS)


def iter_public_policy_items() -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Devuelve las categorías públicas que deben reutilizar CLI/docs/tests."""
    return (
        ("official_targets", "Targets oficiales de transpilación", OFFICIAL_TRANSPILATION_TARGETS),
        ("official_runtime_targets", "Targets con runtime oficial verificable", OFFICIAL_RUNTIME_TARGETS),
        ("verification_targets", "Targets con verificación ejecutable explícita en CLI", VERIFICATION_EXECUTABLE_TARGETS),
        (
            "official_standard_library_targets",
            "Targets con soporte oficial mantenido de `corelibs`/`standard_library` en runtime",
            OFFICIAL_STANDARD_LIBRARY_TARGETS,
        ),
        (
            "advanced_holobit_runtime_targets",
            "Targets con adaptador Holobit mantenido por el proyecto",
            ADVANCED_HOLOBIT_RUNTIME_TARGETS,
        ),
        ("sdk_compatible_targets", "Compatibilidad SDK completa", SDK_COMPATIBLE_TARGETS),
        (
            "transpilation_only_targets",
            "Targets sin runtime oficial público aunque tengan generación de código",
            TRANSPILATION_ONLY_TARGETS,
        ),
    )


def render_public_policy_summary(*, markup: RenderMarkup = "plain") -> str:
    """Renderiza el resumen público de política sin duplicar listas manuales."""
    return "\n".join(
        f"- **{label}**: {format_target_sequence(targets, markup=markup)}."
        for _, label, targets in iter_public_policy_items()
    )


def render_reverse_scope_summary(reverse_scope: tuple[str, ...], *, markup: RenderMarkup = "plain") -> str:
    """Renderiza la línea pública de orígenes reverse oficiales."""
    return (
        "- **Orígenes de transpilación inversa**: "
        + format_target_sequence(reverse_scope, markup=markup)
        + "."
    )


def build_runtime_capability_message(*, capability: str, allowed_targets: tuple[str, ...]) -> str:
    return (
        "Targets oficiales de transpilación: {official}. "
        "Solo tienen runtime oficial para {capability}: {allowed}. "
        "Los targets {non_runtime} siguen siendo salidas oficiales de generación de código, "
        "pero no equivalen a un runtime oficial ni a soporte oficial de librerías en ejecución. "
        "Targets solo transpilación: {transpilation_only}."
    ).format(
        official=official_transpilation_targets_text(),
        capability=capability,
        allowed=", ".join(allowed_targets),
        non_runtime=", ".join(TRANSPILATION_ONLY_TARGETS),
        transpilation_only=transpilation_only_targets_text(),
    )


def validate_runtime_support_contract() -> None:
    """Valida que las promesas públicas de runtime no contradigan la matriz contractual."""
    from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY

    if set(VERIFICATION_EXECUTABLE_TARGETS) != set(OFFICIAL_RUNTIME_TARGETS):
        raise RuntimeError(
            "VERIFICATION_EXECUTABLE_TARGETS debe cubrir exactamente los runtimes oficiales verificables: "
            f"runtime={OFFICIAL_RUNTIME_TARGETS}, verification={VERIFICATION_EXECUTABLE_TARGETS}"
        )

    if set(OFFICIAL_STANDARD_LIBRARY_TARGETS) != set(OFFICIAL_RUNTIME_TARGETS):
        raise RuntimeError(
            "OFFICIAL_STANDARD_LIBRARY_TARGETS debe coincidir con los backends de runtime oficial mantenido: "
            f"runtime={OFFICIAL_RUNTIME_TARGETS}, standard_library={OFFICIAL_STANDARD_LIBRARY_TARGETS}"
        )

    if set(ADVANCED_HOLOBIT_RUNTIME_TARGETS) != set(OFFICIAL_RUNTIME_TARGETS):
        raise RuntimeError(
            "ADVANCED_HOLOBIT_RUNTIME_TARGETS debe coincidir con los backends de runtime oficial con adaptador Holobit mantenido: "
            f"runtime={OFFICIAL_RUNTIME_TARGETS}, holobit={ADVANCED_HOLOBIT_RUNTIME_TARGETS}"
        )

    for backend in OFFICIAL_RUNTIME_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        if contract["corelibs"] == "none" or contract["standard_library"] == "none":
            raise RuntimeError(
                f"{backend} figura como runtime oficial pero no garantiza corelibs/standard_library ejecutables"
            )
        if any(
            contract[feature] == "none"
            for feature in ("holobit", "proyectar", "transformar", "graficar")
        ):
            raise RuntimeError(
                f"{backend} figura como runtime oficial pero no garantiza hooks Holobit mínimos"
            )

    for backend in SDK_COMPATIBLE_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        if any(
            contract[feature] != "full"
            for feature in (
                "holobit",
                "proyectar",
                "transformar",
                "graficar",
                "corelibs",
                "standard_library",
            )
        ):
            raise RuntimeError(
                f"{backend} figura como compatibilidad SDK completa sin cubrir todas las features en nivel full"
            )


validate_runtime_support_contract()


def invalid_target_error(value: str) -> str:
    return "Target no soportado: '{value}'. Usa uno canónico oficial: {supported}.".format(
        value=value.strip(),
        supported=official_transpilation_targets_text(),
    )


def restricted_target_error(*, unsupported: list[str], capability: str, allowed_targets: tuple[str, ...]) -> str:
    return (
        "Los targets {unsupported} son oficiales para transpilación, "
        "pero no tienen runtime oficial para {capability}. "
        "Generar código para esos targets no implica paridad de ejecución real "
        "ni soporte oficial de librerías equivalente a `python`, `rust`, `javascript` o `cpp`. "
        "Targets oficiales: {official}. Usa solo: {allowed}. "
        "Targets solo transpilación: {transpilation_only}."
    ).format(
        unsupported=", ".join(unsupported),
        capability=capability,
        official=official_transpilation_targets_text(),
        allowed=", ".join(allowed_targets),
        transpilation_only=transpilation_only_targets_text(),
    )


def parse_target(value: str) -> str:
    """Valida target CLI aceptando solo nombres canónicos oficiales."""
    canonical = normalize_target_name(value)
    if canonical not in OFFICIAL_TRANSPILATION_TARGETS:
        raise ArgumentTypeError(invalid_target_error(value))
    return canonical


def parse_runtime_target(value: str, *, allowed_targets: tuple[str, ...], capability: str) -> str:
    """Valida un target oficial restringido a una capacidad con runtime."""
    canonical = parse_target(value)
    if canonical not in allowed_targets:
        raise ArgumentTypeError(
            restricted_target_error(
                unsupported=[canonical],
                capability=capability,
                allowed_targets=allowed_targets,
            )
        )
    return canonical



def resolve_docker_backend(target: str) -> str:
    """Resuelve el backend de runtime Docker solo para nombres canónicos oficiales."""
    canonical = parse_runtime_target(
        target,
        allowed_targets=DOCKER_EXECUTABLE_TARGETS,
        capability="ejecución en contenedor",
    )
    return DOCKER_RUNTIME_BY_TARGET[canonical]

def parse_target_list(value: str) -> list[str]:
    """Valida una lista de targets separados por comas."""
    parsed = [parse_target(item) for item in value.split(",") if item.strip()]
    if not parsed:
        raise ArgumentTypeError("La lista de targets no puede estar vacía")
    return parsed


def parse_restricted_target_list(value: str, allowed_targets: tuple[str, ...], capability: str) -> list[str]:
    """Valida una lista de targets oficiales restringida a una capacidad concreta."""
    parsed = parse_target_list(value)
    unsupported = [target for target in parsed if target not in allowed_targets]
    if unsupported:
        raise ArgumentTypeError(
            restricted_target_error(
                unsupported=unsupported,
                capability=capability,
                allowed_targets=allowed_targets,
            )
        )
    return parsed
