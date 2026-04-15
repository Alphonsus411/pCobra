"""Contrato del módulo público ``cobra.web``."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor, FunctionCoverage, RuntimeMapping


WEB_CONTRACT = ContractDescriptor(
    module="cobra.web",
    public_api=(
        "cobra.web.http",
        "cobra.web.router",
        "cobra.web.sse",
    ),
    primary_backend="javascript",
    allowed_fallback=("python",),
    runtime_mapping=RuntimeMapping(
        standard_library="src/pcobra/standard_library/interfaz.py",
        corelibs="src/pcobra/corelibs/red.py",
        core_nativos="src/pcobra/core/nativos/red.js",
    ),
    coverage=(
        FunctionCoverage("cobra.web.http", {"javascript": "full", "python": "partial"}),
        FunctionCoverage("cobra.web.router", {"javascript": "full", "python": "partial"}),
        FunctionCoverage("cobra.web.sse", {"javascript": "full", "python": "partial"}),
    ),
)
