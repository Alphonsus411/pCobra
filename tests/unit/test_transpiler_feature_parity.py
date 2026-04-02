from __future__ import annotations

import importlib
from functools import lru_cache

import pytest

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoClase,
    NodoCondicional,
    NodoDecorador,
    NodoDiccionario,
    NodoEsperar,
    NodoFuncion,
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoLista,
    NodoLlamadaFuncion,
    NodoMetodo,
    NodoRetorno,
    NodoRomper,
    NodoValor,
)
from pcobra.cobra.transpilers.compatibility_matrix import (
    AST_FEATURE_EVIDENCE_BASELINE,
    AST_FEATURES,
    validate_ast_feature_parity_release_gate,
)
from tests.integration.transpilers.backend_contracts import TRANSPILERS
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def _feature_nodes(feature: str):
    if feature == "funciones":
        return [
            NodoFuncion("sumar", ["a"], [NodoRetorno(NodoIdentificador("a"))]),
            NodoLlamadaFuncion("sumar", [NodoValor(1)]),
        ]
    if feature == "clases":
        return [
            NodoClase(
                "Demo",
                [NodoMetodo("saludar", ["self"], [NodoRetorno(NodoValor("ok"))])],
            )
        ]
    if feature == "decoradores":
        return [
            NodoFuncion(
                "decorada",
                [],
                [NodoRetorno(NodoValor(1))],
                decoradores=[NodoDecorador(NodoIdentificador("traza"))],
            ),
            NodoLlamadaFuncion("decorada", []),
        ]
    if feature == "control_flujo":
        return [
            NodoCondicional(
                NodoValor(True),
                [NodoAsignacion("x", NodoValor(1))],
                [NodoAsignacion("x", NodoValor(2))],
            ),
            NodoBucleMientras(NodoValor(True), [NodoRomper()]),
        ]
    if feature == "colecciones":
        return [
            NodoAsignacion("valores", NodoLista([NodoValor(1), NodoValor(2)])),
            NodoAsignacion("tabla", NodoDiccionario([(NodoValor("k"), NodoValor(1))])),
        ]
    if feature == "async":
        return [
            NodoFuncion("af", [], [NodoRetorno(NodoValor(1))], asincronica=True),
            NodoEsperar(NodoLlamadaFuncion("af", [])),
        ]
    if feature == "holobit":
        return [NodoHolobit("hb", [1, 2, 3]), NodoGraficar(NodoIdentificador("hb"))]
    raise ValueError(f"Feature no soportada: {feature}")


def _transpile(backend: str, nodes: list[object]) -> str:
    module_name, class_name = TRANSPILERS[backend]
    transpiler = getattr(importlib.import_module(module_name), class_name)()
    if hasattr(transpiler, "transpilar"):
        return transpiler.transpilar(nodes)
    return transpiler.generate_code(nodes)


DEGRADATION_MARKERS = (
    "contrato partial",
    "partial contract",
    "no soportado",
    "requires external runtime",
    "runtime host-managed",
)


def _infer_observed_level(backend: str, feature: str, output: str) -> str:
    rendered = output.strip()
    lowered = rendered.lower()
    if not rendered:
        return "none"

    if any(marker in lowered for marker in DEGRADATION_MARKERS):
        return "partial"

    if backend == "python":
        if feature == "holobit":
            return (
                "full"
                if "_cobra_import_holobit_runtime" in rendered and "cobra_holobit" in rendered
                else "partial"
            )
        if feature == "async":
            return "full" if "import asyncio" in rendered and "await" in rendered else "partial"
        if feature == "clases":
            return "full" if "class Demo" in rendered and "def saludar" in rendered else "partial"
        if feature == "colecciones":
            return "full" if "valores =" in rendered and "tabla =" in rendered else "partial"
        if feature == "control_flujo":
            return "full" if "x =" in rendered else "partial"
        return "full" if "from core.nativos import *" in rendered else "partial"

    if backend == "javascript":
        if feature == "async":
            return (
                "full"
                if "cobraJsCorelibs" in rendered and "cobraJsStandardLibrary" in rendered and "await" in rendered
                else "partial"
            )
        return (
            "full"
            if "cobraJsCorelibs" in rendered and "cobraJsStandardLibrary" in rendered
            else "partial"
        )

    if backend == "rust" and feature == "funciones":
        return "full" if "fn sumar" in rendered and "sumar(1);" in rendered else "partial"

    if backend == "cpp" and feature == "funciones":
        return "full" if "auto sumar" in rendered and "sumar(1);" in rendered else "partial"

    return "partial"


@lru_cache(maxsize=1)
def _compute_feature_evidence() -> dict[str, dict[str, str]]:
    evidence: dict[str, dict[str, str]] = {backend: {} for backend in OFFICIAL_TARGETS}

    for backend in OFFICIAL_TARGETS:
        for feature in AST_FEATURES:
            nodes = _feature_nodes(feature)
            try:
                output = _transpile(backend, nodes)
            except Exception as exc:
                evidence[backend][feature] = "none"
                continue

            assert output.strip(), f"Salida vacía para {backend}.{feature}"
            if feature == "holobit":
                assert "cobra_holobit" in output, (
                    f"Salida de holobit incoherente para {backend}: faltó hook cobra_holobit."
                )
            evidence[backend][feature] = _infer_observed_level(backend, feature, output)

    return evidence


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("feature", AST_FEATURES)
def test_official_transpilers_feature_contract_is_executable(backend: str, feature: str):
    evidence = _compute_feature_evidence()
    assert evidence[backend][feature] == AST_FEATURE_EVIDENCE_BASELINE[backend][feature]


def test_feature_parity_matrix_evidence_matches_contract():
    evidence = _compute_feature_evidence()
    assert evidence == AST_FEATURE_EVIDENCE_BASELINE
    validate_ast_feature_parity_release_gate(evidence)


def test_wasm_lowering_error_is_contractual_and_homogeneous():
    from pcobra.cobra.transpilers.transpiler.to_wasm import TranspiladorWasm

    transpiler = TranspiladorWasm()
    with pytest.raises(RuntimeError, match="WASM_CONTRACT_ERROR: lowering i32 no soportado"):
        transpiler._obtener_i32(NodoLista([NodoValor(1)]), "tests.wasm.lowering")
