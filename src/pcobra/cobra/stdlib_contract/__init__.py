"""Contrato declarativo de módulos públicos de la stdlib Cobra."""

import ast
from pathlib import Path

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


def _parse_literal_tuple(node: ast.AST) -> tuple[str, ...]:
    if not isinstance(node, (ast.Tuple, ast.List)):
        raise RuntimeError("Estructura inválida en STDLIB_BLUEPRINTS: se esperaba tupla/lista")
    values: list[str] = []
    for item in node.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            raise RuntimeError("STDLIB_BLUEPRINTS contiene valores no literales")
        values.append(item.value)
    return tuple(values)


def _load_stdlib_blueprints() -> tuple[dict[str, object], ...]:
    module_path = Path(__file__).resolve().parents[1] / "architecture" / "unified_ecosystem.py"
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(module_path))
    blueprints: list[dict[str, object]] = []
    for node in ast.walk(tree):
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign):
            has_target = any(
                isinstance(target, ast.Name) and target.id == "STDLIB_BLUEPRINTS"
                for target in node.targets
            )
            if has_target:
                value_node = node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "STDLIB_BLUEPRINTS":
                value_node = node.value

        if not isinstance(value_node, (ast.Tuple, ast.List)):
            continue

        for item in value_node.elts:
            if not isinstance(item, ast.Call):
                continue
            keywords = {kw.arg: kw.value for kw in item.keywords if kw.arg}
            module_node = keywords.get("module")
            primary_node = keywords.get("primary_backend")
            rationale_node = keywords.get("rationale")
            api_node = keywords.get("api_contract")
            fallback_node = keywords.get("fallback_backends")
            if not (
                isinstance(module_node, ast.Constant)
                and isinstance(module_node.value, str)
                and isinstance(primary_node, ast.Constant)
                and isinstance(primary_node.value, str)
                and isinstance(rationale_node, ast.Constant)
                and isinstance(rationale_node.value, str)
                and api_node is not None
                and fallback_node is not None
            ):
                raise RuntimeError("STDLIB_BLUEPRINTS contiene campos no literales")
            blueprints.append(
                {
                    "module": module_node.value,
                    "primary_backend": primary_node.value,
                    "api_contract": _parse_literal_tuple(api_node),
                    "fallback_backends": _parse_literal_tuple(fallback_node),
                    "rationale": rationale_node.value,
                }
            )
    if not blueprints:
        raise RuntimeError("No se pudo extraer STDLIB_BLUEPRINTS de unified_ecosystem.py")
    return blueprints


def get_blueprint_contract_manifests() -> dict[str, dict[str, object]]:
    """Devuelve manifiestos de módulos públicos desde ``STDLIB_BLUEPRINTS``."""
    blueprints = _load_stdlib_blueprints()
    return {
        str(blueprint["module"]): {
            "backend_preferido": str(blueprint["primary_backend"]),
            "fallback_permitido": list(blueprint["fallback_backends"]),
            "capacidades": list(blueprint["api_contract"]),
            "rationale": str(blueprint["rationale"]),
        }
        for blueprint in blueprints
    }


def get_public_stdlib_module_contracts() -> dict[str, dict[str, object]]:
    """Expone el contrato mínimo para resolver módulos públicos ``cobra.*``."""
    manifests = get_blueprint_contract_manifests()
    return {
        module: {
            "backend_preferido": manifest["backend_preferido"],
            "fallback_permitido": manifest["fallback_permitido"],
            "capacidades": manifest["capacidades"],
        }
        for module, manifest in manifests.items()
    }


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
    "get_blueprint_contract_manifests",
    "get_contract_manifests",
    "get_contract_matrix",
    "get_public_stdlib_module_contracts",
]
