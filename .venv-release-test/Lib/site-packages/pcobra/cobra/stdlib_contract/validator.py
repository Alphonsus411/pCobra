"""Validaciones para evitar drift entre contrato stdlib y runtime real."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Final

from pcobra.cobra.stdlib_contract import CONTRACTS, get_blueprint_contract_manifests
from pcobra.cobra.stdlib_contract.base import ContractDescriptor, PublicApiExport
from pcobra.cobra.stdlib_contract.generator import build_contract_matrix, render_contract_markdown

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
VALID_LEVELS: Final[set[str]] = {"full", "partial"}
RUNTIME_API_MATRIX_PATH: Final[Path] = REPO_ROOT / "docs" / "_generated" / "runtime_api_matrix.json"
STDLIB_CONTRACT_MATRIX_JSON_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "_generated" / "stdlib_contract_matrix.json"
)
STDLIB_CONTRACT_MATRIX_MD_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "_generated" / "stdlib_contract_matrix.md"
)
PRIMARY_BACKEND_POLICY: Final[dict[str, tuple[str, ...]]] = {
    "cobra.core": ("python",),
    "cobra.datos": ("python",),
    "cobra.web": ("javascript",),
    "cobra.system": ("python",),
}


class ContractValidationError(RuntimeError):
    """Error de validación del contrato de stdlib."""


def _extract_py_functions(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    return {
        node.name
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    }


def _extract_js_exports(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    return set(re.findall(r"export\s+(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)", source))


def _extract_symbols(path: Path) -> set[str]:
    if path.suffix == ".py":
        return _extract_py_functions(path)
    if path.suffix == ".js":
        return _extract_js_exports(path)
    return set()


def _iter_mapping_paths(contract: ContractDescriptor) -> list[Path]:
    paths: list[Path] = []
    for bucket in (
        contract.runtime_mapping.standard_library,
        contract.runtime_mapping.corelibs,
        contract.runtime_mapping.core_nativos,
    ):
        for relative in bucket:
            path = (REPO_ROOT / relative).resolve()
            paths.append(path)
    return paths


def _primary_backends(contract: ContractDescriptor) -> tuple[str, ...]:
    return tuple(part for part in contract.primary_backend.split("+") if part)


def _validate_mapping_paths(contract: ContractDescriptor) -> None:
    for path in _iter_mapping_paths(contract):
        if not path.exists():
            raise ContractValidationError(
                f"{contract.module}: runtime_mapping apunta a ruta inexistente: {path}"
            )


def _validate_public_api(contract: ContractDescriptor) -> None:
    expected_prefix = f"{contract.module}."
    invalid_api = [api for api in contract.public_api if not api.startswith(expected_prefix)]
    if invalid_api:
        raise ContractValidationError(
            f"{contract.module}: API pública fuera del namespace del módulo: {invalid_api}"
        )
    if len(contract.public_exports) != len(contract.public_api):
        raise ContractValidationError(
            f"{contract.module}: cantidad de public_exports no coincide con public_api. "
            f"public_api={len(contract.public_api)} public_exports={len(contract.public_exports)}"
        )

    allowed_paths = {
        *contract.runtime_mapping.standard_library,
        *contract.runtime_mapping.corelibs,
    }
    allowed_prefixes = ("src/pcobra/standard_library/", "src/pcobra/corelibs/")
    export_by_alias: dict[str, PublicApiExport] = {}
    for export in contract.public_exports:
        if export.alias in export_by_alias:
            raise ContractValidationError(
                f"{contract.module}: alias público duplicado en public_exports: {export.alias}"
            )
        export_by_alias[export.alias] = export
        if not export.alias.startswith(expected_prefix):
            raise ContractValidationError(
                f"{contract.module}: alias fuera del namespace del módulo: {export.alias}"
            )
        if export.source_path not in allowed_paths:
            raise ContractValidationError(
                f"{contract.module}: source_path fuera de runtime_mapping standard_library/corelibs: "
                f"{export.source_path}"
            )
        if not export.source_path.startswith(allowed_prefixes):
            raise ContractValidationError(
                f"{contract.module}: source_path inválido para trazabilidad pública: {export.source_path}"
            )

        path = (REPO_ROOT / export.source_path).resolve()
        symbols = _extract_symbols(path)
        if export.python_symbol not in symbols:
            raise ContractValidationError(
                f"{contract.module}: símbolo `{export.python_symbol}` no encontrado en {export.source_path}"
            )

    missing_exports = [api for api in contract.public_api if api not in export_by_alias]
    if missing_exports:
        raise ContractValidationError(
            f"{contract.module}: public_api sin entrada en public_exports: {missing_exports}"
        )


def _validate_coverage(contract: ContractDescriptor) -> None:
    primary_backends = set(_primary_backends(contract))
    if not primary_backends:
        raise ContractValidationError(f"{contract.module}: primary_backend vacío")
    expected_backends = {*primary_backends, *contract.allowed_fallback}
    declared_functions = set(contract.public_api)

    if len(contract.coverage) != len(contract.public_api):
        raise ContractValidationError(
            f"{contract.module}: cobertura incompleta. "
            f"public_api={len(contract.public_api)} coverage={len(contract.coverage)}"
        )

    for function_coverage in contract.coverage:
        if function_coverage.function not in declared_functions:
            raise ContractValidationError(
                f"{contract.module}: cobertura para función no declarada: {function_coverage.function}"
            )

        coverage_backends = set(function_coverage.backend_levels)
        if coverage_backends != expected_backends:
            raise ContractValidationError(
                f"{contract.module}.{function_coverage.function}: backends de cobertura inválidos. "
                f"esperados={sorted(expected_backends)} recibidos={sorted(coverage_backends)}"
            )

        for backend, level in function_coverage.backend_levels.items():
            if level not in VALID_LEVELS:
                raise ContractValidationError(
                    f"{contract.module}.{function_coverage.function}.{backend}: "
                    f"nivel inválido '{level}', use full|partial"
                )


def _validate_primary_backend_policy(contract: ContractDescriptor) -> None:
    expected = PRIMARY_BACKEND_POLICY.get(contract.module)
    if expected is None:
        return
    resolved = _primary_backends(contract)
    if resolved != expected:
        raise ContractValidationError(
            f"{contract.module}: backend primario inválido. "
            f"esperado={'+'.join(expected)} recibido={contract.primary_backend}"
        )


def _load_runtime_api_matrix() -> dict[str, object]:
    try:
        payload = json.loads(RUNTIME_API_MATRIX_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractValidationError(
            f"No existe runtime_api_matrix requerido para validación: {RUNTIME_API_MATRIX_PATH}"
        ) from exc
    if not isinstance(payload, dict):
        raise ContractValidationError("runtime_api_matrix inválido: estructura raíz no es objeto")
    return payload


def validate_coverage_against_runtime_matrix(contract: ContractDescriptor) -> None:
    """Valida que `coverage` (full/partial) coincida con disponibilidad en runtime_api_matrix."""
    matrix = _load_runtime_api_matrix()
    available_by_backend = matrix.get("available_api_by_backend")
    if not isinstance(available_by_backend, dict):
        raise ContractValidationError("runtime_api_matrix inválido: falta `available_api_by_backend`")

    for function_coverage in contract.coverage:
        symbol = function_coverage.function.rsplit(".", 1)[-1]
        for backend, level in function_coverage.backend_levels.items():
            backend_data = available_by_backend.get(backend)
            if not isinstance(backend_data, dict):
                raise ContractValidationError(
                    f"runtime_api_matrix inválido: backend ausente o inválido `{backend}`"
                )
            global_api = backend_data.get("global")
            if not isinstance(global_api, list):
                raise ContractValidationError(
                    f"runtime_api_matrix inválido: `{backend}.global` no es lista"
                )
            is_available = symbol in set(global_api)
            if level == "full" and not is_available:
                raise ContractValidationError(
                    f"{function_coverage.function}.{backend}: marcado full pero no aparece "
                    "en runtime_api_matrix.available_api_by_backend.global"
                )
            if level == "partial" and is_available:
                raise ContractValidationError(
                    f"{function_coverage.function}.{backend}: marcado partial pero aparece "
                    "como disponible en runtime_api_matrix; usar full o actualizar matriz."
                )


def validate_contract_descriptor(contract: ContractDescriptor) -> None:
    """Valida mapping, API pública y cobertura de un descriptor."""

    _validate_mapping_paths(contract)
    _validate_public_api(contract)
    _validate_coverage(contract)
    _validate_primary_backend_policy(contract)


def validate_contracts_against_blueprints() -> None:
    """Valida consistencia del contrato stdlib con ``STDLIB_BLUEPRINTS``."""
    contract_by_module = {contract.module: contract for contract in CONTRACTS}
    blueprint_by_module = get_blueprint_contract_manifests()

    contract_modules = set(contract_by_module)
    blueprint_modules = set(blueprint_by_module)
    if contract_modules != blueprint_modules:
        raise ContractValidationError(
            "Módulos públicos inconsistentes entre contrato y STDLIB_BLUEPRINTS. "
            f"solo_contrato={sorted(contract_modules - blueprint_modules)} "
            f"solo_blueprint={sorted(blueprint_modules - contract_modules)}"
        )

    for module in sorted(contract_modules):
        contract = contract_by_module[module]
        blueprint = blueprint_by_module[module]

        primary_backend = blueprint.get("backend_preferido")
        if contract.primary_backend != primary_backend:
            raise ContractValidationError(
                f"{module}: primary_backend inconsistente con STDLIB_BLUEPRINTS. "
                f"contract={contract.primary_backend} blueprint={primary_backend}"
            )

        fallback_backends = tuple(blueprint.get("fallback_permitido", []))
        if contract.allowed_fallback != fallback_backends:
            raise ContractValidationError(
                f"{module}: fallbacks inconsistentes con STDLIB_BLUEPRINTS. "
                f"contract={contract.allowed_fallback} blueprint={fallback_backends}"
            )


def validate_contracts() -> None:
    """Valida todos los contratos de stdlib definidos en el proyecto."""

    modules_seen: set[str] = set()
    for contract in CONTRACTS:
        if contract.module in modules_seen:
            raise ContractValidationError(f"Módulo duplicado en contrato: {contract.module}")
        modules_seen.add(contract.module)
        validate_contract_descriptor(contract)
    validate_contracts_against_blueprints()


def validate_contracts_against_runtime_matrix() -> None:
    """Valida cobertura full/partial por función contra `runtime_api_matrix`."""
    for contract in CONTRACTS:
        validate_coverage_against_runtime_matrix(contract)


def validate_generated_stdlib_contract_matrix() -> None:
    """Valida consistencia entre contrato vivo y docs generadas de stdlib."""
    expected_json = build_contract_matrix()
    try:
        rendered_json = json.loads(STDLIB_CONTRACT_MATRIX_JSON_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractValidationError(
            "No existe stdlib_contract_matrix.json generado en docs/_generated"
        ) from exc
    if rendered_json != expected_json:
        raise ContractValidationError(
            "docs/_generated/stdlib_contract_matrix.json está desactualizado respecto al contrato."
        )

    expected_md = render_contract_markdown().strip()
    try:
        rendered_md = STDLIB_CONTRACT_MATRIX_MD_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ContractValidationError(
            "No existe stdlib_contract_matrix.md generado en docs/_generated"
        ) from exc
    if rendered_md != expected_md:
        raise ContractValidationError(
            "docs/_generated/stdlib_contract_matrix.md está desactualizado respecto al contrato."
        )
