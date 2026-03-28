from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.core.ast_nodes import NodoLlamadaFuncion, NodoValor, NodoHolobit, NodoProyectar, NodoTransformar, NodoGraficar, NodoIdentificador
from tests.integration.transpilers.backend_contracts import TRANSPILERS

GOLDEN_DIR = Path(__file__).parent / "golden"


def _generate(language: str, nodes: list[object]) -> str:
    module_name, class_name = TRANSPILERS[language]
    transpiler = getattr(importlib.import_module(module_name), class_name)()
    code = transpiler.generate_code(nodes)
    return "\n".join(code) if isinstance(code, list) else str(code)


def _parse_markers(path: Path) -> dict[str, tuple[str, ...]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections[current] = []
            continue
        if current is None:
            raise ValueError(f"Formato inválido en {path}: línea fuera de sección: {raw!r}")
        sections[current].append(raw)
    return {backend: tuple(markers) for backend, markers in sections.items()}


def _exercise_nodes() -> list[object]:
    return [
        NodoHolobit("hb", [1, 2, 3]),
        NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")),
        NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
        NodoGraficar(NodoIdentificador("hb")),
        NodoLlamadaFuncion("longitud", [NodoValor("cobra")]),
        NodoLlamadaFuncion("mostrar", [NodoValor("hola")]),
    ]


def _tier_backends(tier: str) -> tuple[str, ...]:
    return tuple(backend for backend, contract in BACKEND_COMPATIBILITY.items() if contract["tier"] == tier)


@pytest.mark.parametrize(
    "tier,golden_file",
    [
        ("tier1", GOLDEN_DIR / "corelibs_standard_library_tier1.golden"),
        ("tier2", GOLDEN_DIR / "corelibs_standard_library_tier2.golden"),
    ],
)
def test_corelibs_standard_library_markers_por_tier_en_goldens(tier: str, golden_file: Path):
    expected_by_backend = _parse_markers(golden_file)
    tier_backends = _tier_backends(tier)

    assert set(expected_by_backend) == set(tier_backends)

    for backend in tier_backends:
        generated = _generate(backend, _exercise_nodes())
        for marker in expected_by_backend[backend]:
            assert marker in generated, f"{backend} ({tier}) no incluyó marcador esperado: {marker!r}"
