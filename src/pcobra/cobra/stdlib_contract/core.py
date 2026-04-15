"""Contrato del módulo público ``cobra.core``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


CORE_CONTRACT = ContractDescriptor(
    module="cobra.core",
    public_api=(
        "cobra.core.es_finito",
        "cobra.core.es_infinito",
        "cobra.core.copiar_signo",
        "cobra.core.signo",
    ),
    primary_backend="python",
    allowed_fallback=("rust", "javascript"),
    runtime_mapping=RuntimeMapping(
        standard_library=("src/pcobra/standard_library/numero.py",),
        corelibs=("src/pcobra/corelibs/numero.py",),
        core_nativos=("src/pcobra/core/nativos/numero.js",),
    ),
    coverage=(
        FunctionCoverage(
            "cobra.core.es_finito",
            {"python": "full", "rust": "partial", "javascript": "full"},
        ),
        FunctionCoverage(
            "cobra.core.es_infinito",
            {"python": "full", "rust": "partial", "javascript": "full"},
        ),
        FunctionCoverage(
            "cobra.core.copiar_signo",
            {"python": "full", "rust": "partial", "javascript": "full"},
        ),
        FunctionCoverage(
            "cobra.core.signo",
            {"python": "full", "rust": "partial", "javascript": "full"},
        ),
    ),
)
