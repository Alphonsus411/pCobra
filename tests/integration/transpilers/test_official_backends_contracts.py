from __future__ import annotations

import importlib
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
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
    "wasm": ("(func $cobra_holobit", "(func $cobra_proyectar", "(func $cobra_transformar", "(func $cobra_graficar"),
    "go": ("func cobra_holobit", "func cobra_proyectar", "func cobra_transformar", "func cobra_graficar"),
    "cpp": ("inline CobraHolobit cobra_holobit", "inline std::vector<double> cobra_proyectar", "inline CobraHolobit cobra_transformar", "inline std::string cobra_graficar"),
    "java": ("private static CobraHolobit cobra_holobit", "private static double[] cobra_proyectar", "private static CobraHolobit cobra_transformar", "private static String cobra_graficar"),
    "asm": ("cobra_holobit:", "cobra_proyectar:", "cobra_transformar:", "cobra_graficar:"),
}

IMPORT_EXPECTATIONS = {
    "python": ("from corelibs import *", "from standard_library import *"),
    "javascript": ("import * as io from './nativos/io.js';", "import * as interfaz from './nativos/interfaz.js';"),
    "rust": ("use crate::corelibs::*;", "use crate::standard_library::*;", "fn longitud<T: ToString>(valor: T) -> usize {"),
    "wasm": (
        ";; backend wasm: adaptadores host-managed de corelibs y standard_library",
        '(import "pcobra:corelibs" "longitud"',
        '(import "pcobra:standard_library" "mostrar"',
    ),
    "go": ('"cobra/corelibs"', '"cobra/standard_library"'),
    "cpp": ("#include <cobra/corelibs.hpp>", "#include <cobra/standard_library.hpp>"),
    "java": ("import cobra.corelibs.*;", "import cobra.standard_library.*;"),
    "asm": ("; backend asm: imports de runtime administrados externamente",),
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
    "wasm": (
        ";; backend wasm: hooks Holobit delegados en runtime host-managed de pcobra",
        "Runtime Holobit Wasm: si el host no implementa pcobra:holobit",
        '(import "pcobra:holobit" "cobra_proyectar"',
        '(import "pcobra:holobit" "cobra_transformar"',
    ),
    "go": (
        "type CobraHolobit struct",
        "panic(",
        "func mostrar(valores ...any) any {",
    ),
    "cpp": (
        "COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE",
        "inline std::size_t longitud(const T& valor) {",
        "parámetro numérico no soportado por contrato partial del adaptador oficial (sin fallback)",
        'cobra_transformar(hb, "rotar", {cobra_runtime_arg(90)});',
    ),
    "java": (
        "COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE",
        "private static int longitud(Object valor) {",
        "parámetro numérico no soportado por contrato partial del adaptador oficial (sin fallback)",
        'cobra_transformar(hb, "rotar", 90);',
    ),
    "asm": (
        "runtime de inspección/diagnóstico",
        "la proyección requiere runtime externo (fallo contractual explícito, sin fallback silencioso).",
        "la visualización requiere runtime externo (fallo contractual explícito, sin fallback silencioso).",
    ),
}


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


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_official_backend_transpilation_follows_promised_compatibility(backend: str):
    for feature in REQUIRED_FEATURES:
        level = BACKEND_COMPATIBILITY[backend][feature]
        if level == "none":
            with pytest.raises(NotImplementedError):
                _generate(backend, _feature_nodes(feature))
            continue
        generated = _generate(backend, _feature_nodes(feature))
        assert generated.strip(), f"{backend} no generó salida para {feature}"


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_official_backend_generated_code_includes_expected_imports_hooks_and_adapter_markers(backend: str):
    generated = _generate(backend, _representative_nodes(backend))
    for snippet in IMPORT_EXPECTATIONS[backend]:
        assert snippet in generated
    for hook in HOOK_EXPECTATIONS[backend]:
        assert hook in generated
    for marker in RUNTIME_ADAPTER_MARKERS[backend]:
        assert marker in generated


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_official_backend_only_injects_cobra_hooks_when_ast_requires_holobit(backend: str):
    generated = _generate(backend, [NodoLlamadaFuncion("longitud", [NodoValor("cobra")]), NodoLlamadaFuncion("mostrar", [NodoValor("hola")])])
    for hook in HOOK_EXPECTATIONS[backend]:
        assert hook not in generated


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_official_backend_codegen_matches_golden_snapshot(backend: str):
    generated = _generate(backend, _representative_nodes(backend)).strip() + "\n"
    golden_file = GOLDEN_DIR / f"{backend}.golden"
    assert golden_file.exists(), f"Falta golden file para {backend}: {golden_file}"
    assert generated == golden_file.read_text(encoding="utf-8")




def test_suite_y_goldens_cubren_exactamente_los_8_backends_oficiales():
    golden_backends = tuple(sorted(path.stem for path in GOLDEN_DIR.glob("*.golden")))
    assert set(golden_backends) == set(OFFICIAL_TARGETS)
    assert len(golden_backends) == 8
    assert set(TRANSPILERS) == set(OFFICIAL_TARGETS)
    assert len(TRANSPILERS) == 8

MINIMAL_RUNTIME_ROUTE_EXPECTATIONS = {
    "python": ("longitud('cobra')", "mostrar('hola')"),
    "javascript": ("longitud('cobra');", "mostrar('hola');"),
    "rust": ('longitud("cobra");', 'mostrar("hola");'),
    "go": ('longitud("cobra")', 'mostrar("hola")'),
    "cpp": ('longitud("cobra");', 'mostrar("hola");'),
    "java": ('longitud("cobra")', 'mostrar("hola")'),
    "wasm": (
        '(import "pcobra:corelibs" "longitud"',
        '(import "pcobra:standard_library" "mostrar"',
        'host-managed',
    ),
    "asm": (
        "CALL longitud 'cobra'",
        "CALL mostrar 'hola'",
        "runtime de inspección/diagnóstico",
        "TRAP",
    ),
}


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
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


def test_python_backend_generated_program_executes_in_repo_runtime():
    code = _generate("python", [NodoAsignacion("x", NodoValor(1)), NodoAsignacion("y", NodoValor(2))])
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        temp_path = tmp.name

    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    try:
        proc = subprocess.run(
            ["python", temp_path],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert proc.returncode == 0, proc.stderr
    finally:
        Path(temp_path).unlink(missing_ok=True)
