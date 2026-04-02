#!/usr/bin/env python3
"""Audita paridad de standard_library entre exports, backends y documentación.

Reglas de severidad:
- error: símbolo público sin estrategia declarada de backend.
- warning: símbolo con soporte parcial sin workaround documentado.

Además genera un reporte Markdown como artefacto de CI.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
SRC: Final[Path] = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.transpilers.compatibility_matrix import (  # noqa: E402
    BACKEND_FEATURE_NODE_SUPPORT,
    BACKEND_COMPATIBILITY,
)
from pcobra.cobra.transpilers.runtime_api_matrix import (  # noqa: E402
    SNAPSHOT_PATH,
    build_runtime_api_matrix,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS  # noqa: E402

STANDARD_LIBRARY_INIT = ROOT / "src" / "pcobra" / "standard_library" / "__init__.py"
DECORADORES_MODULE = ROOT / "src" / "pcobra" / "standard_library" / "decoradores.py"
LANGUAGE_EQ_PATH = ROOT / "data" / "language_equivalence.yml"
LANGUAGE_EQ_DOC = ROOT / "docs" / "language_equivalence_matrix.md"
LIBRARY_COMPAT_DOC = ROOT / "docs" / "library_compatibility_matrix.md"
DECORATORS_DOC = ROOT / "docs" / "standard_library" / "decoradores.md"


@dataclass(frozen=True)
class Finding:
    severity: str
    symbol: str
    message: str


def _read_all_exports(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    for node in module.body:
        value = None
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    value = node.value
                    break
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__":
            value = node.value
        if value is None:
            continue
        resolved = ast.literal_eval(value)
        if not isinstance(resolved, list) or not all(isinstance(item, str) for item in resolved):
            raise RuntimeError(f"{path}: __all__ inválido")
        return resolved
    raise RuntimeError(f"{path}: no se encontró __all__")


def _load_language_equivalence() -> dict:
    payload = yaml.safe_load(LANGUAGE_EQ_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Contrato inválido en {LANGUAGE_EQ_PATH}")
    return payload


def _decorator_sections_with_workaround(doc: str) -> dict[str, bool]:
    sections: dict[str, bool] = {}
    current: str | None = None
    buffer: list[str] = []

    for line in doc.splitlines():
        if line.startswith("## `") and line.endswith("`"):
            if current is not None:
                text = "\n".join(buffer)
                sections[current] = "Limitación real fuera de Python runtime" in text
            current = line.replace("## `", "", 1)[:-1]
            buffer = []
            continue
        if current is not None:
            buffer.append(line)

    if current is not None:
        text = "\n".join(buffer)
        sections[current] = "Limitación real fuera de Python runtime" in text

    return sections


def _markdown_status_row(symbol: str, status_by_backend: dict[str, str], severity: str, notes: str) -> str:
    ordered = [status_by_backend.get(backend, "none") for backend in OFFICIAL_TARGETS]
    return "| " + " | ".join([symbol, *ordered, severity, notes]) + " |"


def run_audit(report_path: Path) -> int:
    stdlib_exports = _read_all_exports(STANDARD_LIBRARY_INIT)
    decorator_exports = _read_all_exports(DECORADORES_MODULE)

    runtime_matrix = build_runtime_api_matrix()
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    python_snapshot = set(snapshot.get("python_global_api_snapshot", []))

    equivalence = _load_language_equivalence()
    features = {feature["id"]: feature for feature in equivalence.get("features", [])}
    decoradores_contract = features.get("decoradores", {})
    decorator_support = decoradores_contract.get("decorator_support", {})

    decorators_doc_text = DECORATORS_DOC.read_text(encoding="utf-8")
    decorators_workarounds = _decorator_sections_with_workaround(decorators_doc_text)

    language_eq_doc = LANGUAGE_EQ_DOC.read_text(encoding="utf-8")
    library_compat_doc = LIBRARY_COMPAT_DOC.read_text(encoding="utf-8")

    findings: list[Finding] = []
    table_rows: list[str] = []

    # Reglas de error: símbolo público sin estrategia declarada.
    for symbol in stdlib_exports:
        if symbol not in python_snapshot:
            findings.append(
                Finding(
                    severity="error",
                    symbol=symbol,
                    message="Símbolo público sin estrategia declarada en runtime_api_parity_snapshot.",
                )
            )

    # Auditoría detallada de decoradores (equivalencia + nodos + workaround docs)
    for symbol in decorator_exports:
        status_by_backend: dict[str, str] = {}
        notes: list[str] = []

        if symbol not in stdlib_exports:
            findings.append(
                Finding(
                    severity="error",
                    symbol=symbol,
                    message="Decorador público no re-exportado en standard_library.__all__.",
                )
            )

        if symbol not in decorator_support:
            findings.append(
                Finding(
                    severity="error",
                    symbol=symbol,
                    message="Decorador sin estrategia declarada en data/language_equivalence.yml.decorator_support.",
                )
            )
            # Fallback para no romper el reporte
            status_by_backend = {backend: "none" for backend in OFFICIAL_TARGETS}
        else:
            raw = decorator_support[symbol]
            status_by_backend = {backend: raw.get(backend, "none") for backend in OFFICIAL_TARGETS}

        for backend in OFFICIAL_TARGETS:
            status = status_by_backend.get(backend, "none")
            node_support = BACKEND_FEATURE_NODE_SUPPORT.get(backend, {}).get("decoradores", ())
            if status in {"partial", "full"} and not node_support:
                findings.append(
                    Finding(
                        severity="error",
                        symbol=symbol,
                        message=(
                            f"Backend `{backend}` marca `{status}` en equivalencia, "
                            "pero no declara nodos/visitadores en BACKEND_FEATURE_NODE_SUPPORT.decoradores."
                        ),
                    )
                )
            if status == "partial" and not decorators_workarounds.get(symbol, False):
                findings.append(
                    Finding(
                        severity="warning",
                        symbol=symbol,
                        message=(
                            "Soporte parcial sin workaround documentado en "
                            "docs/standard_library/decoradores.md."
                        ),
                    )
                )

        if "| decoradores |" not in language_eq_doc:
            findings.append(
                Finding(
                    severity="error",
                    symbol=symbol,
                    message="La tabla de docs/language_equivalence_matrix.md no contiene la fila `decoradores`.",
                )
            )
        if "standard_library" not in library_compat_doc:
            findings.append(
                Finding(
                    severity="error",
                    symbol=symbol,
                    message="docs/library_compatibility_matrix.md no documenta `standard_library`.",
                )
            )

        severity = "error" if any(f.severity == "error" and f.symbol == symbol for f in findings) else (
            "warning" if any(f.severity == "warning" and f.symbol == symbol for f in findings) else "ok"
        )
        if status_by_backend.get("python") != "full":
            notes.append("python debería permanecer en full para decoradores")
        if BACKEND_COMPATIBILITY["python"]["standard_library"] != "full":
            notes.append("contrato backend python/standard_library degradado")

        table_rows.append(_markdown_status_row(symbol, status_by_backend, severity, "; ".join(notes) or "-"))

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines = [
        "# Auditoría CI: paridad de `standard_library`",
        "",
        "## Resumen",
        "",
        f"- Símbolos públicos auditados en `standard_library.__all__`: **{len(stdlib_exports)}**.",
        f"- Decoradores auditados en detalle: **{len(decorator_exports)}**.",
        f"- Errores: **{len(errors)}**.",
        f"- Warnings: **{len(warnings)}**.",
        "",
        "## Tabla de paridad (funcionalidad / python / javascript / rust / go / cpp / java / wasm / asm)",
        "",
        "| funcionalidad | python | javascript | rust | go | cpp | java | wasm | asm | severidad | notas |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        *table_rows,
        "",
        "## Hallazgos",
        "",
    ]

    if not findings:
        lines.append("Sin hallazgos: contrato de paridad consistente.")
    else:
        for finding in findings:
            lines.append(f"- **{finding.severity.upper()}** `{finding.symbol}`: {finding.message}")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Reporte generado en: {report_path}")
    print(f"Errores={len(errors)} Warnings={len(warnings)}")

    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "docs" / "_generated" / "audit_stdlib_parity_report.md",
        help="Ruta de salida para el reporte Markdown.",
    )
    args = parser.parse_args()
    return run_audit(args.report)


if __name__ == "__main__":
    raise SystemExit(main())
