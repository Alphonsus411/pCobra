"""Políticas centralizadas de targets para comandos CLI."""

from __future__ import annotations

from argparse import ArgumentTypeError
from typing import Literal

from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    BEST_EFFORT_RUNTIME_BACKENDS,
    CONTRACT_FEATURES,
    OFFICIAL_RUNTIME_BACKENDS,
    SDK_FULL_BACKENDS,
    TRANSPILATION_ONLY_BACKENDS,
)
from pcobra.cobra.transpilers.target_utils import (
    DEPRECATION_WINDOW_REMOVAL_VERSION,
    LEGACY_OR_AMBIGUOUS_TARGETS,
    build_target_help_by_tier,
    deprecation_window_text,
    format_target_sequence,
    normalize_target_name,
    retired_target_migration_hint,
    require_exact_official_targets,
    require_official_target_subset,
    target_cli_choices,
)
from pcobra.cobra.config.transpile_targets import LEGACY_INTERNAL_TARGETS
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

RenderMarkup = Literal["plain", "markdown", "rst"]


ACCEPTED_TARGET_ALIASES: tuple[tuple[str, str], ...] = ()


def accepted_target_aliases_examples_text() -> str:
    """No existen aliases aceptados en la superficie pública actual."""
    return "sin aliases públicos"


# Todos los destinos oficiales de generación/transpilación.
OFFICIAL_TRANSPILATION_TARGETS = require_exact_official_targets(
    OFFICIAL_TARGETS,
    context="pcobra.cobra.cli.target_policies.OFFICIAL_TRANSPILATION_TARGETS",
)

# Targets oficiales con tooling oficial de ejecución en contenedor/sandbox Docker.
OFFICIAL_RUNTIME_TARGETS = target_cli_choices(
    tuple(target for target in OFFICIAL_RUNTIME_BACKENDS if target in OFFICIAL_TRANSPILATION_TARGETS)
)

# Targets best-effort conservados fuera del contrato oficial de runtime.
BEST_EFFORT_RUNTIME_TARGETS = target_cli_choices(
    tuple(target for target in BEST_EFFORT_RUNTIME_BACKENDS if target in OFFICIAL_TRANSPILATION_TARGETS)
)

# Targets oficiales que hoy son solo de generación y no prometen runtime.
TRANSPILATION_ONLY_TARGETS = target_cli_choices(
    tuple(target for target in TRANSPILATION_ONLY_BACKENDS if target in OFFICIAL_TRANSPILATION_TARGETS)
)

# Targets sin runtime automatizado en la CLI/suite actual.
NO_RUNTIME_TARGETS = TRANSPILATION_ONLY_TARGETS

# Alias semántico conservado para la UX existente.
DOCKER_EXECUTABLE_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Backend runtime que espera ``core.sandbox.ejecutar_en_contenedor``.
DOCKER_RUNTIME_BY_TARGET: dict[str, str] = {target: target for target in OFFICIAL_RUNTIME_TARGETS}

# Targets oficiales cuyo runtime también puede verificarse ejecutando realmente
# el código generado desde la CLI/suite actual.
VERIFICATION_EXECUTABLE_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Targets con soporte oficial de librerías base (`corelibs`/`standard_library`)
# a nivel de runtime mantenido y verificable por el proyecto.
OFFICIAL_STANDARD_LIBRARY_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Targets con adaptador Holobit mantenido oficialmente por el proyecto.
# Esto no equivale a compatibilidad SDK total: fuera de Python sigue siendo
# compatibilidad parcial según ``compatibility_matrix.py``.
ADVANCED_HOLOBIT_RUNTIME_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Compatibilidad SDK completa: se deriva de la matriz contractual.
SDK_COMPATIBLE_TARGETS = target_cli_choices(
    tuple(target for target in SDK_FULL_BACKENDS if target in OFFICIAL_TRANSPILATION_TARGETS)
)

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


