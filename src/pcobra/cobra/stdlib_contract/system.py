"""Contrato del módulo público ``cobra.system``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


SYSTEM_CONTRACT = ContractDescriptor(
    module="cobra.system",
    public_api=(
        "cobra.system.leer",
        "cobra.system.escribir",
        "cobra.system.ejecutar",
        "cobra.system.obtener_env",
    ),
    primary_backend="python",
    allowed_fallback=("rust", "javascript"),
    runtime_mapping=RuntimeMapping(
        standard_library=("src/pcobra/standard_library/archivo.py",),
        corelibs=("src/pcobra/corelibs/sistema.py",),
        core_nativos=("src/pcobra/core/nativos/sistema.js",),
    ),
    coverage=(
        FunctionCoverage("cobra.system.leer", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage(
            "cobra.system.escribir",
            {"python": "full", "rust": "partial", "javascript": "partial"},
        ),
        FunctionCoverage(
            "cobra.system.ejecutar",
            {"python": "full", "rust": "partial", "javascript": "full"},
        ),
        FunctionCoverage(
            "cobra.system.obtener_env",
            {"python": "full", "rust": "partial", "javascript": "full"},
        ),
    ),
)
