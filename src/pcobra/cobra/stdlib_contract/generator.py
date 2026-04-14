"""Generación de manifiestos TOML y documentación del contrato stdlib."""

from __future__ import annotations

from pathlib import Path

from pcobra.cobra.stdlib_contract import CONTRACTS
from pcobra.cobra.stdlib_contract.base import ContractDescriptor


def _toml_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(f'\"{value}\"' for value in values) + "]"


def render_manifest(contract: ContractDescriptor) -> str:
    """Renderiza el manifiesto TOML mínimo compatible con ``module_map``."""
    return "\n".join(
        (
            f"public_api = {_toml_array(contract.public_api)}",
            f'backend_preferido = "{contract.primary_backend}"',
            f"fallback_permitido = {_toml_array(contract.allowed_fallback)}",
            "",
        )
    )


def render_contract_markdown() -> str:
    """Construye documentación Markdown desde descriptores Python."""
    lines: list[str] = [
        "# Contrato de stdlib Cobra (autogenerado)",
        "",
        "Este documento se genera desde `src/pcobra/cobra/stdlib_contract/*.py`.",
        "",
    ]
    for descriptor in CONTRACTS:
        mapping = descriptor.runtime_mapping
        lines.extend(
            (
                f"## `{descriptor.module}`",
                "",
                f"- **Backend primario:** `{descriptor.primary_backend}`",
                f"- **Fallback permitido:** `{', '.join(descriptor.allowed_fallback) or 'ninguno'}`",
                f"- **Mapeo `standard_library`:** `{mapping.standard_library or '-'}`",
                f"- **Mapeo `corelibs`:** `{mapping.corelibs or '-'}`",
                f"- **Mapeo `core/nativos`:** `{mapping.core_nativos or '-'}`",
                "",
                "### API pública",
                "",
            )
        )
        lines.extend(f"- `{api}`" for api in descriptor.public_api)
        lines.extend(("", "### Cobertura por función", "", "| Función | Backend | Nivel |", "|---|---|---|"))
        for coverage in descriptor.coverage:
            for backend, level in coverage.backend_levels.items():
                lines.append(f"| `{coverage.function}` | `{backend}` | `{level}` |")
        lines.append("")
    return "\n".join(lines)


def sync_contract_artifacts(contract_dir: Path, docs_path: Path) -> None:
    """Sincroniza manifiestos TOML y Markdown generado."""
    contract_dir.mkdir(parents=True, exist_ok=True)
    for descriptor in CONTRACTS:
        (contract_dir / descriptor.module).write_text(render_manifest(descriptor), encoding="utf-8")
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(render_contract_markdown(), encoding="utf-8")
