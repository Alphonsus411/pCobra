"""Contrato del módulo público ``cobra.system``."""

from pcobra.cobra.stdlib_contract.base import (
    ContractDescriptor,
    FunctionCoverage,
    PublicApiExport,
    RuntimeMapping,
)


SYSTEM_CONTRACT = ContractDescriptor(
    module="cobra.system",
    public_api=(
        "cobra.system.leer",
        "cobra.system.escribir",
        "cobra.system.adjuntar",
        "cobra.system.existe",
        "cobra.system.ejecutar",
        "cobra.system.ejecutar_comando_async",
        "cobra.system.obtener_env",
        "cobra.system.listar_dir",
        "cobra.system.ahora",
        "cobra.system.formatear",
        "cobra.system.dormir",
    ),
    public_exports=(
        PublicApiExport("cobra.system.leer", "src/pcobra/standard_library/archivo.py", "leer"),
        PublicApiExport("cobra.system.escribir", "src/pcobra/standard_library/archivo.py", "escribir"),
        PublicApiExport("cobra.system.adjuntar", "src/pcobra/standard_library/archivo.py", "adjuntar"),
        PublicApiExport("cobra.system.existe", "src/pcobra/standard_library/archivo.py", "existe"),
        PublicApiExport("cobra.system.ejecutar", "src/pcobra/corelibs/sistema.py", "ejecutar"),
        PublicApiExport(
            "cobra.system.ejecutar_comando_async",
            "src/pcobra/corelibs/sistema.py",
            "ejecutar_comando_async",
        ),
        PublicApiExport(
            "cobra.system.obtener_env",
            "src/pcobra/corelibs/sistema.py",
            "obtener_env",
        ),
        PublicApiExport("cobra.system.listar_dir", "src/pcobra/corelibs/sistema.py", "listar_dir"),
        PublicApiExport("cobra.system.ahora", "src/pcobra/corelibs/tiempo.py", "ahora"),
        PublicApiExport("cobra.system.formatear", "src/pcobra/corelibs/tiempo.py", "formatear"),
        PublicApiExport("cobra.system.dormir", "src/pcobra/corelibs/tiempo.py", "dormir"),
    ),
    primary_backend="python",
    allowed_fallback=("rust", "javascript"),
    runtime_mapping=RuntimeMapping(
        standard_library=("src/pcobra/standard_library/archivo.py",),
        corelibs=("src/pcobra/corelibs/sistema.py", "src/pcobra/corelibs/tiempo.py"),
        core_nativos=("src/pcobra/core/nativos/sistema.js",),
    ),
    coverage=(
        FunctionCoverage("cobra.system.leer", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage(
            "cobra.system.escribir",
            {"python": "full", "rust": "partial", "javascript": "partial"},
        ),
        FunctionCoverage("cobra.system.adjuntar", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage("cobra.system.existe", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage(
            "cobra.system.ejecutar",
            {"python": "full", "rust": "partial", "javascript": "partial"},
        ),
        FunctionCoverage("cobra.system.ejecutar_comando_async", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage(
            "cobra.system.obtener_env",
            {"python": "full", "rust": "partial", "javascript": "partial"},
        ),
        FunctionCoverage("cobra.system.listar_dir", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage("cobra.system.ahora", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage("cobra.system.formatear", {"python": "full", "rust": "partial", "javascript": "partial"}),
        FunctionCoverage("cobra.system.dormir", {"python": "full", "rust": "partial", "javascript": "partial"}),
    ),
)
