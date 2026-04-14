"""Contrato del módulo público ``cobra.system``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


SYSTEM_CONTRACT = ContractDescriptor(
    module="cobra.system",
    public_api=(
        "cobra.system.fs",
        "cobra.system.proc",
        "cobra.system.env",
    ),
    primary_backend="rust",
    allowed_fallback=("python",),
    runtime_mapping=RuntimeMapping(
        standard_library="src/pcobra/standard_library/archivo.py",
        corelibs="src/pcobra/corelibs/sistema.py",
        core_nativos="src/pcobra/core/nativos/sistema.js",
    ),
    coverage=(
        FunctionCoverage("cobra.system.fs", {"rust": "full", "python": "full"}),
        FunctionCoverage("cobra.system.proc", {"rust": "full", "python": "partial"}),
        FunctionCoverage("cobra.system.env", {"rust": "full", "python": "full"}),
    ),
)
