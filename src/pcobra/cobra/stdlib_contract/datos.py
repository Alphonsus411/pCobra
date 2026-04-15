"""Contrato del módulo público ``cobra.datos``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


DATOS_CONTRACT = ContractDescriptor(
    module="cobra.datos",
    public_api=(
        "cobra.datos.filtrar",
        "cobra.datos.seleccionar_columnas",
        "cobra.datos.a_listas",
        "cobra.datos.de_listas",
    ),
    primary_backend="python",
    allowed_fallback=("javascript",),
    runtime_mapping=RuntimeMapping(
        standard_library=("src/pcobra/standard_library/datos.py",),
        corelibs=("src/pcobra/corelibs/coleccion.py",),
        core_nativos=("src/pcobra/core/nativos/datos.js",),
    ),
    coverage=(
        FunctionCoverage("cobra.datos.filtrar", {"python": "full", "javascript": "full"}),
        FunctionCoverage(
            "cobra.datos.seleccionar_columnas",
            {"python": "full", "javascript": "full"},
        ),
        FunctionCoverage("cobra.datos.a_listas", {"python": "full", "javascript": "full"}),
        FunctionCoverage("cobra.datos.de_listas", {"python": "full", "javascript": "full"}),
    ),
)
