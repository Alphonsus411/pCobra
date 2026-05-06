"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

import inspect
import logging
from importlib import import_module
from importlib.metadata import entry_points
from types import MappingProxyType
from typing import Final

from pcobra.cobra.architecture.backend_policy import (
    ALL_BACKENDS,
    PUBLIC_BACKENDS,
    assert_public_targets_contract,
)
from pcobra.cobra.config.transpile_targets import OFFICIAL_TARGETS

TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
}

# Bloque dedicado de compatibilidad interna (no público).
INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}

PUBLIC_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = TRANSPILER_CLASS_PATHS

# Alias explícito para continuidad semántica en módulos/tests internos.
def _internal_compat_legacy_contracts():
    """Carga diferida de contratos legacy internos (no públicos)."""
    from pcobra.cobra.internal_compat.legacy_contracts import (
        INTERNAL_BACKENDS,
        INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
        lifecycle_status_for_backend,
    )

    return {
        "INTERNAL_BACKENDS": INTERNAL_BACKENDS,
        "INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW": INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
        "lifecycle_status_for_backend": lifecycle_status_for_backend,
    }


INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = (
    INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS
)


def _validate_complete_registry_contract() -> tuple[str, ...]:
    """Valida que el inventario completo preserve el contrato total de backends."""
    configured_keys = tuple(TRANSPILER_CLASS_PATHS) + tuple(
        INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS
    )
    missing = tuple(target for target in ALL_BACKENDS if target not in configured_keys)
    extras = tuple(target for target in configured_keys if target not in ALL_BACKENDS)

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS + INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS tienen claves fuera de contrato y deben usar exactamente ALL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )

    if len(configured_keys) != len(ALL_BACKENDS):
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS + INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS tienen cardinalidad inválida. "
            f"len(current)={len(configured_keys)}; len(expected)={len(ALL_BACKENDS)}; "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )

    if configured_keys != ALL_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS + INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS deben preservar el orden de backend_policy.ALL_BACKENDS. "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )
    return configured_keys


def _validate_public_registry_contract() -> tuple[str, ...]:
    """Valida contrato estricto del registro público frente a OFFICIAL_TARGETS/PUBLIC_BACKENDS."""
    assert_public_targets_contract(
        OFFICIAL_TARGETS,
        source="transpilers.registry.OFFICIAL_TARGETS",
    )

    configured_keys = tuple(PUBLIC_TRANSPILER_CLASS_PATHS)
    missing = tuple(target for target in PUBLIC_BACKENDS if target not in configured_keys)
    extras = tuple(target for target in configured_keys if target not in PUBLIC_BACKENDS)

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] PUBLIC_TRANSPILER_CLASS_PATHS debe usar exactamente PUBLIC_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={PUBLIC_BACKENDS}"
        )

    if configured_keys != PUBLIC_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] PUBLIC_TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.PUBLIC_BACKENDS. "
            f"current={configured_keys}; expected={PUBLIC_BACKENDS}"
        )
    return configured_keys


def _validate_internal_legacy_registry_contract() -> tuple[str, ...]:
    """Valida inventario separado para backends legacy internos."""
    contracts = _internal_compat_legacy_contracts()
    internal_backends = contracts["INTERNAL_BACKENDS"]
    internal_retirement_window = contracts["INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW"]

    configured_keys = tuple(INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS)
    missing = tuple(
        target for target in internal_backends if target not in configured_keys
    )
    extras = tuple(
        target for target in configured_keys if target not in internal_backends
    )

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS debe usar exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={internal_backends}"
        )

    lifecycle_keys = set(internal_retirement_window)
    internal_keys = set(internal_backends)
    if lifecycle_keys != internal_keys:
        extras = tuple(sorted(lifecycle_keys - internal_keys))
        missing = tuple(sorted(internal_keys - lifecycle_keys))
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW debe cubrir "
            "exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}"
        )

    if configured_keys != internal_backends:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.INTERNAL_BACKENDS. "
            f"current={configured_keys}; expected={internal_backends}"
        )
    return configured_keys


