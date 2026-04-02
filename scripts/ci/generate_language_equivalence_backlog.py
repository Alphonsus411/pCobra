#!/usr/bin/env python3
"""Genera backlog técnico automáticamente para gaps de equivalencia (status != full)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "language_equivalence.yml"
OUT_PATH = ROOT / "data" / "language_equivalence_backlog.md"


def main() -> int:
    payload = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))
    today = date.today().isoformat()

    lines: list[str] = [
        "# Backlog técnico de equivalencia (autogenerado)",
        "",
        f"Fecha de generación: {today}",
        f"Versión contrato: {payload.get('version', 'n/a')}",
        "",
        "## Tareas abiertas (status != full)",
        "",
    ]

    open_tasks = 0
    for feature in payload["features"]:
        feature_id = feature["id"]
        for backend, details in feature["backend_equivalents"].items():
            status = details["status"]
            if status == "full":
                continue
            open_tasks += 1
            limitations = details.get("limitations", [])
            limitation_msg = "; ".join(limitations) if limitations else "Sin limitaciones documentadas."
            lines.append(
                f"- [ ] `{feature_id}` en `{backend}` → elevar de `{status}` a `full`. "
                f"Contexto: {limitation_msg}"
            )

    if open_tasks == 0:
        lines.append("- Sin tareas abiertas: todas las features están en full.")

    lines.extend(
        [
            "",
            "## Regla de mantenimiento",
            "",
            "Ejecutar este script tras cualquier cambio en la matriz o backends para mantener el backlog sincronizado.",
        ]
    )

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Backlog actualizado: {OUT_PATH} ({open_tasks} tareas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
