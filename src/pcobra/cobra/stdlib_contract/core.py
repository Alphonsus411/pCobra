"""Contrato del módulo público ``cobra.core``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


CORE_CONTRACT = ContractDescriptor(
    module="cobra.core",
    public_api=(
        "cobra.core.lex",
        "cobra.core.parse",
        "cobra.core.ast",
    ),
    primary_backend="python",
    allowed_fallback=("rust", "javascript"),
    runtime_mapping=RuntimeMapping(
        standard_library="src/pcobra/standard_library/util.py",
        corelibs="src/pcobra/corelibs/numero.py",
        core_nativos="src/pcobra/core/nativos/numero.js",
    ),
    coverage=(
        FunctionCoverage("cobra.core.lex", {"python": "full", "rust": "partial", "javascript": "full"}),
        FunctionCoverage("cobra.core.parse", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage("cobra.core.ast", {"python": "full", "rust": "partial", "javascript": "partial"}),
    ),
)
