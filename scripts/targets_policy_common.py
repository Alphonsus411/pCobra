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
    DOCKER_EXECUTABLE_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    CONTRACT_FEATURES,
)
from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    TIER1_TARGETS,
    TIER2_TARGETS,
)

PUBLIC_CANONICAL_TARGETS: tuple[str, ...] = tuple(OFFICIAL_TARGETS)
ACTIVE_PROPOSAL_PATHS = tuple(sorted((ROOT / "docs/proposals").glob("*.md")))
PUBLIC_ACCEPTED_TARGET_NAMES: tuple[str, ...] = tuple(OFFICIAL_TARGETS)
INTERNAL_COMPATIBILITY_TARGET_NAMES: tuple[str, ...] = tuple(OFFICIAL_TARGETS)

VALIDATION_SCAN_PATHS = (
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "docs/MANUAL_COBRA.md",
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

PUBLIC_TEXT_PATHS = (
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/target_policies.py",
    ROOT / "src/pcobra/cobra/cli/commands/benchmarks_cmd.py",
    ROOT / "README.md",
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/README.en.md",
    ROOT / "docs/blog_minilenguaje.md",
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
    ROOT / "docs/frontend/cli.rst",
    ROOT / "docs/frontend/contenedores.rst",
    ROOT / "docs/frontend/ejemplos.rst",
    ROOT / "docs/frontend/hololang.rst",
    ROOT / "docs/frontend/referencia.rst",
    ROOT / "examples/README.md",
    ROOT / "examples/hola_mundo/README.md",
    ROOT / "examples/hello_world/README.md",
    *ACTIVE_PROPOSAL_PATHS,
)
PUBLIC_TEXT_PATH_STRS: frozenset[str] = frozenset(
    path.relative_to(ROOT).as_posix() for path in PUBLIC_TEXT_PATHS
)

PROPOSAL_POLICY_PATHS = ACTIVE_PROPOSAL_PATHS

PUBLIC_RUNTIME_POLICY_PATHS = (
    ROOT / "README.md",
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/README.en.md",
    ROOT / "docs/matriz_transpiladores.md",
    ROOT / "docs/targets_policy.md",
)

HOLOBIT_PUBLIC_CONTRACT_PATHS = (
    ROOT / "README.md",
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/README.en.md",
    ROOT / "docs/contrato_runtime_holobit.md",
    ROOT / "docs/matriz_transpiladores.md",
    ROOT / "docs/targets_policy.md",
)

HOLOBIT_MATRIX_DOC_PATHS = (
    ROOT / "docs/contrato_runtime_holobit.md",
    ROOT / "docs/matriz_transpiladores.md",
)

LEGACY_ALIAS_ALLOWLIST: dict[str, tuple[re.Pattern[str], ...]] = {}
NON_CANONICAL_PUBLIC_NAMES: dict[str, str] = {
    "c++": "cpp",
    "assembly": "asm",
    "ensamblador": "asm",
    "js": "javascript",
}
OUT_OF_POLICY_LANGUAGE_TERMS: frozenset[str] = frozenset(
    {
        "kotlin",
        "swift",
        "ruby",
        "julia",
        "matlab",
    }
)


def read_target_policy() -> dict[str, Any]:
    return {
        "tier1_targets": tuple(TIER1_TARGETS),
        "tier2_targets": tuple(TIER2_TARGETS),
        "official_targets": tuple(OFFICIAL_TARGETS),
        "official_runtime_targets": tuple(DOCKER_EXECUTABLE_TARGETS),
        "verification_targets": tuple(VERIFICATION_EXECUTABLE_TARGETS),
        "transpilation_only_targets": tuple(TRANSPILATION_ONLY_TARGETS),
        "cli_aliases": {},
        "legacy_aliases": {},
        "public_names": tuple(PUBLIC_ACCEPTED_TARGET_NAMES),
        "internal_names": tuple(INTERNAL_COMPATIBILITY_TARGET_NAMES),
        "non_canonical_public_names": dict(NON_CANONICAL_PUBLIC_NAMES),
        "out_of_policy_language_terms": tuple(sorted(OUT_OF_POLICY_LANGUAGE_TERMS)),
        "compatibility_matrix": {
            backend: {
                feature: BACKEND_COMPATIBILITY[backend][feature]
                for feature in ("tier", *CONTRACT_FEATURES)
            }
            for backend in OFFICIAL_TARGETS
        },
    }


def build_legacy_alias_patterns(
    legacy_aliases: dict[str, str],
) -> tuple[re.Pattern[str], ...]:
    alias_group = "|".join(re.escape(alias) for alias in sorted(legacy_aliases))
    if not alias_group:
        return ()

    return (
        re.compile(
            rf"\b(?:--(?:tipo|tipos|backend|origen|destino)\s+|--(?:tipo|tipos|backend|origen|destino)=)({alias_group})\b",
            re.IGNORECASE,
        ),
        re.compile(rf"""['"]({alias_group})['"]""", re.IGNORECASE),
        re.compile(rf"``({alias_group})``", re.IGNORECASE),
    )
