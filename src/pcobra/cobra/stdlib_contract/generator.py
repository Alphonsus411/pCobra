"""Generación de manifiestos TOML y documentación del contrato stdlib."""

from __future__ import annotations

import json
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


def build_contract_matrix() -> dict[str, object]:
    """Construye matriz única de stdlib consumible por CLI/docs."""
    matrix_modules: list[dict[str, object]] = []

    for descriptor in CONTRACTS:
        coverage_rows: list[dict[str, str]] = []
        for coverage in descriptor.coverage:
            for backend, level in coverage.backend_levels.items():
                coverage_rows.append(
                    {
                        "function": coverage.function,
                        "backend": backend,
                        "level": level,
                    }
                )

        mapping = descriptor.runtime_mapping
        matrix_modules.append(
            {
                "module": descriptor.module,
                "primary_backend": descriptor.primary_backend,
                "allowed_fallback": list(descriptor.allowed_fallback),
                "runtime_mapping": {
                    "standard_library": list(mapping.standard_library),
                    "corelibs": list(mapping.corelibs),
                    "core_nativos": list(mapping.core_nativos),
                },
                "public_api": list(descriptor.public_api),
                "coverage": coverage_rows,
            }
        )

    return {"modules": matrix_modules}


def _format_paths(paths: tuple[str, ...]) -> str:
    return ", ".join(f"`{path}`" for path in paths) if paths else "-"


def render_contract_markdown() -> str:
    """Construye documentación Markdown desde descriptores Python."""
    lines: list[str] = [
        "# Matriz única de stdlib Cobra (autogenerado)",
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
                f"- **Mapeo `standard_library`:** {_format_paths(mapping.standard_library)}",
                f"- **Mapeo `corelibs`:** {_format_paths(mapping.corelibs)}",
                f"- **Mapeo `core/nativos`:** {_format_paths(mapping.core_nativos)}",
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


def sync_contract_artifacts(
    contract_dir: Path,
    docs_generated_md: Path,
    docs_generated_json: Path,
    docs_stdlib_md: Path,
) -> None:
    """Sincroniza manifiestos TOML y matriz única (Markdown + JSON)."""
    contract_dir.mkdir(parents=True, exist_ok=True)
    for descriptor in CONTRACTS:
        (contract_dir / descriptor.module).write_text(render_manifest(descriptor), encoding="utf-8")

    markdown = render_contract_markdown()
    matrix = build_contract_matrix()

    docs_generated_md.parent.mkdir(parents=True, exist_ok=True)
    docs_generated_md.write_text(markdown, encoding="utf-8")

    docs_generated_json.parent.mkdir(parents=True, exist_ok=True)
    docs_generated_json.write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    docs_stdlib_md.parent.mkdir(parents=True, exist_ok=True)
    docs_stdlib_md.write_text(markdown, encoding="utf-8")
