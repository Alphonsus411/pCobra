from __future__ import annotations

import importlib
import os
import shutil
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
    "python": (),
    "javascript": ("function cobra_proyectar", "function cobra_transformar", "function cobra_graficar"),
    "rust": ("fn cobra_proyectar", "fn cobra_transformar", "fn cobra_graficar"),
    "wasm": ("(func $cobra_proyectar", "(func $cobra_transformar", "(func $cobra_graficar"),
    "go": ("func cobraProyectar", "func cobraTransformar", "func cobraGraficar"),
    "cpp": ("inline void cobra_proyectar", "inline void cobra_transformar", "inline void cobra_graficar"),
    "java": ("private static void cobraProyectar", "private static void cobraTransformar", "private static void cobraGraficar"),
    "asm": ("cobra_proyectar:", "cobra_transformar:", "cobra_graficar:"),
}

IMPORT_EXPECTATIONS = {
    "python": ("from corelibs import *", "from standard_library import *"),
    "javascript": ("import * as io from './nativos/io.js';", "import * as texto from './nativos/texto.js';"),
    "rust": ("use crate::corelibs::*;", "use crate::standard_library::*;"),
    "wasm": (";; backend wasm: imports de runtime administrados externamente",),
    "go": ('"cobra/corelibs"', '"cobra/standard_library"'),
    "cpp": ("#include <cobra/corelibs.hpp>", "#include <cobra/standard_library.hpp>"),
    "java": ("import cobra.corelibs.*;", "import cobra.standard_library.*;"),
    "asm": ("; backend asm: imports de runtime administrados externamente",),
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
    nodes.extend(
        [
            NodoLlamadaFuncion("longitud", [NodoValor("cobra")]),
            NodoLlamadaFuncion("mostrar", [NodoValor("hola")]),
        ]
    )
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
def test_official_backend_generated_code_includes_expected_imports_and_hooks(backend: str):
    generated = _generate(backend, _representative_nodes(backend))

    for snippet in IMPORT_EXPECTATIONS[backend]:
        assert snippet in generated

    for hook in HOOK_EXPECTATIONS[backend]:
        assert hook in generated


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_official_backend_codegen_matches_golden_snapshot(backend: str):
    generated = _generate(backend, _representative_nodes(backend)).strip() + "\n"
    golden_file = GOLDEN_DIR / f"{backend}.golden"
    assert golden_file.exists(), f"Falta golden file para {backend}: {golden_file}"
    assert generated == golden_file.read_text(encoding="utf-8")


def test_python_backend_generated_program_executes_in_repo_runtime():
    code = _generate(
        "python",
        [
            NodoAsignacion("x", NodoValor(1)),
            NodoAsignacion("y", NodoValor(2)),
        ],
    )
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
            timeout=20,
        )
    finally:
        os.unlink(temp_path)

    assert proc.returncode == 0, proc.stderr


def test_javascript_backend_generated_program_executes_when_node_runtime_is_available():
    if shutil.which("node") is None:
        pytest.skip("Node.js no está instalado en el entorno")

    node_fetch_probe = subprocess.run(
        ["node", "-e", "import(\"node-fetch\").then(()=>process.exit(0)).catch(()=>process.exit(1))"],
        capture_output=True,
        text=True,
    )
    if node_fetch_probe.returncode != 0:
        pytest.skip("Node.js disponible pero falta dependencia runtime 'node-fetch'")

    code = _generate(
        "javascript",
        [
            NodoAsignacion("x", NodoValor(1)),
            NodoAsignacion("y", NodoValor(2)),
        ],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        script_path = tmp_path / "main.mjs"
        script_path.write_text(code, encoding="utf-8")

        src_nativos = Path(__file__).resolve().parents[3] / "src" / "pcobra" / "core" / "nativos"
        shutil.copytree(src_nativos, tmp_path / "nativos")

        proc = subprocess.run(
            ["node", str(script_path)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=20,
        )

    assert proc.returncode == 0, proc.stderr
