"""Contrato declarativo de módulos públicos de la stdlib Cobra."""

from pcobra.cobra.stdlib_contract.base import ContractDescriptor
from pcobra.cobra.stdlib_contract.core import CORE_CONTRACT
from pcobra.cobra.stdlib_contract.datos import DATOS_CONTRACT
from pcobra.cobra.stdlib_contract.system import SYSTEM_CONTRACT
from pcobra.cobra.stdlib_contract.web import WEB_CONTRACT

CONTRACTS: tuple[ContractDescriptor, ...] = (
    CORE_CONTRACT,
    DATOS_CONTRACT,
    WEB_CONTRACT,
    SYSTEM_CONTRACT,
)


def get_contract_manifests() -> dict[str, dict[str, object]]:
    """Devuelve manifiestos mínimos compatibles con ``module_map``."""
    return {
        contract.module: {
            "public_api": list(contract.public_api),
            "backend_preferido": contract.primary_backend,
            "fallback_permitido": list(contract.allowed_fallback),
        }
        for contract in CONTRACTS
    }


def get_contract_matrix() -> dict[str, object]:
    """Devuelve matriz única de stdlib para consumo CLI/docs."""
    modules: list[dict[str, object]] = []
    for contract in CONTRACTS:
        mapping = contract.runtime_mapping
        rows: list[dict[str, str]] = []
        for fn in contract.coverage:
            for backend, level in fn.backend_levels.items():
                rows.append({"function": fn.function, "backend": backend, "level": level})
        modules.append(
            {
                "module": contract.module,
                "primary_backend": contract.primary_backend,
                "allowed_fallback": list(contract.allowed_fallback),
                "runtime_mapping": {
                    "standard_library": list(mapping.standard_library),
                    "corelibs": list(mapping.corelibs),
                    "core_nativos": list(mapping.core_nativos),
                },
                "public_api": list(contract.public_api),
                "coverage": rows,
            }
        )
    return {"modules": modules}


__all__ = [
    "CONTRACTS",
    "ContractDescriptor",
    "get_contract_manifests",
    "get_contract_matrix",
]
