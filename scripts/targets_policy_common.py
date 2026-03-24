from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.cli.target_policies import (
    ADVANCED_HOLOBIT_RUNTIME_TARGETS,
    BEST_EFFORT_RUNTIME_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_STANDARD_LIBRARY_TARGETS,
    SDK_COMPATIBLE_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    CONTRACT_FEATURES,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS

PUBLIC_CANONICAL_TARGETS: tuple[str, ...] = OFFICIAL_TARGETS
PUBLIC_ACCEPTED_TARGET_NAMES: tuple[str, ...] = OFFICIAL_TARGETS
INTERNAL_COMPATIBILITY_TARGET_NAMES: tuple[str, ...] = OFFICIAL_TARGETS

VALIDATION_SCAN_PATHS = (
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/README.en.md",
    ROOT / "examples",
    ROOT / "docker",
    ROOT / "extensions",
    ROOT / "tests/utils",
    ROOT / "tests/performance",
    ROOT / "tests/integration",
    ROOT / "scripts",
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/commands/benchmarks_cmd.py",
    ROOT / "src/pcobra/cobra/cli/target_policies.py",
)

ACTIVE_PROPOSAL_PATHS = tuple(sorted((ROOT / "docs/proposals").glob("*.md")))

PUBLIC_TEXT_PATHS = (
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/target_policies.py",
    ROOT / "src/pcobra/cobra/cli/commands/benchmarks_cmd.py",
    ROOT / "README.md",
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/arquitectura_parser_transpiladores.md",
    ROOT / "docs/blog_minilenguaje.md",
    ROOT / "docs/casos_reales.md",
    ROOT / "docs/config_cli.md",
    ROOT / "docs/contrato_runtime_holobit.md",
    ROOT / "docs/especificacion_tecnica.md",
    ROOT / "docs/guia_basica.md",
    ROOT / "docs/lenguajes.rst",
    ROOT / "docs/lenguajes_soportados.rst",
    ROOT / "docs/matriz_transpiladores.md",
    ROOT / "docs/targets_policy.md",
    ROOT / "docs/frontend/index.rst",
    ROOT / "docs/frontend/avances.rst",
    ROOT / "docs/frontend/backends.rst",
    ROOT / "docs/frontend/benchmarking.rst",
    ROOT / "docs/frontend/caracteristicas.rst",
    ROOT / "docs/frontend/cli.rst",
    ROOT / "docs/frontend/contenedores.rst",
    ROOT / "docs/frontend/ejemplos.rst",
    ROOT / "docs/frontend/optimizaciones.rst",
    ROOT / "docs/frontend/referencia.rst",
    ROOT / "docs/frontend/sintaxis.rst",
    ROOT / "docs/frontend/transpilers_tier_plan.md",
    ROOT / "docs/_generated/target_policy_summary.md",
    ROOT / "docs/_generated/target_policy_summary.rst",
    ROOT / "docs/_generated/official_targets_table.rst",
    ROOT / "docs/_generated/runtime_capability_matrix.rst",
    ROOT / "docs/_generated/reverse_scope_table.rst",
    ROOT / "docs/_generated/cli_backend_examples.rst",
    ROOT / "examples/README.md",
    ROOT / "examples/hola_mundo/README.md",
    ROOT / "examples/hello_world/README.md",
    ROOT / "extensions/vscode/README.md",
    ROOT / "extensions/vscode/snippets/cobra.json",
    *sorted((ROOT / "examples/casos_reales").glob("*/README.md")),
    *ACTIVE_PROPOSAL_PATHS,
)
PUBLIC_TEXT_PATH_STRS: frozenset[str] = frozenset(
    path.relative_to(ROOT).as_posix() for path in PUBLIC_TEXT_PATHS
)

PUBLIC_RUNTIME_POLICY_PATHS = (
    ROOT / "README.md",
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/README.en.md",
    ROOT / "docs/matriz_transpiladores.md",
    ROOT / "docs/targets_policy.md",
)

HOLOBIT_MATRIX_DOC_PATHS = (
    ROOT / "docs/contrato_runtime_holobit.md",
    ROOT / "docs/matriz_transpiladores.md",
)

ACCEPTED_PUBLIC_TARGET_ALIASES: tuple[tuple[str, str], ...] = (
    ("c++", "cpp"),
    ("ensamblador", "asm"),
)

FORBIDDEN_PUBLIC_TARGET_ALIASES: tuple[tuple[str, str], ...] = (
    ("assembly", "asm"),
    ("js", "javascript"),
)


def normalized_public_line(line: str) -> str:
    return (
        line.replace(".js", "")
        .replace(".mjs", "")
        .replace(".cjs", "")
        .replace(".cpp", "")
        .replace(".wasm", "")
        .replace("Node.js", "Node")
    )



def find_public_alias_errors(rel: str, content: str) -> list[str]:
    if rel not in PUBLIC_TEXT_PATH_STRS:
        return []
    errors: list[str] = []
    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        line = normalized_public_line(raw_line)
        for alias, canonical in FORBIDDEN_PUBLIC_TARGET_ALIASES:
            pattern = re.compile(rf"(?<![\w.+/-]){re.escape(alias)}(?![\w.+/-])", re.IGNORECASE)
            if pattern.search(line):
                errors.append(
                    f"{rel}:{line_no}: alias público no canónico -> '{alias}' (usar: {canonical})"
                )
    return errors



def read_target_policy() -> dict[str, Any]:
    return {
        "tier1_targets": tuple(TIER1_TARGETS),
        "tier2_targets": tuple(TIER2_TARGETS),
        "official_targets": tuple(OFFICIAL_TARGETS),
        "official_runtime_targets": tuple(OFFICIAL_RUNTIME_TARGETS),
        "verification_targets": tuple(VERIFICATION_EXECUTABLE_TARGETS),
        "transpilation_only_targets": tuple(TRANSPILATION_ONLY_TARGETS),
        "best_effort_runtime_targets": tuple(BEST_EFFORT_RUNTIME_TARGETS),
        "no_runtime_targets": tuple(NO_RUNTIME_TARGETS),
        "official_standard_library_targets": tuple(OFFICIAL_STANDARD_LIBRARY_TARGETS),
        "advanced_holobit_runtime_targets": tuple(ADVANCED_HOLOBIT_RUNTIME_TARGETS),
        "sdk_compatible_targets": tuple(SDK_COMPATIBLE_TARGETS),
        "public_names": tuple(PUBLIC_ACCEPTED_TARGET_NAMES),
        "internal_names": tuple(INTERNAL_COMPATIBILITY_TARGET_NAMES),
        "compatibility_matrix": {
            backend: {
                feature: BACKEND_COMPATIBILITY[backend][feature]
                for feature in ("tier", *CONTRACT_FEATURES)
            }
            for backend in OFFICIAL_TARGETS
        },
    }