def _validate_runtime_categories_contract() -> None:
    """Asegura que runtime/best-effort/transpilación-only particionen el canon."""
    category_map = {
        "OFFICIAL_RUNTIME_TARGETS": OFFICIAL_RUNTIME_TARGETS,
        "BEST_EFFORT_RUNTIME_TARGETS": BEST_EFFORT_RUNTIME_TARGETS,
        "TRANSPILATION_ONLY_TARGETS": TRANSPILATION_ONLY_TARGETS,
    }
    canonical_set = set(OFFICIAL_TRANSPILATION_TARGETS)
    category_sets = {name: set(values) for name, values in category_map.items()}

    for name, values in category_map.items():
        missing = tuple(target for target in values if target not in canonical_set)
        if missing:
            raise RuntimeError(
                f"{name} contiene targets fuera del canon oficial. "
                f"out_of_contract={missing}; canonical={OFFICIAL_TRANSPILATION_TARGETS}"
            )

    overlap_pairs = []
    category_names = tuple(category_map)
    for index, left in enumerate(category_names):
        for right in category_names[index + 1 :]:
            overlap = tuple(sorted(category_sets[left] & category_sets[right]))
            if overlap:
                overlap_pairs.append((left, right, overlap))
    if overlap_pairs:
        overlaps = "; ".join(
            f"{left}∩{right}={overlap}" for left, right, overlap in overlap_pairs
        )
        raise RuntimeError(
            "Las categorías de targets no deben solaparse entre sí. "
            f"{overlaps}; canonical={OFFICIAL_TRANSPILATION_TARGETS}"
        )

    partition_union = (
        category_sets["OFFICIAL_RUNTIME_TARGETS"]
        | category_sets["BEST_EFFORT_RUNTIME_TARGETS"]
        | category_sets["TRANSPILATION_ONLY_TARGETS"]
    )
    missing_from_partition = tuple(
        target for target in OFFICIAL_TRANSPILATION_TARGETS if target not in partition_union
    )
    extras_in_partition = tuple(
        target for target in partition_union if target not in canonical_set
    )
    if missing_from_partition or extras_in_partition:
        raise RuntimeError(
            "La partición OFFICIAL/BEST_EFFORT/TRANSPILATION_ONLY debe cubrir exactamente el canon. "
            f"missing={missing_from_partition or '∅'}; extras={extras_in_partition or '∅'}; "
            f"partition={tuple(sorted(partition_union))}; canonical={OFFICIAL_TRANSPILATION_TARGETS}"
        )


_validate_runtime_categories_contract()

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


def legacy_internal_targets_text() -> str:
    return ", ".join(LEGACY_INTERNAL_TARGETS)


def build_cli_compile_examples(
    *,
    source_file: str = "programa.co",
    command_prefix: str = "cobra compilar",
) -> tuple[str, ...]:
    """Construye ejemplos CLI canónicos sin listas hardcodeadas."""
    return tuple(
        f"{command_prefix} {source_file} --backend {backend}"
        for backend in OFFICIAL_TRANSPILATION_TARGETS
    )


