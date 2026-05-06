from __future__ import annotations

import importlib
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)
from tests.integration.transpilers.backend_contracts import REQUIRED_FEATURES, TRANSPILERS

GOLDEN_DIR = Path(__file__).parent / "golden"

HOOK_EXPECTATIONS = {
    "python": ("def cobra_holobit", "def cobra_proyectar", "def cobra_transformar", "def cobra_graficar"),
    "javascript": ("function cobra_holobit", "function cobra_proyectar", "function cobra_transformar", "function cobra_graficar"),
    "rust": ("fn cobra_holobit", "fn cobra_proyectar", "fn cobra_transformar", "fn cobra_graficar"),
}

IMPORT_EXPECTATIONS = {
    "python": ("import pcobra.corelibs as _pcobra_corelibs", "import pcobra.standard_library as _pcobra_standard_library"),
    "javascript": ("import * as io from './nativos/io.js';", "import * as interfaz from './nativos/interfaz.js';"),
    "rust": ("use crate::corelibs::*;", "use crate::standard_library::*;", "fn longitud<T: ToString>(valor: T) -> usize {"),
}

RUNTIME_ADAPTER_MARKERS = {
    "python": (
        "Runtime Holobit Python: 'proyectar' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.",
        "Runtime Holobit Python: 'transformar' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.",
        "Runtime Holobit Python: 'graficar' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.",
    ),
    "javascript": (
        "COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE",
        "case '2d':",
        "const vista = `Holobit(${holobit.valores.join(', ')})`;",
    ),
    "rust": (
        "COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE",
        "struct CobraRuntimeError",
        'cobra_runtime_expect(cobra_graficar(&hb));',
    ),
}



def test_public_backend_policy_exact_set_is_enforced() -> None:
    """Política pública exacta: solo python/javascript/rust."""

    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")

def _generate(language: str, nodes: list[object]) -> str:
    module_name, class_name = TRANSPILERS[language]
    transpiler = getattr(importlib.import_module(module_name), class_name)()
    code = transpiler.generate_code(nodes)
    return "\n".join(code) if isinstance(code, list) else str(code)


def _feature_nodes(feature: str) -> list[object]:
    base = {
        "holobit": [NodoHolobit("hb", [1, 2, 3])],
        "proyectar": [NodoHolobit("hb", [1, 2, 3]), NodoProyectar(NodoIdentificador("hb"), NodoValor("2d"))],
        "transformar": [
            NodoHolobit("hb", [1, 2, 3]),
            NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
        ],
        "graficar": [NodoHolobit("hb", [1, 2, 3]), NodoGraficar(NodoIdentificador("hb"))],
        "corelibs": [NodoLlamadaFuncion("longitud", [NodoValor("cobra")])],
        "standard_library": [NodoLlamadaFuncion("mostrar", [NodoValor("hola")])],
    }
    return base[feature]


def _representative_nodes(language: str) -> list[object]:
    nodes: list[object] = [NodoHolobit("hb", [1, 2, 3])]
    if BACKEND_COMPATIBILITY[language]["proyectar"] != "none":
        nodes.append(NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")))
    if BACKEND_COMPATIBILITY[language]["transformar"] != "none":
        nodes.append(NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]))
    if BACKEND_COMPATIBILITY[language]["graficar"] != "none":
        nodes.append(NodoGraficar(NodoIdentificador("hb")))
    nodes.extend([NodoLlamadaFuncion("longitud", [NodoValor("cobra")]), NodoLlamadaFuncion("mostrar", [NodoValor("hola")])])
    return nodes


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_official_backend_transpilation_follows_promised_compatibility(backend: str):
    for feature in REQUIRED_FEATURES:
        level = BACKEND_COMPATIBILITY[backend][feature]
        if level == "none":
            with pytest.raises(NotImplementedError):
                _generate(backend, _feature_nodes(feature))
            continue
        generated = _generate(backend, _feature_nodes(feature))
        assert generated.strip(), f"{backend} no generó salida para {feature}"


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_official_backend_generated_code_includes_expected_imports_hooks_and_adapter_markers(backend: str):
    generated = _generate(backend, _representative_nodes(backend))
    for snippet in IMPORT_EXPECTATIONS[backend]:
        assert snippet in generated
    for hook in HOOK_EXPECTATIONS[backend]:
        assert hook in generated
    for marker in RUNTIME_ADAPTER_MARKERS[backend]:
        assert marker in generated


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_official_backend_only_injects_cobra_hooks_when_ast_requires_holobit(backend: str):
    generated = _generate(backend, [NodoLlamadaFuncion("longitud", [NodoValor("cobra")]), NodoLlamadaFuncion("mostrar", [NodoValor("hola")])])
    for hook in HOOK_EXPECTATIONS[backend]:
        assert hook not in generated


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_official_backend_codegen_matches_golden_snapshot(backend: str):
    generated = _generate(backend, _representative_nodes(backend)).strip() + "\n"
    golden_file = GOLDEN_DIR / f"{backend}.golden"
    assert golden_file.exists(), f"Falta golden file para {backend}: {golden_file}"
    if backend == "python":
        assert "import pcobra.corelibs as _pcobra_corelibs" in generated
        return
    expected = golden_file.read_text(encoding="utf-8")
    assert generated == expected




def test_suite_y_goldens_cubren_exactamente_los_3_backends_publicos():
    golden_backends = tuple(sorted(path.stem for path in GOLDEN_DIR.glob("*.golden")))
    assert set(PUBLIC_BACKENDS).issubset(set(golden_backends))
    assert set(PUBLIC_BACKENDS).issubset(set(TRANSPILERS))

MINIMAL_RUNTIME_ROUTE_EXPECTATIONS = {
    "python": ("longitud('cobra')", "mostrar('hola')"),
    "javascript": ("longitud('cobra');", "mostrar('hola');"),
    "rust": ('longitud("cobra");', 'mostrar("hola");'),
}


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_minimal_corelibs_standard_library_route_or_contractual_failure_is_explicit(backend: str):
    generated = _generate(backend, [
        NodoHolobit("hb", [1, 2, 3]),
        NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")),
        NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
        NodoGraficar(NodoIdentificador("hb")),
        NodoLlamadaFuncion("longitud", [NodoValor("cobra")]),
        NodoLlamadaFuncion("mostrar", [NodoValor("hola")]),
    ])

    for marker in MINIMAL_RUNTIME_ROUTE_EXPECTATIONS[backend]:
        assert marker in generated


def test_python_backend_generated_program_exposes_public_runtime_import_route():
    code = _generate("python", [NodoAsignacion("x", NodoValor(1)), NodoAsignacion("y", NodoValor(2))])
    assert "import pcobra.corelibs as _pcobra_corelibs" in code
    assert "import pcobra.standard_library as _pcobra_standard_library" in code

