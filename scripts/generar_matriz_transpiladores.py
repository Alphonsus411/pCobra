#!/usr/bin/env python3
"""Genera la matriz contractual pública de transpiladores.

Este script ya no intenta inferir una cobertura amplia/exploratoria del AST.
Su objetivo es regenerar la tabla pública alineada con:
- los 8 targets oficiales de transpilación;
- el subconjunto con runtime oficial;
- el subconjunto conservado como runtime best-effort no público.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ))

from pcobra.cobra.cli.target_policies import (  # noqa: E402
    ADVANCED_HOLOBIT_RUNTIME_TARGETS,
    BEST_EFFORT_RUNTIME_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    SDK_COMPATIBLE_TARGETS,
    render_public_policy_summary,
)
from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY, CONTRACT_FEATURES  # noqa: E402
from pcobra.cobra.transpilers.target_utils import target_label  # noqa: E402
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS  # noqa: E402

BEST_EFFORT_RUNTIME_TARGETS_INTERNAL = BEST_EFFORT_RUNTIME_TARGETS
GOLDEN_DIR = RAIZ / "tests" / "integration" / "transpilers" / "golden"

EVIDENCE_MARKERS: dict[str, dict[str, tuple[str, ...]]] = {
    "python": {
        "holobit": ("hb = cobra_holobit([1, 2, 3])",),
        "proyectar": ("cobra_proyectar(hb, '2d')",),
        "transformar": ("cobra_transformar(hb, 'rotar', 90)",),
        "graficar": ("cobra_graficar(hb)",),
        "corelibs": ("longitud('cobra')",),
        "standard_library": ("mostrar('hola')",),
    },
    "javascript": {
        "holobit": ("let hb = cobra_holobit([1, 2, 3]);",),
        "proyectar": ("Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk;",),
        "transformar": ("Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk;",),
        "graficar": ("Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk;",),
        "corelibs": ("longitud('cobra');",),
        "standard_library": ("mostrar('hola');",),
    },
    "rust": {
        "holobit": ("let hb = cobra_holobit(vec![1, 2, 3]);",),
        "proyectar": ("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk;",),
        "transformar": ("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk;",),
        "graficar": ("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk;",),
        "corelibs": ('longitud("cobra");',),
        "standard_library": ('mostrar("hola");',),
    },
    "wasm": {
        "holobit": ("(drop (call $cobra_holobit (i32.const 1)))",),
        "proyectar": ("backend wasm: contrato partial",),
        "transformar": ("backend wasm: contrato partial",),
        "graficar": ("backend wasm: contrato partial",),
        "corelibs": ('(import "pcobra:corelibs" "longitud"',),
        "standard_library": ('(import "pcobra:standard_library" "mostrar"',),
    },
    "go": {
        "holobit": ("hb := cobra_holobit([]float64{1, 2, 3})",),
        "proyectar": ("Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk;",),
        "transformar": ("Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk;",),
        "graficar": ("Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk;",),
        "corelibs": ('longitud("cobra")',),
        "standard_library": ('mostrar("hola")',),
    },
    "cpp": {
        "holobit": ("auto hb = cobra_holobit({ 1, 2, 3 });",),
        "proyectar": ("Runtime Holobit C++: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",),
        "transformar": ("Runtime Holobit C++: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",),
        "graficar": ("Runtime Holobit C++: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",),
        "corelibs": ('longitud("cobra");',),
        "standard_library": ('mostrar("hola");',),
    },
    "java": {
        "holobit": ("Object hb = cobra_holobit(new double[]{1, 2, 3});",),
        "proyectar": ("Runtime Holobit Java: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",),
        "transformar": ("Runtime Holobit Java: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",),
        "graficar": ("Runtime Holobit Java: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",),
        "corelibs": ('longitud("cobra")',),
        "standard_library": ('mostrar("hola")',),
    },
    "asm": {
        "holobit": ("HOLOBIT hb [1, 2, 3]",),
        "proyectar": ("TRAP",),
        "transformar": ("TRAP",),
        "graficar": ("TRAP",),
        "corelibs": ("CALL longitud 'cobra'",),
        "standard_library": ("CALL mostrar 'hola'",),
    },
}


def _runtime_policy(target: str) -> str:
    if target in OFFICIAL_RUNTIME_TARGETS:
        return "runtime oficial"
    if target in BEST_EFFORT_RUNTIME_TARGETS_INTERNAL:
        return "best-effort"
    if target in NO_RUNTIME_TARGETS:
        return "solo transpilación"
    raise RuntimeError(f"Target fuera de política conocida: {target}")


def _load_golden(backend: str) -> str:
    return (GOLDEN_DIR / f"{backend}.golden").read_text(encoding="utf-8")


def _evidence_line(content: str, marker: str) -> str:
    for line in content.splitlines():
        if marker in line:
            return line.strip()
    return f"[marker no encontrado] {marker}"


def _build_markdown() -> str:
    summary_start = "<!-- BEGIN GENERATED MATRIZ POLICY SUMMARY -->"
    summary_end = "<!-- END GENERATED MATRIZ POLICY SUMMARY -->"
    status_start = "<!-- BEGIN GENERATED MATRIZ STATUS TABLE -->"
    status_end = "<!-- END GENERATED MATRIZ STATUS TABLE -->"
    lines = [
        "# Matriz de transpiladores",
        "",
        "> ⚠️ Documento parcialmente derivado: los bloques marcados como `BEGIN/END GENERATED`",
        "> se regeneran automáticamente y no deben editarse manualmente.",
        "",
        "Fuente de generación: `scripts/generar_matriz_transpiladores.py`.",
        "",
        "## Resumen de política",
        "",
        summary_start,
        render_public_policy_summary(markup="markdown"),
        summary_end,
        "",
        "## Estado público por backend",
        "",
        status_start,
        "| Backend | Nombre | Tier | runtime_publico | holobit_publico | sdk_real |",
        "|---|---|---|---|---|---|",
    ]
    for backend in OFFICIAL_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        runtime_status = _runtime_policy(backend)
        holobit_status = (
            "SDK full solo python"
            if backend in SDK_COMPATIBLE_TARGETS
            else "adaptador mantenido (partial)"
            if backend in ADVANCED_HOLOBIT_RUNTIME_TARGETS
            else "partial"
        )
        sdk_status = "full" if backend in SDK_COMPATIBLE_TARGETS else "partial"
        row = [
            f"`{backend}`",
            target_label(backend),
            contract["tier"].replace("tier", "Tier "),
            runtime_status,
            holobit_status,
            sdk_status,
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append(status_end)
    lines.extend(
        [
            "",
            "## Matriz contractual",
            "",
            "| Backend | Nombre | Tier | runtime_policy | " + " | ".join(CONTRACT_FEATURES) + " |",
            "|---|---|---|---|" + "---|" * len(CONTRACT_FEATURES),
        ]
    )
    for backend in OFFICIAL_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        row = [
            f"`{backend}`",
            target_label(backend),
            contract["tier"].replace("tier", "Tier "),
            _runtime_policy(backend),
            *[contract[feature] for feature in CONTRACT_FEATURES],
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.extend(
        [
            "",
            "> `runtime_policy` distingue explícitamente entre runtime oficial, best-effort y solo transpilación.",
            "> `holobit_publico` resume la promesa pública: `SDK full solo python` aplica únicamente a `python`; `rust`, `javascript` y `cpp` se publican como `adaptador mantenido (partial)`; el resto permanece en `partial`.",
            "",
            "## Evidencia técnica automática (derivada de goldens)",
            "",
            "| Backend | Feature | Nivel contrato | Evidencia automática |",
            "|---|---|---|---|",
        ]
    )
    for backend in OFFICIAL_TARGETS:
        golden_content = _load_golden(backend)
        for feature in CONTRACT_FEATURES:
            level = BACKEND_COMPATIBILITY[backend][feature]
            markers = EVIDENCE_MARKERS[backend][feature]
            evidence = _evidence_line(golden_content, markers[0]).replace("|", "\\|")
            lines.append(f"| `{backend}` | `{feature}` | `{level}` | `{evidence}` |")
    return "\n".join(lines) + "\n"



def _write_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["backend", "label", "tier", "runtime_policy", *CONTRACT_FEATURES])
        for backend in OFFICIAL_TARGETS:
            contract = BACKEND_COMPATIBILITY[backend]
            writer.writerow(
                [
                    backend,
                    target_label(backend),
                    contract["tier"],
                    _runtime_policy(backend),
                    *[contract[feature] for feature in CONTRACT_FEATURES],
                ]
            )


def main() -> None:
    docs_dir = RAIZ / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "matriz_transpiladores.md").write_text(_build_markdown(), encoding="utf-8")
    _write_csv(docs_dir / "matriz_transpiladores.csv")


if __name__ == "__main__":
    main()
