"""Utilidades de política de targets para benchmarks.

La política oficial de targets se hereda de
``src/pcobra/cobra/transpilers/targets.py`` y no debe redefinirse en scripts.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Mapping

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS, normalize_target_name


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


def benchmark_backends(backends: Mapping[str, object]) -> tuple[str, ...]:
    """Devuelve backends benchmark en orden oficial (Tier 1 -> Tier 2)."""
    return tuple(target for target in (*TIER1_TARGETS, *TIER2_TARGETS) if target in backends)
