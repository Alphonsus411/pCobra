from __future__ import annotations

"""Matriz viva de paridad de API runtime por backend.

Este módulo extrae los exports públicos de:
- ``src/pcobra/standard_library/__init__.py``
- ``src/pcobra/corelibs/__init__.py``

Además cruza dichos exports con un mapa contractual versionado por backend
(``runtime_api_parity_snapshot.json``) para producir una salida estructurada
consumible desde ``compatibility_matrix.py`` y scripts de documentación.
"""

from dataclasses import dataclass
import ast
import json
from pathlib import Path
from typing import Final

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
STANDARD_LIBRARY_INIT: Final[Path] = REPO_ROOT / "src/pcobra/standard_library/__init__.py"
CORELIBS_INIT: Final[Path] = REPO_ROOT / "src/pcobra/corelibs/__init__.py"
SNAPSHOT_PATH: Final[Path] = Path(__file__).resolve().with_name("runtime_api_parity_snapshot.json")


@dataclass(frozen=True)
class RuntimeApiExportSets:
    standard_library: tuple[str, ...]
    corelibs: tuple[str, ...]

    @property
    def global_api(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.standard_library) | set(self.corelibs)))


def _read_all_exports(path: Path) -> tuple[str, ...]:
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
        if not isinstance(resolved, list):
            raise RuntimeError(f"{path}: __all__ debe ser lista literal")
        symbols = [item for item in resolved if isinstance(item, str)]
        if len(symbols) != len(resolved):
            raise RuntimeError(f"{path}: __all__ contiene elementos no-string")
        return tuple(symbols)
    raise RuntimeError(f"{path}: no se encontró __all__")


def extract_runtime_export_sets() -> RuntimeApiExportSets:
    return RuntimeApiExportSets(
        standard_library=_read_all_exports(STANDARD_LIBRARY_INIT),
        corelibs=_read_all_exports(CORELIBS_INIT),
    )


def _load_snapshot() -> dict[str, object]:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def build_runtime_api_matrix() -> dict[str, object]:
    exports = extract_runtime_export_sets()
    snapshot = _load_snapshot()

    backend_runtime_api = snapshot["backend_runtime_api"]
    if not isinstance(backend_runtime_api, dict):
        raise RuntimeError("runtime_api_parity_snapshot.json: backend_runtime_api inválido")

    global_api = set(exports.global_api)
    corelibs_api = set(exports.corelibs)
    standard_library_api = set(exports.standard_library)

    available_by_backend: dict[str, dict[str, list[str]]] = {}
    missing_by_backend: dict[str, dict[str, list[str]]] = {}

    for backend in OFFICIAL_TARGETS:
        backend_map = backend_runtime_api.get(backend)
        if not isinstance(backend_map, dict):
            raise RuntimeError(f"Snapshot sin backend '{backend}'")

        backend_corelibs = set(backend_map.get("corelibs", []))
        backend_standard_library = set(backend_map.get("standard_library", []))
        backend_available_global = backend_corelibs | backend_standard_library

        available_by_backend[backend] = {
            "global": sorted(backend_available_global),
            "corelibs": sorted(backend_corelibs),
            "standard_library": sorted(backend_standard_library),
        }
        missing_by_backend[backend] = {
            "global": sorted(global_api - backend_available_global),
            "corelibs": sorted(corelibs_api - backend_corelibs),
            "standard_library": sorted(standard_library_api - backend_standard_library),
        }

    return {
        "global_api": {
            "global": sorted(global_api),
            "corelibs": sorted(corelibs_api),
            "standard_library": sorted(standard_library_api),
        },
        "available_api_by_backend": available_by_backend,
        "missing_api_by_backend": missing_by_backend,
    }


def render_runtime_api_matrix_markdown(matrix: dict[str, object]) -> str:
    lines = [
        "# Matriz viva de API runtime por backend",
        "",
        "## API disponible global",
        "",
        f"- Total global: **{len(matrix['global_api']['global'])}** símbolos.",
        f"- corelibs: **{len(matrix['global_api']['corelibs'])}** símbolos.",
        f"- standard_library: **{len(matrix['global_api']['standard_library'])}** símbolos.",
        "",
        "## API parcial por backend",
        "",
        "| Backend | Disponibles (global) | Disponibles corelibs | Disponibles standard_library |",
        "|---|---:|---:|---:|",
    ]

    available = matrix["available_api_by_backend"]
    missing = matrix["missing_api_by_backend"]
    for backend in OFFICIAL_TARGETS:
        backend_available = available[backend]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{backend}`",
                    str(len(backend_available["global"])),
                    str(len(backend_available["corelibs"])),
                    str(len(backend_available["standard_library"])),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## API faltante por backend",
            "",
            "| Backend | Faltantes (global) | Faltantes corelibs | Faltantes standard_library |",
            "|---|---:|---:|---:|",
        ]
    )
    for backend in OFFICIAL_TARGETS:
        backend_missing = missing[backend]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{backend}`",
                    str(len(backend_missing["global"])),
                    str(len(backend_missing["corelibs"])),
                    str(len(backend_missing["standard_library"])),
                ]
            )
            + " |"
        )

    return "\n".join(lines) + "\n"


def validate_runtime_api_parity_snapshot() -> None:
    exports = extract_runtime_export_sets()
    snapshot = _load_snapshot()

    python_global_snapshot = set(snapshot["python_global_api_snapshot"])
    python_global_current = set(exports.global_api)

    if python_global_snapshot != python_global_current:
        missing_in_snapshot = sorted(python_global_current - python_global_snapshot)
        removed_from_python = sorted(python_global_snapshot - python_global_current)
        raise RuntimeError(
            "Snapshot de API Python desactualizado para matriz de paridad. "
            f"Nuevos símbolos sin mapear: {missing_in_snapshot}. "
            f"Símbolos removidos en Python: {removed_from_python}."
        )

    backend_runtime_api = snapshot["backend_runtime_api"]
    known_symbols = python_global_current
    for backend in OFFICIAL_TARGETS:
        backend_map = backend_runtime_api.get(backend)
        if not isinstance(backend_map, dict):
            raise RuntimeError(f"Falta backend '{backend}' en snapshot de paridad")
        for namespace in ("corelibs", "standard_library"):
            symbols = backend_map.get(namespace, [])
            if not isinstance(symbols, list):
                raise RuntimeError(
                    f"Snapshot inválido para {backend}.{namespace}: se esperaba lista"
                )
            unknown = sorted(set(symbols) - known_symbols)
            if unknown:
                raise RuntimeError(
                    f"Snapshot inválido para {backend}.{namespace}: símbolos desconocidos {unknown}"
                )
