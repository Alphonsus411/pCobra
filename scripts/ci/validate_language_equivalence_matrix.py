#!/usr/bin/env python3
"""Valida la matriz de equivalencia versionada contra compatibility_matrix.py."""

from __future__ import annotations

import subprocess
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
BASELINE_PATH = ROOT / "data" / "language_equivalence_baseline.yml"
DOWNGRADES_PATH = ROOT / "data" / "language_equivalence_downgrades.yml"
DOC_PATH = ROOT / "docs" / "language_equivalence_matrix.md"
CONTRACT_TEST_PATH = ROOT / "tests" / "integration" / "transpilers" / "test_language_equivalence_contract.py"
VALID_STATUSES = {"full", "partial", "none"}
STATUS_SOURCES = {
    "AST_FEATURE_MINIMUM_CONTRACT": AST_FEATURE_MINIMUM_CONTRACT,
    "BACKEND_COMPATIBILITY": BACKEND_COMPATIBILITY,
    "BACKEND_HOLOBIT_SDK_CAPABILITIES": BACKEND_HOLOBIT_SDK_CAPABILITIES,
}


def _load_yaml(path: Path, *, required: bool) -> dict:
    if not path.exists():
        if required:
            raise SystemExit(f"Falta archivo requerido: {path}")
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"YAML inválido en {path}")
    return payload


def _load_contract() -> dict:
    data = _load_yaml(DATA_PATH, required=True)
    if "features" not in data:
        raise SystemExit("Contrato YAML inválido: se esperaba clave `features`.")
    return data


def _build_status_table(payload: dict) -> dict[tuple[str, str], str]:
    table: dict[tuple[str, str], str] = {}
    for feature in payload.get("features", []):
        feature_id = feature["id"]
        table[(feature_id, "python")] = "full"
        for backend, metadata in feature.get("backend_equivalents", {}).items():
            table[(feature_id, backend)] = metadata["status"]
    return table


def _validate_downgrades_against_baseline(contract: dict) -> None:
    baseline = _load_yaml(BASELINE_PATH, required=True)
    approved_payload = _load_yaml(DOWNGRADES_PATH, required=True)

    baseline_table = _build_status_table(baseline)
    current_table = _build_status_table(contract)
    approved = {
        (item["feature"], item["backend"])
        for item in approved_payload.get("approved_downgrades", [])
        if isinstance(item, dict) and "feature" in item and "backend" in item
    }

    downgrades: list[str] = []
    for key, previous in baseline_table.items():
        current = current_table.get(key)
        if previous == "full" and current in {"partial", "none"} and key not in approved:
            feature, backend = key
            downgrades.append(
                f"feature={feature}, backend={backend}, baseline={previous}, actual={current}"
            )

    if downgrades:
        joined = "\n - ".join(downgrades)
        raise SystemExit(
            "Downgrade detectado full -> partial/none sin aprobación explícita en "
            f"{DOWNGRADES_PATH}:\n - {joined}"
        )


def _run_contract_test_suite() -> None:
    if not CONTRACT_TEST_PATH.exists():
        raise SystemExit(f"No existe suite contractual requerida: {CONTRACT_TEST_PATH}")

    command = [sys.executable, "-m", "pytest", str(CONTRACT_TEST_PATH), "-q"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        details = "\n".join(part for part in [stdout, stderr] if part)
        raise SystemExit(f"La evidencia ejecutable del contrato falló.\n{details}")


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

    _validate_downgrades_against_baseline(payload)
    _run_contract_test_suite()

    print("Contrato de equivalencia validado correctamente + suite contractual en verde.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
