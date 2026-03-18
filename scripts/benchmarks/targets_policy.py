"""Utilidades comunes de política de targets para benchmarks.

La política oficial de targets se hereda de
``src/pcobra/cobra/transpilers/targets.py`` y no debe redefinirse en scripts.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Final, Mapping

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name, target_cli_choices

BENCHMARK_BACKEND_METADATA: Final[dict[str, dict[str, object]]] = {
    "python": {"ext": "py", "run": ["python", "{file}"]},
    "javascript": {"ext": "js", "run": ["node", "{file}"]},
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
    },
    "wasm": {
        "ext": "wat",
        "compile": ["wat2wasm", "{file}", "-o", "{tmp}/prog.wasm"],
        "run": ["wasmtime", "{tmp}/prog.wasm"],
    },
    "go": {"ext": "go", "run": ["go", "run", "{file}"]},
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"],
    },
    "java": {
        "ext": "java",
        "compile": ["javac", "{file}"],
        "run": ["java", "-cp", "{tmp}", "Main"],
    },
    "asm": {
        "ext": "s",
        "compile": ["gcc", "{file}", "-o", "{tmp}/prog_asm"],
        "run": ["{tmp}/prog_asm"],
    },
}

BINARY_BENCHMARK_METADATA: Final[dict[str, dict[str, object]]] = {
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"],
        "bin": "{tmp}/prog_cpp",
    },
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
        "bin": "{tmp}/prog_rs",
    },
    "java": {
        "ext": "java",
        "compile": ["javac", "{file}"],
        "run": ["java", "-cp", "{tmp}", "Main"],
        "bin": "{tmp}/Main.class",
    },
    "asm": {
        "ext": "s",
        "compile": ["gcc", "{file}", "-o", "{tmp}/prog_asm"],
        "run": ["{tmp}/prog_asm"],
        "bin": "{tmp}/prog_asm",
    },
    "wasm": {
        "ext": "wat",
        "compile": ["wat2wasm", "{file}", "-o", "{tmp}/prog.wasm"],
        "run": ["wasmtime", "{tmp}/prog.wasm"],
        "bin": "{tmp}/prog.wasm",
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
        if canonical not in OFFICIAL_TARGETS:
            unsupported.append(str(target))
    if unsupported:
        raise RuntimeError(
            "Config local inválida: backends no oficiales en [project].required_targets: "
            f"{', '.join(unsupported)}. Oficiales: {', '.join(OFFICIAL_TARGETS)}"
        )



def validate_backend_metadata(backends: Mapping[str, object], *, context: str) -> None:
    """Falla rápido si existe metadata para targets fuera de la whitelist oficial."""
    unsupported = [target for target in backends if target not in OFFICIAL_TARGETS]
    if unsupported:
        raise RuntimeError(
            f"{context}: target(s) fuera de whitelist oficial: {', '.join(sorted(unsupported))}. "
            f"Oficiales: {', '.join(OFFICIAL_TARGETS)}"
        )



def benchmark_backends(backends: Mapping[str, object] | None = None) -> tuple[str, ...]:
    """Devuelve backends benchmark en orden oficial filtrados por metadata disponible."""
    available_targets = OFFICIAL_TARGETS if backends is None else tuple(backends.keys())
    return target_cli_choices(available_targets)