_ORDERED_ALL_TARGETS: Final[tuple[str, ...]] = _validate_complete_registry_contract()
_ORDERED_OFFICIAL_TARGETS: Final[tuple[str, ...]] = _validate_public_registry_contract()
_ORDERED_INTERNAL_LEGACY_TARGETS_CACHE: tuple[str, ...] | None = None
_OFFICIAL_TARGETS_SET: Final[frozenset[str]] = frozenset(_ORDERED_OFFICIAL_TARGETS)


def _ordered_internal_legacy_targets() -> tuple[str, ...]:
    """Resuelve y cachea el orden de backends legacy internos de forma lazy."""
    global _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE
    if _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE is None:
        _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE = _validate_internal_legacy_registry_contract()
    return _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE

_PLUGIN_TRANSPILERS: dict[str, type] = {}
_ENTRYPOINTS_LOADED = False


def ordered_official_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el registro público en el orden de ``OFFICIAL_TARGETS``."""
    return tuple(
        (target, PUBLIC_TRANSPILER_CLASS_PATHS[target])
        for target in _ORDERED_OFFICIAL_TARGETS
    )


def ordered_internal_legacy_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el inventario legacy interno en orden contractual."""
    return tuple(
        (target, INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS[target])
        for target in _ordered_internal_legacy_targets()
    )


def ordered_internal_legacy_transpiler_entries() -> tuple[tuple[str, tuple[str, str], str], ...]:
    """Devuelve inventario interno legacy con etiqueta de estado lifecycle."""
    contracts = _internal_compat_legacy_contracts()
    lifecycle_status_for_backend = contracts["lifecycle_status_for_backend"]
    return tuple(
        (
            target,
            INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS[target],
            lifecycle_status_for_backend(target),
        )
        for target in _ordered_internal_legacy_targets()
    )


