from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.core.ast_nodes import (
    NodoEsperar,
    NodoFuncion,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoRetorno,
    NodoThrow,
    NodoTryCatch,
    NodoValor,
)
from tests.integration.transpilers.backend_contracts import TRANSPILERS

CONTRACT_PATH = Path(__file__).resolve().parents[3] / "data" / "language_equivalence.yml"
SNAPSHOTS_DIR = Path(__file__).resolve().parent / "golden_language_equivalence"
CRITICAL_FEATURES = ("decoradores", "manejo_errores", "async", "imports_corelibs")


def _validate_syntax_output(backend: str, code: str) -> tuple[str, str]:
    if backend == "python":
        import ast

        try:
            ast.parse(code)
            return "ok", "ast.parse correcto"
        except SyntaxError as exc:
            return "fail", str(exc)

    if backend == "javascript":
        if not shutil.which("node"):
            return "skipped", "node no disponible"
        with tempfile.TemporaryDirectory(prefix="leq_js_") as tmp:
            p = Path(tmp) / "main.js"
            p.write_text(code, encoding="utf-8")
            result = subprocess.run(["node", "--check", str(p)], text=True, capture_output=True)
        return ("ok", "node --check") if result.returncode == 0 else ("fail", result.stderr.strip())

    if backend == "rust":
        opens = code.count("{")
        closes = code.count("}")
        if opens != closes:
            return "fail", "llaves desbalanceadas en salida rust"
        return "ok", "estructura rust mínima válida"

    if backend == "go":
        gofmt = shutil.which("gofmt")
        if not gofmt:
            return "skipped", "gofmt no disponible"
        with tempfile.TemporaryDirectory(prefix="leq_go_") as tmp:
            p = Path(tmp) / "main.go"
            p.write_text(code, encoding="utf-8")
            result = subprocess.run([gofmt, "-w", str(p)], text=True, capture_output=True)
        return ("ok", "gofmt parse correcto") if result.returncode == 0 else ("fail", result.stderr.strip())

    if backend == "cpp":
        if "#include" in code or ("{" in code and "}" in code):
            return "ok", "estructura C++ mínima válida"
        return "fail", "cabecera/bloques C++ ausentes"

    if backend == "java":
        return ("ok", "estructura Java no vacía") if "class Main" in code else ("fail", "class Main ausente")

    if backend == "wasm":
        if "(module" in code or "(import \"pcobra:" in code:
            return "ok", "estructura WAT mínima válida"
        return "fail", "estructura WAT ausente"

    if backend == "asm":
        return ("ok", "salida asm no vacía") if code.strip() else ("fail", "salida asm vacía")

    return "fail", f"backend no soportado: {backend}"


def _load_contract() -> dict:
    command = [
        sys.executable,
        "-c",
        (
            "import json, yaml; from pathlib import Path; "
            "p = Path(r'" + str(CONTRACT_PATH) + "'); "
            "print(json.dumps(yaml.safe_load(p.read_text(encoding='utf-8')), ensure_ascii=False))"
        ),
    ]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("Contrato de equivalencia inválido")
    return payload


def _feature_map() -> dict[str, dict]:
    payload = _load_contract()
    features = payload.get("features")
    if not isinstance(features, list):
        raise RuntimeError(f"Contrato inválido en {CONTRACT_PATH}: claves={list(payload)}")
    return {item["id"]: item for item in features}


def _feature_nodes(feature_id: str) -> list[object]:
    fixtures = {
        "decoradores": [
            NodoFuncion(
                "saludar",
                ["nombre"],
                [NodoRetorno(NodoValor("hola"))],
                decoradores=[NodoIdentificador("traza")],
            )
        ],
        "imports_corelibs": [NodoLlamadaFuncion("longitud", [NodoValor(3)])],
        "manejo_errores": [
            NodoTryCatch(
                [NodoThrow(NodoValor("fallo"))],
                "error",
                [NodoThrow(NodoValor("error"))],
                [],
            )
        ],
        "async": [
            NodoFuncion(
                "obtener_datos",
                [],
                [NodoRetorno(NodoEsperar(NodoLlamadaFuncion("fetch", [])))],
                asincronica=True,
            )
        ],
    }
    return fixtures[feature_id]


def _generate(backend: str, nodes: list[object]) -> str:
    module_name, class_name = TRANSPILERS[backend]
    transpiler = getattr(importlib.import_module(module_name), class_name)()
    out = transpiler.generate_code(nodes)
    return "\n".join(out) if isinstance(out, list) else str(out)


def _contract_status(feature_id: str, backend: str) -> str:
    features = _feature_map()
    if backend == "python":
        return "full"
    return features[feature_id]["backend_equivalents"][backend]["status"]


def _expected_markers(feature_id: str, backend: str) -> tuple[str, ...]:
    features = _feature_map()
    if backend == "python":
        return tuple(features[feature_id].get("python_expected_markers", []))
    return tuple(features[feature_id]["backend_equivalents"][backend].get("expected_markers", []))


@pytest.mark.parametrize("feature_id", CRITICAL_FEATURES)
@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_language_equivalence_contract_transpiles_and_validates_syntax(backend: str, feature_id: str):
    generated = _generate(backend, _feature_nodes(feature_id))
    assert generated.strip(), f"{backend} no generó salida para {feature_id}"

    status = _contract_status(feature_id, backend)
    syntax_status, syntax_message = _validate_syntax_output(backend, generated)

    if status == "full":
        assert syntax_status in {"ok", "skipped"}, (
            f"{backend}/{feature_id} (full) debe validar sintaxis, obtenido={syntax_status}: {syntax_message}"
        )
    else:
        assert syntax_status in {"ok", "skipped"}, (
            f"{backend}/{feature_id} no debe romper validación mínima: {syntax_status}: {syntax_message}"
        )


@pytest.mark.parametrize("feature_id", CRITICAL_FEATURES)
@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_language_equivalence_contract_minimum_markers(feature_id: str, backend: str):
    generated = _generate(backend, _feature_nodes(feature_id))
    for marker in _expected_markers(feature_id, backend):
        assert marker in generated, f"No se encontró marcador `{marker}` en {backend}/{feature_id}"


@pytest.mark.parametrize("feature_id", CRITICAL_FEATURES)
@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_language_equivalence_contract_critical_snapshots(feature_id: str, backend: str):
    snapshot = SNAPSHOTS_DIR / f"{backend}.{feature_id}.golden"
    assert snapshot.exists(), f"Falta snapshot crítico: {snapshot}"

    generated = _generate(backend, _feature_nodes(feature_id)).strip() + "\n"
    expected = snapshot.read_text(encoding="utf-8")
    assert generated == expected
