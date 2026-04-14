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


__all__ = [
    "CONTRACTS",
    "ContractDescriptor",
    "get_contract_manifests",
]
