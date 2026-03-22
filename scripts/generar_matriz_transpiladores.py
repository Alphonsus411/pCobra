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
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, target_label  # noqa: E402

BEST_EFFORT_RUNTIME_TARGETS_INTERNAL = BEST_EFFORT_RUNTIME_TARGETS


def _runtime_policy(target: str) -> str:
    if target in OFFICIAL_RUNTIME_TARGETS:
        return "runtime_oficial"
    if target in BEST_EFFORT_RUNTIME_TARGETS_INTERNAL:
        return "runtime_best_effort_no_publico"
    if target in NO_RUNTIME_TARGETS:
        return "solo_transpilacion"
    raise RuntimeError(f"Target fuera de política conocida: {target}")


def _build_markdown() -> str:
    lines = [
        "# Matriz de transpiladores",
        "",
        "Generado desde `scripts/generar_matriz_transpiladores.py`.",
        "",
        "## Resumen de política",
        "",
        render_public_policy_summary(markup="markdown"),
        f"- **Targets con runtime best-effort no público**: {', '.join(f'`{t}`' for t in BEST_EFFORT_RUNTIME_TARGETS_INTERNAL)}.",
        f"- **Targets solo de transpilación**: {', '.join(f'`{t}`' for t in NO_RUNTIME_TARGETS)}.",
        "",
        "## Estado público por backend",
        "",
        "| Backend | Nombre | Tier | runtime_publico | holobit_publico | sdk_real |",
        "|---|---|---|---|---|---|",
    ]
    for backend in OFFICIAL_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        runtime_status = _runtime_policy(backend)
        holobit_status = (
            "sdk_full"
            if backend in SDK_COMPATIBLE_TARGETS
            else "adaptador_mantenido_partial"
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
            "> `runtime_policy` distingue explícitamente entre transpilación oficial, runtime oficial y runtime best-effort no público.",
            "> `holobit_publico` resume la promesa pública: `sdk_full` solo aplica a `python`; `adaptador_mantenido_partial` aplica a `rust`, `javascript` y `cpp`; el resto permanece en `partial`.",
        ]
    )
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