def iter_public_policy_items() -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Devuelve las categorías públicas que deben reutilizar CLI/docs/tests."""
    return (
        ("official_targets", "Targets oficiales de transpilación", OFFICIAL_TRANSPILATION_TARGETS),
        ("official_runtime_targets", "Targets con runtime oficial verificable (full SDK solo en python)", OFFICIAL_RUNTIME_TARGETS),
        ("verification_targets", "Targets con verificación ejecutable explícita en CLI", VERIFICATION_EXECUTABLE_TARGETS),
        ("best_effort_runtime_targets", "Targets con runtime best-effort", BEST_EFFORT_RUNTIME_TARGETS),
        (
            "official_standard_library_targets",
            "Targets con soporte oficial mantenido de `corelibs`/`standard_library` (partial fuera de python)",
            OFFICIAL_STANDARD_LIBRARY_TARGETS,
        ),
        (
            "advanced_holobit_runtime_targets",
            "Targets con adaptador Holobit mantenido por el proyecto (partial fuera de python)",
            ADVANCED_HOLOBIT_RUNTIME_TARGETS,
        ),
        ("sdk_compatible_targets", "Compatibilidad SDK completa (solo python)", SDK_COMPATIBLE_TARGETS),
        (
            "transpilation_only_targets",
            "Targets solo de transpilación",
            TRANSPILATION_ONLY_TARGETS,
        ),
        (
            "legacy_internal_targets",
            "Targets legacy/internal (no públicos)",
            LEGACY_INTERNAL_TARGETS,
        ),
    )


def render_public_policy_summary(*, markup: RenderMarkup = "plain") -> str:
    """Renderiza el resumen público de política sin duplicar listas manuales."""
    lines = [
        "- **Backends oficiales de salida**: "
        + str(len(OFFICIAL_TRANSPILATION_TARGETS))
        + " targets canónicos."
    ]
    lines.extend(
        f"- **{label}**: {format_target_sequence(targets, markup=markup)}."
        for _, label, targets in iter_public_policy_items()
    )
    return "\n".join(lines)


def render_reverse_scope_summary(reverse_scope: tuple[str, ...], *, markup: RenderMarkup = "plain") -> str:
    """Renderiza la línea pública de orígenes reverse oficiales."""
    official_targets_count = len(OFFICIAL_TRANSPILATION_TARGETS)
    return (
        "- **Orígenes de transpilación inversa**: "
        + format_target_sequence(reverse_scope, markup=markup)
        + f". Este alcance reverse de entrada está separado de los {official_targets_count} targets oficiales de salida."
    )


def build_runtime_capability_message(*, capability: str, allowed_targets: tuple[str, ...]) -> str:
    official_targets_count = len(OFFICIAL_TRANSPILATION_TARGETS)
    return (
        "Targets oficiales de salida: {official}. "
        "Targets con runtime oficial para {capability}: {allowed}. "
        "Compatibilidad SDK completa: {sdk_compatible}. "
        "Targets best-effort: {best_effort}. "
        "Targets solo de transpilación: {transpilation_only}. "
        "Generar código para los {official_count} targets oficiales no implica paridad de ejecución real."
    ).format(
        official=official_transpilation_targets_text(),
        capability=capability,
        allowed=", ".join(allowed_targets),
        sdk_compatible=sdk_compatible_targets_text(),
        best_effort=", ".join(BEST_EFFORT_RUNTIME_TARGETS),
        transpilation_only=transpilation_only_targets_text(),
        official_count=official_targets_count,
    )


def _sdk_full_targets_from_matrix() -> tuple[str, ...]:
    """Deriva targets SDK full desde la matriz contractual canonical."""
    return tuple(
        backend
        for backend in OFFICIAL_TRANSPILATION_TARGETS
        if all(BACKEND_COMPATIBILITY[backend][feature] == "full" for feature in CONTRACT_FEATURES)
    )


def validate_runtime_support_contract() -> None:
    """Valida que las promesas públicas de runtime no contradigan la matriz contractual."""
    from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY

    runtime_targets = set(OFFICIAL_RUNTIME_TARGETS)
    best_effort_targets = set(BEST_EFFORT_RUNTIME_TARGETS)
    transpilation_only_targets = set(TRANSPILATION_ONLY_TARGETS)
    official_targets = set(OFFICIAL_TRANSPILATION_TARGETS)

    if runtime_targets & best_effort_targets:
        raise RuntimeError(
            "OFFICIAL_RUNTIME_TARGETS y BEST_EFFORT_RUNTIME_TARGETS deben ser disjuntos: "
            f"runtime={OFFICIAL_RUNTIME_TARGETS}, best_effort={BEST_EFFORT_RUNTIME_TARGETS}"
        )

    if runtime_targets & transpilation_only_targets:
        raise RuntimeError(
            "OFFICIAL_RUNTIME_TARGETS y TRANSPILATION_ONLY_TARGETS deben ser disjuntos: "
            f"runtime={OFFICIAL_RUNTIME_TARGETS}, transpilation_only={TRANSPILATION_ONLY_TARGETS}"
        )

    if best_effort_targets & transpilation_only_targets:
        raise RuntimeError(
            "BEST_EFFORT_RUNTIME_TARGETS y TRANSPILATION_ONLY_TARGETS deben ser disjuntos: "
            f"best_effort={BEST_EFFORT_RUNTIME_TARGETS}, transpilation_only={TRANSPILATION_ONLY_TARGETS}"
        )

    if runtime_targets | best_effort_targets | transpilation_only_targets != official_targets:
        raise RuntimeError(
            "Los targets oficiales deben particionarse exactamente en runtime oficial, best-effort y solo transpilación: "
            f"official={OFFICIAL_TRANSPILATION_TARGETS}, runtime={OFFICIAL_RUNTIME_TARGETS}, "
            f"best_effort={BEST_EFFORT_RUNTIME_TARGETS}, transpilation_only={TRANSPILATION_ONLY_TARGETS}"
        )

    if set(NO_RUNTIME_TARGETS) != transpilation_only_targets:
        raise RuntimeError(
            "NO_RUNTIME_TARGETS debe coincidir exactamente con TRANSPILATION_ONLY_TARGETS: "
            f"no_runtime={NO_RUNTIME_TARGETS}, transpilation_only={TRANSPILATION_ONLY_TARGETS}"
        )

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


    if SDK_COMPATIBLE_TARGETS != ("python",):
        raise RuntimeError(
            "SDK_COMPATIBLE_TARGETS debe permanecer fijado a ('python',): "
            f"sdk={SDK_COMPATIBLE_TARGETS}"
        )

    matrix_sdk_targets = _sdk_full_targets_from_matrix()
    if SDK_COMPATIBLE_TARGETS != matrix_sdk_targets:
        raise RuntimeError(
            "SDK_COMPATIBLE_TARGETS debe coincidir con los backends 'full' de la matriz contractual: "
            f"sdk={SDK_COMPATIBLE_TARGETS}, matrix={matrix_sdk_targets}"
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
    valid_with_tier = official_targets_with_tier_text()
    return (
        "Target no soportado: '{value}'. Usa uno canónico oficial de la matriz: {supported}. "
        "Lista exacta válida (target=tier): {valid_with_tier}."
    ).format(
        value=value.strip(),
        supported=official_transpilation_targets_text(),
        valid_with_tier=valid_with_tier,
    )


def legacy_or_ambiguous_target_error(value: str) -> str:
    valid_with_tier = official_targets_with_tier_text()
    lowered = value.strip().lower()
    migration_hint = retired_target_migration_hint(lowered)
    return (
        "Target no permitido por nombre legacy/ambiguo: '{value}'. "
        "Este nombre está retirado ({window}; "
        "migración obligatoria antes de v{removal}). "
        "{migration_hint}. "
        "Usa solo nombres canónicos oficiales: {supported}. "
        "Lista exacta válida (target=tier): {valid_with_tier}."
    ).format(
        value=value.strip(),
        window=deprecation_window_text(),
        removal=DEPRECATION_WINDOW_REMOVAL_VERSION,
        migration_hint=migration_hint.capitalize(),
        supported=official_transpilation_targets_text(),
        valid_with_tier=valid_with_tier,
    )


def official_targets_with_tier_rows() -> tuple[tuple[str, str], ...]:
    """Devuelve el listado canónico target->tier derivado de la matriz oficial."""
    return tuple(
        (
            target,
            BACKEND_COMPATIBILITY[target]["tier"],
        )
        for target in OFFICIAL_TRANSPILATION_TARGETS
    )


def official_targets_with_tier_text() -> str:
    """Renderiza ``target=tier`` para mensajes de error contractuales."""
    return ", ".join(
        f"{target}={tier}" for target, tier in official_targets_with_tier_rows()
    )


def restricted_target_error(*, unsupported: list[str], capability: str, allowed_targets: tuple[str, ...]) -> str:
    best_effort_unsupported = [target for target in unsupported if target in BEST_EFFORT_RUNTIME_TARGETS]
    transpilation_only_unsupported = [target for target in unsupported if target in TRANSPILATION_ONLY_TARGETS]
    unsupported_labels: list[str] = []
    if best_effort_unsupported:
        unsupported_labels.append(
            "targets best-effort " + ", ".join(best_effort_unsupported)
        )
    if transpilation_only_unsupported:
        unsupported_labels.append(
            "targets solo de transpilación " + ", ".join(transpilation_only_unsupported)
        )
    if not unsupported_labels:
        unsupported_labels.append(", ".join(unsupported))

    return (
        "Los {unsupported} son targets oficiales de salida, "
        "pero no tienen runtime oficial para {capability}. "
        "Targets con runtime oficial: {runtime}. "
        "Targets best-effort: {best_effort}. "
        "Targets solo de transpilación: {transpilation_only}. "
        "Generar código para esos targets no implica paridad de ejecución real "
        "ni compatibilidad SDK completa. Usa solo: {allowed}."
    ).format(
        unsupported="; ".join(unsupported_labels),
        capability=capability,
        runtime=official_runtime_targets_text(),
        best_effort=", ".join(BEST_EFFORT_RUNTIME_TARGETS),
        transpilation_only=transpilation_only_targets_text(),
        allowed=", ".join(allowed_targets),
    )


def parse_target(value: str) -> str:
    """Valida target CLI aceptando solo nombres canónicos oficiales."""
    raw = value.strip()
    if not raw:
        raise ArgumentTypeError(invalid_target_error(value))
    lowered = raw.lower()
    if lowered in LEGACY_OR_AMBIGUOUS_TARGETS:
        raise ArgumentTypeError(legacy_or_ambiguous_target_error(value))
    canonical = normalize_target_name(raw)
    if canonical not in OFFICIAL_TARGETS:
        raise ArgumentTypeError(invalid_target_error(value))
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
