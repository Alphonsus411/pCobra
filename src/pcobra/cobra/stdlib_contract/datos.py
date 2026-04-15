"""Contrato del módulo público ``cobra.datos``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


DATOS_CONTRACT = ContractDescriptor(
    module="cobra.datos",
    public_api=(
        "cobra.datos.tabla",
        "cobra.datos.csv",
        "cobra.datos.json",
    ),
    primary_backend="python",
    allowed_fallback=("javascript",),
    runtime_mapping=RuntimeMapping(
        standard_library="src/pcobra/standard_library/datos.py",
        corelibs="src/pcobra/corelibs/coleccion.py",
        core_nativos="src/pcobra/core/nativos/datos.js",
    ),
    coverage=(
        FunctionCoverage("cobra.datos.tabla", {"python": "full", "javascript": "partial"}),
        FunctionCoverage("cobra.datos.csv", {"python": "full", "javascript": "partial"}),
        FunctionCoverage("cobra.datos.json", {"python": "full", "javascript": "full"}),
    ),
)
