"""Constantes compartidas de targets soportados para la suite de tests."""

from pcobra.cobra.cli.target_policies import (
    OFFICIAL_RUNTIME_TARGETS as CLI_OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
    TRANSPILATION_ONLY_TARGETS as CLI_TRANSPILATION_ONLY_TARGETS,
)

SUPPORTED_TARGETS = OFFICIAL_TRANSPILATION_TARGETS
OFFICIAL_RUNTIME_TARGETS = CLI_OFFICIAL_RUNTIME_TARGETS
TRANSPILATION_ONLY_TARGETS = CLI_TRANSPILATION_ONLY_TARGETS

# Cobertura conservada solo como best-effort/manual; no forma parte del contrato
# oficial de runtime.
EXPERIMENTAL_RUNTIME_TARGETS = tuple(
    target for target in TRANSPILATION_ONLY_TARGETS if target in {"go", "java"}
)
BEST_EFFORT_RUNTIME_TARGETS = EXPERIMENTAL_RUNTIME_TARGETS
