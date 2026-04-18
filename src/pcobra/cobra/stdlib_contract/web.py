"""Contrato del módulo público ``cobra.web``."""

from pcobra.cobra.stdlib_contract.base import (
    ContractDescriptor,
    FunctionCoverage,
    PublicApiExport,
    RuntimeMapping,
)


WEB_CONTRACT = ContractDescriptor(
    module="cobra.web",
    public_api=(
        "cobra.web.obtener_url",
        "cobra.web.enviar_post",
        "cobra.web.descargar_archivo",
    ),
    public_exports=(
        PublicApiExport("cobra.web.obtener_url", "src/pcobra/corelibs/red.py", "obtener_url"),
        PublicApiExport("cobra.web.enviar_post", "src/pcobra/corelibs/red.py", "enviar_post"),
        PublicApiExport(
            "cobra.web.descargar_archivo",
            "src/pcobra/corelibs/red.py",
            "descargar_archivo",
        ),
    ),
    primary_backend="javascript",
    allowed_fallback=("python",),
    runtime_mapping=RuntimeMapping(
        standard_library=(),
        corelibs=("src/pcobra/corelibs/red.py",),
        core_nativos=("src/pcobra/core/nativos/red.js",),
    ),
    coverage=(
        FunctionCoverage("cobra.web.obtener_url", {"javascript": "partial", "python": "full"}),
        FunctionCoverage("cobra.web.enviar_post", {"javascript": "partial", "python": "full"}),
        FunctionCoverage(
            "cobra.web.descargar_archivo",
            {"javascript": "partial", "python": "full"},
        ),
    ),
)
