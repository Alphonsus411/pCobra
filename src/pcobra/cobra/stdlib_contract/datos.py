"""Contrato del módulo público ``cobra.datos``."""

from pcobra.cobra.stdlib_contract.base import (
    ContractDescriptor,
    FunctionCoverage,
    PublicApiExport,
    RuntimeMapping,
)


DATOS_CONTRACT = ContractDescriptor(
    module="cobra.datos",
    public_api=(
        "cobra.datos.filtrar",
        "cobra.datos.seleccionar_columnas",
        "cobra.datos.a_listas",
        "cobra.datos.de_listas",
    ),
    public_exports=(
        PublicApiExport("cobra.datos.filtrar", "src/pcobra/standard_library/datos.py", "filtrar"),
        PublicApiExport(
            "cobra.datos.seleccionar_columnas",
            "src/pcobra/standard_library/datos.py",
            "seleccionar_columnas",
        ),
        PublicApiExport("cobra.datos.a_listas", "src/pcobra/standard_library/datos.py", "a_listas"),
        PublicApiExport("cobra.datos.de_listas", "src/pcobra/standard_library/datos.py", "de_listas"),
    ),
    primary_backend="python",
    allowed_fallback=("javascript",),
    runtime_mapping=RuntimeMapping(
        standard_library=("src/pcobra/standard_library/datos.py",),
        corelibs=("src/pcobra/corelibs/coleccion.py",),
        core_nativos=("src/pcobra/core/nativos/datos.js",),
    ),
    coverage=(
        FunctionCoverage("cobra.datos.filtrar", {"python": "full", "javascript": "partial"}),
        FunctionCoverage(
            "cobra.datos.seleccionar_columnas",
            {"python": "full", "javascript": "partial"},
        ),
        FunctionCoverage("cobra.datos.a_listas", {"python": "full", "javascript": "partial"}),
        FunctionCoverage("cobra.datos.de_listas", {"python": "full", "javascript": "partial"}),
    ),
)
