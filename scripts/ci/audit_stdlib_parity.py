#!/usr/bin/env python3
"""Audita la paridad de stdlib pública por función desde contratos declarativos.

Fuente única de verdad:
- src/pcobra/cobra/stdlib_contract/core.py
- src/pcobra/cobra/stdlib_contract/datos.py
- src/pcobra/cobra/stdlib_contract/web.py
- src/pcobra/cobra/stdlib_contract/system.py

El reporte de CI y la tabla pública en docs se generan exclusivamente desde
``ContractDescriptor.coverage``.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
SRC: Final[Path] = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.stdlib_contract import CONTRACTS  # noqa: E402



@dataclass(frozen=True)
class CoverageRow:
    module: str
    function: str
    primary_backend: str
    python: str
    javascript: str
    rust: str
    notes: str


def _build_rows() -> list[CoverageRow]:
    rows: list[CoverageRow] = []
    for contract in CONTRACTS:
        coverage_by_function = {item.function: item.backend_levels for item in contract.coverage}
        for function in contract.public_api:
            levels = coverage_by_function.get(function)
            if levels is None:
                raise RuntimeError(f"{contract.module}: cobertura faltante para {function}")

            row = CoverageRow(
                module=contract.module,
                function=function,
                primary_backend=contract.primary_backend,
                python=levels.get("python", "n/a"),
                javascript=levels.get("javascript", "n/a"),
                rust=levels.get("rust", "n/a"),
                notes="",
            )
            rows.append(row)

    rows.sort(key=lambda row: (row.module, row.function))
    return rows


def _build_web_notes(rows: list[CoverageRow]) -> dict[str, str]:
    web_rows = [row for row in rows if row.module == "cobra.web"]
    if not web_rows:
        raise RuntimeError("No se encontraron funciones para cobra.web en el contrato")

    fallback_full = [
        row.function
        for row in web_rows
        if row.primary_backend == "javascript" and row.javascript == "partial" and row.python == "full"
    ]

    notes: dict[str, str] = {}
    for row in web_rows:
        if row.function in fallback_full:
            notes[row.function] = "JS primario partial; fallback python full"
        elif row.primary_backend == "javascript" and row.javascript == "partial":
            notes[row.function] = "JS primario partial; fallback python no-full"
        else:
            notes[row.function] = "-"
    return notes


def _render_table(rows: list[CoverageRow]) -> list[str]:
    web_notes = _build_web_notes(rows)
    lines = [
        "| módulo | función | primario | python | javascript | rust | notas |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        notes = web_notes.get(row.function, row.notes) if row.module == "cobra.web" else "-"
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{row.module}`",
                    f"`{row.function}`",
                    f"`{row.primary_backend}`",
                    row.python,
                    row.javascript,
                    row.rust,
                    notes,
                )
            )
            + " |"
        )
    return lines


def _render_web_summary(rows: list[CoverageRow]) -> list[str]:
    web_rows = [row for row in rows if row.module == "cobra.web"]
    fallback_full = [
        row.function
        for row in web_rows
        if row.primary_backend == "javascript" and row.javascript == "partial" and row.python == "full"
    ]
    fallback_list = ", ".join(f"`{fn}`" for fn in fallback_full)
    return [
        "## Estado explícito de `cobra.web`",
        "",
        "- El backend primario se mantiene en `javascript`.",
        "- Estado del primario JS: `partial` en todas las funciones públicas declaradas.",
        f"- Funciones con fallback `python` en `full`: {fallback_list}.",
        "",
    ]


def run_audit(report_path: Path, docs_table_path: Path) -> int:
    rows = _build_rows()

    report_lines = [
        "# Auditoría CI: paridad stdlib por función",
        "",
        "Fuente única de API pública y cobertura:",
        "- `src/pcobra/cobra/stdlib_contract/core.py`",
        "- `src/pcobra/cobra/stdlib_contract/datos.py`",
        "- `src/pcobra/cobra/stdlib_contract/web.py`",
        "- `src/pcobra/cobra/stdlib_contract/system.py`",
        "",
        "## Cobertura por función (python/javascript/rust)",
        "",
        *_render_table(rows),
        "",
        *_render_web_summary(rows),
    ]

    docs_lines = [
        "# Paridad de stdlib pública por función",
        "",
        "Tabla publicada para usuarios finales. Se genera desde los contratos de",
        "`src/pcobra/cobra/stdlib_contract/{core,datos,web,system}.py`.",
        "",
        *_render_table(rows),
        "",
        *_render_web_summary(rows),
    ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    docs_table_path.parent.mkdir(parents=True, exist_ok=True)
    docs_table_path.write_text("\n".join(docs_lines) + "\n", encoding="utf-8")

    print(f"Reporte generado en: {report_path}")
    print(f"Tabla pública generada en: {docs_table_path}")
    print(f"Funciones auditadas: {len(rows)}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "docs" / "_generated" / "audit_stdlib_parity_report.md",
        help="Ruta de salida para el reporte Markdown de CI.",
    )
    parser.add_argument(
        "--docs-table",
        type=Path,
        default=ROOT / "docs" / "standard_library" / "paridad_stdlib_por_funcion.md",
        help="Ruta de salida para tabla pública de paridad.",
    )
    args = parser.parse_args()
    return run_audit(args.report, args.docs_table)


if __name__ == "__main__":
    raise SystemExit(main())
