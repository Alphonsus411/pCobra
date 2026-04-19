"""Utilidades comunes de política de targets para benchmarks.

La política oficial de targets se hereda de
``src/pcobra/cobra/architecture/backend_policy.py`` y no debe redefinirse en scripts.
"""

from __future__ import annotations

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # Fallback para Python < 3.11.
from pathlib import Path
from typing import Final, Mapping

from pcobra.cobra.architecture.backend_policy import ALL_BACKENDS, PUBLIC_BACKENDS
from pcobra.cobra.cli.target_policies import (
    BEST_EFFORT_RUNTIME_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
)
from pcobra.cobra.transpilers.registry import official_transpiler_targets
from pcobra.cobra.transpilers.target_utils import normalize_target_name, target_cli_choices

BEST_EFFORT_BENCHMARK_RUNTIME_TARGETS: Final[tuple[str, ...]] = BEST_EFFORT_RUNTIME_TARGETS
NO_RUNTIME_BENCHMARK_TARGETS: Final[tuple[str, ...]] = NO_RUNTIME_TARGETS

BENCHMARK_BACKEND_METADATA: Final[dict[str, dict[str, object]]] = {
    "python": {"ext": "py", "run": ["python", "{file}"], "runtime_policy": "official"},
    "javascript": {"ext": "js", "run": ["node", "{file}"], "runtime_policy": "official"},
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
        "runtime_policy": "official",
    },
    "wasm": {
        "ext": "wat",
        "compile": ["wat2wasm", "{file}", "-o", "{tmp}/prog.wasm"],
        "run": ["wasmtime", "{tmp}/prog.wasm"],
        "runtime_policy": "transpilation_only",
    },
    "go": {
        "ext": "go",
        "run": ["go", "run", "{file}"],
        "runtime_policy": "best_effort_non_public",
    },
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"],
        "runtime_policy": "official",
    },
    "java": {
        "ext": "java",
        "compile": ["javac", "{file}"],
        "run": ["java", "-cp", "{tmp}", "Main"],
        "runtime_policy": "best_effort_non_public",
    },
    "asm": {
        "ext": "s",
        "compile": ["gcc", "{file}", "-o", "{tmp}/prog_asm"],
        "run": ["{tmp}/prog_asm"],
        "runtime_policy": "transpilation_only",
    },
}

BINARY_BENCHMARK_METADATA: Final[dict[str, dict[str, object]]] = {
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"],
        "bin": "{tmp}/prog_cpp",
        "runtime_policy": "official",
    },
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
        "bin": "{tmp}/prog_rs",
        "runtime_policy": "official",
    },
    "java": {
        "ext": "java",
        "compile": ["javac", "{file}"],
        "run": ["java", "-cp", "{tmp}", "Main"],
        "bin": "{tmp}/Main.class",
        "runtime_policy": "best_effort_non_public",
    },
    "asm": {
        "ext": "s",
        "compile": ["gcc", "{file}", "-o", "{tmp}/prog_asm"],
        "run": ["{tmp}/prog_asm"],
        "bin": "{tmp}/prog_asm",
        "runtime_policy": "transpilation_only",
    },
    "wasm": {
        "ext": "wat",
        "compile": ["wat2wasm", "{file}", "-o", "{tmp}/prog.wasm"],
        "run": ["wasmtime", "{tmp}/prog.wasm"],
        "bin": "{tmp}/prog.wasm",
        "runtime_policy": "transpilation_only",
    },
}


def validate_local_targets_policy(repo_root: Path) -> None:
    """Valida que cobra.toml local no declare backends fuera de política oficial."""
    config_path = repo_root / "cobra.toml"
    if not config_path.exists():
        return

    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    project_cfg = config.get("project", {})
    raw_targets = project_cfg.get("required_targets", project_cfg.get("targets_requeridos"))
    if not raw_targets:
        return

    if not isinstance(raw_targets, list):
        raise RuntimeError(
            "Config local inválida: [project].required_targets debe ser una lista de backends oficiales."
        )

    unsupported = []
    for target in raw_targets:
        canonical = normalize_target_name(str(target))
        if canonical not in PUBLIC_BACKENDS:
            unsupported.append(str(target))
    if unsupported:
        raise RuntimeError(
            "Config local inválida: backends no oficiales en [project].required_targets: "
            f"{', '.join(unsupported)}. Oficiales: {', '.join(PUBLIC_BACKENDS)}"
        )



def validate_backend_metadata(backends: Mapping[str, object], *, context: str) -> None:
    """Falla rápido si falta metadata para backends conocidos o sobran claves."""
    configured = tuple(backends.keys())
    missing = tuple(target for target in ALL_BACKENDS if target not in configured)
    extras = tuple(target for target in configured if target not in ALL_BACKENDS)
    if missing or extras:
        raise RuntimeError(
            "Metadata de benchmarks fuera de contrato en {context}: missing={missing}; extras={extras}; "
            "expected={expected}; current={current}".format(
                context=context,
                missing=missing or "∅",
                extras=extras or "∅",
                expected=ALL_BACKENDS,
                current=configured,
            )
        )



def benchmark_backends(backends: Mapping[str, object] | None = None) -> tuple[str, ...]:
    """Devuelve backends benchmark públicos en orden canónico."""
    canonical = official_transpiler_targets()
    available_targets = canonical if backends is None else tuple(
        target for target in canonical if target in backends
    )
    return target_cli_choices(available_targets)


def executable_benchmark_backends(
    backends: Mapping[str, object] | None = None,
    *,
    include_experimental: bool = False,
) -> tuple[str, ...]:
    """Devuelve solo backends con runtime utilizable por benchmarks ejecutables.

    Por defecto incluye el runtime oficial. Si ``include_experimental=True``,
    añade además los runtimes best-effort no públicos (`go`, `java`).
    Los targets `wasm` y `asm` permanecen fuera del benchmark ejecutable
    automatizado en esta capa.
    """
    canonical = official_transpiler_targets()
    available_targets = canonical if backends is None else tuple(
        target for target in canonical if target in backends
    )
    allowed = list(OFFICIAL_RUNTIME_TARGETS)
    if include_experimental:
        allowed.extend(BEST_EFFORT_BENCHMARK_RUNTIME_TARGETS)
    return target_cli_choices(tuple(target for target in available_targets if target in allowed))