def build_official_transpilers() -> dict[str, type]:
    """Carga las clases públicas oficiales desde el registro público."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_official_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry


def _canonical_target_or_raise(backend: str, *, context: str, require_exact: bool = False) -> str:
    candidate = backend.strip().lower()
    if candidate not in _OFFICIAL_TARGETS_SET:
        raise ValueError(
            "Backend no permitido en {context}: {backend}. "
            "Los plugins/transpiladores externos solo pueden registrar targets oficiales canónicos: {supported}".format(
                context=context,
                backend=backend,
                supported=", ".join(_ORDERED_OFFICIAL_TARGETS),
            )
        )
    if require_exact and backend != candidate:
        raise ValueError(
            "Backend no permitido en {context}: {backend}. "
            "Los entry points solo pueden usar nombres canónicos oficiales: {supported}".format(
                context=context,
                backend=backend,
                supported=", ".join(_ORDERED_OFFICIAL_TARGETS),
            )
        )
    return candidate


def _validate_transpiler_class_or_raise(transpiler_cls, *, backend: str, context: str) -> None:
    if not isinstance(transpiler_cls, type):
        raise ValueError(
            "Contrato inválido para backend '{backend}' en {context}: "
            "se esperaba una clase, recibido {type_name}.".format(
                backend=backend,
                context=context,
                type_name=type(transpiler_cls).__name__,
            )
        )
    generate_code = getattr(transpiler_cls, "generate_code", None)
    if not callable(generate_code):
        raise ValueError(
            "Contrato inválido para backend '{backend}' en {context}: "
            "la clase '{class_name}' no implementa el método callable 'generate_code'.".format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
            )
        )
    try:
        signature = inspect.signature(transpiler_cls)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Contrato inválido para backend '{backend}' en {context}: "
            "no se pudo inspeccionar la firma de '{class_name}': {cause}".format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
                cause=exc,
            )
        ) from exc

    required_params = [
        p.name
        for p in signature.parameters.values()
        if p.default is inspect.Signature.empty
        and p.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    ]
    if required_params:
        raise ValueError(
            "Contrato inválido para backend '{backend}' en {context}: "
            "la clase '{class_name}' requiere argumentos de inicialización ({params}). "
            "El protocolo soportado por plugins exige constructor sin argumentos.".format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
                params=", ".join(required_params),
            )
        )


def register_transpiler_backend(backend: str, transpiler_cls, *, context: str) -> str:
    """Registra plugins externos sobre targets oficiales canónicos sin duplicados."""
    canonical = _canonical_target_or_raise(backend, context=context)
    if backend != canonical:
        raise ValueError(
            "Backend no permitido en {context}: {backend}. "
            "Los plugins deben usar nombres canónicos oficiales sin alias: {supported}".format(
                context=context,
                backend=backend,
                supported=", ".join(_ORDERED_OFFICIAL_TARGETS),
            )
        )
    _validate_transpiler_class_or_raise(
        transpiler_cls,
        backend=canonical,
        context=context,
    )
    if canonical in _PLUGIN_TRANSPILERS:
        raise ValueError(
            "Registro duplicado en {context}: ya existe un plugin para backend '{backend}'.".format(
                context=context,
                backend=canonical,
            )
        )
    _PLUGIN_TRANSPILERS[canonical] = transpiler_cls
    return canonical


def plugin_transpilers() -> MappingProxyType:
    """Snapshot inmutable del overlay de plugins."""
    return MappingProxyType(dict(_PLUGIN_TRANSPILERS))


def _iter_transpiler_entry_points():
    try:
        return entry_points(group="cobra.transpilers")
    except TypeError:
        return entry_points().get("cobra.transpilers", [])


def load_entrypoint_transpilers() -> tuple[int, int, int]:
    loaded = 0
    rejected = 0
    skipped_existing = 0
    entrypoint_items = list(_iter_transpiler_entry_points())
    logging.info(
        "Iniciando carga de plugins de transpiladores por entry points: total=%d",
        len(entrypoint_items),
    )
    for ep in entrypoint_items:
        try:
            canonical_name = _canonical_target_or_raise(
                ep.name,
                context="plugins(entry_points)",
                require_exact=True,
            )
            module_name, class_name = ep.value.split(":", 1)
            if not all(c.isalnum() or c in "._" for c in module_name + class_name):
                raise ValueError(f"Nombre de módulo o clase inválido: {ep.value}")
            cls = getattr(import_module(module_name), class_name)
            if canonical_name in _PLUGIN_TRANSPILERS:
                logging.warning(
                    "Plugin de transpilador '%s' omitido: '%s' ya existe en el registro canónico",
                    ep.name,
                    canonical_name,
                )
                skipped_existing += 1
                continue
            register_transpiler_backend(canonical_name, cls, context="plugins(entry_points)")
            loaded += 1
        except ValueError as exc:
            rejected += 1
            logging.error(
                "Plugin de transpilador '%s' rechazado por política/contrato: %s",
                ep.name,
                exc,
            )
        except Exception as exc:
            rejected += 1
            logging.error("Error cargando transpilador '%s': %s", ep.name, exc)
    logging.info(
        (
            "Carga de plugins de transpiladores finalizada: "
            "total=%d cargados=%d rechazados=%d omitidos=%d"
        ),
        len(entrypoint_items),
        loaded,
        rejected,
        skipped_existing,
    )
    return loaded, rejected, skipped_existing


def ensure_entrypoint_transpilers_loaded_once() -> None:
    global _ENTRYPOINTS_LOADED
    if _ENTRYPOINTS_LOADED:
        logging.debug("Carga de plugins por entry points omitida: ya fue ejecutada.")
        return
    load_entrypoint_transpilers()
    _ENTRYPOINTS_LOADED = True


def get_transpilers(
    *,
    include_plugins: bool = True,
    ensure_entrypoints_loaded: bool = True,
) -> dict[str, type]:
    """Registro consolidado oficial (+ overlay de plugins si se habilita)."""
    if include_plugins and ensure_entrypoints_loaded:
        ensure_entrypoint_transpilers_loaded_once()
    registry = build_official_transpilers()
    if include_plugins:
        registry.update(_PLUGIN_TRANSPILERS)
    return registry


def build_internal_legacy_transpilers() -> dict[str, type]:
    """Carga las clases legacy internas para procesos de migración interna."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_internal_legacy_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry


def official_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets del registro público en el orden contractual."""
    return _ORDERED_OFFICIAL_TARGETS


def official_transpiler_module_filenames() -> tuple[str, ...]:
    """Devuelve los nombres de archivo ``to_*.py`` canónicos del registro oficial."""
    return tuple(
        module_name.rsplit(".", 1)[-1] + ".py"
        for _, (module_name, _) in ordered_official_transpiler_paths()
    )


def official_transpiler_registry_literal() -> dict[str, tuple[str, str]]:
    """Devuelve el literal esperado del registro canónico para auditorías."""
    return {target: value for target, value in ordered_official_transpiler_paths()}
