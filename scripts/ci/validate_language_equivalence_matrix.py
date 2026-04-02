#!/usr/bin/env python3
"""Valida la matriz de equivalencia versionada contra compatibility_matrix.py."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.transpilers.compatibility_matrix import (  # noqa: E402
    AST_FEATURE_MINIMUM_CONTRACT,
    BACKEND_COMPATIBILITY,
    BACKEND_HOLOBIT_SDK_CAPABILITIES,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS  # noqa: E402

DATA_PATH = ROOT / "data" / "language_equivalence.yml"
DOC_PATH = ROOT / "docs" / "language_equivalence_matrix.md"
VALID_STATUSES = {"full", "partial", "none"}
STATUS_SOURCES = {
    "AST_FEATURE_MINIMUM_CONTRACT": AST_FEATURE_MINIMUM_CONTRACT,
    "BACKEND_COMPATIBILITY": BACKEND_COMPATIBILITY,
    "BACKEND_HOLOBIT_SDK_CAPABILITIES": BACKEND_HOLOBIT_SDK_CAPABILITIES,
}


def _load_contract() -> dict:
    if not DATA_PATH.exists():
        raise SystemExit(f"Falta contrato YAML: {DATA_PATH}")
    data = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "features" not in data:
        raise SystemExit("Contrato YAML inválido: se esperaba clave `features`.")
    return data


def main() -> int:
    if not DOC_PATH.exists():
        raise SystemExit(f"Falta documentación requerida: {DOC_PATH}")

    payload = _load_contract()
    declared_backends = payload.get("backends", [])
    if set(declared_backends) != set(OFFICIAL_TARGETS):
        raise SystemExit(
            "Backends del contrato no coinciden con OFFICIAL_TARGETS. "
            f"Contrato={declared_backends} OFFICIAL={list(OFFICIAL_TARGETS)}"
        )

    for feature in payload["features"]:
        feature_id = feature["id"]
        source_meta = feature.get("status_source", {})
        matrix_name = source_meta.get("matrix")
        matrix_key = source_meta.get("key")

        if matrix_name not in STATUS_SOURCES:
            raise SystemExit(f"Feature `{feature_id}` referencia matriz desconocida: {matrix_name}")

        matrix = STATUS_SOURCES[matrix_name]
        backend_equivalents = feature.get("backend_equivalents", {})

        if set(backend_equivalents) != (set(OFFICIAL_TARGETS) - {"python"}):
            raise SystemExit(
                f"Feature `{feature_id}` debe declarar equivalentes para todos los backends "
                "excepto python (que va en `python_equivalent`)."
            )

        if "python_equivalent" not in feature or "cobra_syntax" not in feature:
            raise SystemExit(f"Feature `{feature_id}` debe incluir `cobra_syntax` y `python_equivalent`.")

        for backend in OFFICIAL_TARGETS:
            contract_status = "full" if backend == "python" else backend_equivalents[backend]["status"]
            if contract_status not in VALID_STATUSES:
                raise SystemExit(
                    f"Status inválido en feature={feature_id}, backend={backend}: {contract_status}"
                )

            matrix_status = matrix[backend][matrix_key]
            if contract_status != matrix_status:
                raise SystemExit(
                    "Desalineación de estado entre contrato y matriz ejecutable: "
                    f"feature={feature_id}, backend={backend}, contrato={contract_status}, "
                    f"matriz={matrix_status}, fuente={matrix_name}.{matrix_key}"
                )

            limitations = [] if backend == "python" else backend_equivalents[backend].get("limitations", [])
            if contract_status != "full" and not limitations:
                raise SystemExit(
                    f"Feature `{feature_id}` backend `{backend}` requiere limitaciones cuando status != full."
                )

    print("Contrato de equivalencia validado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
