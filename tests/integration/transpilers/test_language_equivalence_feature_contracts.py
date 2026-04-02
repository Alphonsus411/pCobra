from __future__ import annotations

import importlib

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import (
    AST_FEATURE_MINIMUM_CONTRACT,
    BACKEND_COMPATIBILITY,
    BACKEND_FEATURE_NODE_SUPPORT,
    LANGUAGE_EQUIVALENCE_PRIORITY_PHASES,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.core.ast_nodes import (
    NodoEsperar,
    NodoFuncion,
    NodoIdentificador,
    NodoLista,
    NodoLlamadaFuncion,
    NodoRetorno,
    NodoThrow,
    NodoTryCatch,
    NodoValor,
)
from tests.integration.transpilers.backend_contracts import TRANSPILERS

PRIORITY_FEATURES = (
    "decoradores",
    "imports_corelibs",
    "manejo_errores",
    "async",
    "tipos_compuestos",
)

TRANSPILER_FEATURE_CONSTANTS = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "PYTHON_FEATURE_NODE_SUPPORT"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "JAVASCRIPT_FEATURE_NODE_SUPPORT"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "RUST_FEATURE_NODE_SUPPORT"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "GO_FEATURE_NODE_SUPPORT"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "CPP_FEATURE_NODE_SUPPORT"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "JAVA_FEATURE_NODE_SUPPORT"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "WASM_FEATURE_NODE_SUPPORT"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "ASM_FEATURE_NODE_SUPPORT"),
}


def _generate(language: str, nodes: list[object]) -> str:
    module_name, class_name = TRANSPILERS[language]
    transpiler = getattr(importlib.import_module(module_name), class_name)()
    code = transpiler.generate_code(nodes)
    return "\n".join(code) if isinstance(code, list) else str(code)


def _feature_nodes(feature: str) -> list[object]:
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
                [NodoLlamadaFuncion("mostrar", [NodoIdentificador("error")])],
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
        "tipos_compuestos": [NodoLlamadaFuncion("longitud", [NodoLista([NodoValor("Ana"), NodoValor("Luis")])])],
    }
    return fixtures[feature]


def _contract_status(feature_id: str, backend: str) -> str:
    if feature_id in {"decoradores", "async", "tipos_compuestos"}:
        matrix_key = {
            "decoradores": "decoradores",
            "async": "async",
            "tipos_compuestos": "colecciones",
        }[feature_id]
        return AST_FEATURE_MINIMUM_CONTRACT[backend][matrix_key]
    matrix_key = {"imports_corelibs": "corelibs", "manejo_errores": "holobit"}[feature_id]
    return BACKEND_COMPATIBILITY[backend][matrix_key]


@pytest.mark.parametrize(
    "phase,expected",
    [
        ("fase_1", ("decoradores", "imports_corelibs")),
        ("fase_2", ("manejo_errores",)),
        ("fase_3", ("async", "tipos_compuestos")),
    ],
)
def test_language_equivalence_priority_phases_follow_contract(phase: str, expected: tuple[str, ...]):
    assert LANGUAGE_EQUIVALENCE_PRIORITY_PHASES[phase] == expected


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("feature", PRIORITY_FEATURES)
def test_feature_node_mapping_is_explicit_and_synchronized_across_matrix_and_transpiler_modules(
    backend: str, feature: str
):
    matrix_mapping = BACKEND_FEATURE_NODE_SUPPORT[backend][feature]

    module_name, constant_name = TRANSPILER_FEATURE_CONSTANTS[backend]
    transpiler_mapping = getattr(importlib.import_module(module_name), constant_name)[feature]
    assert transpiler_mapping == matrix_mapping


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("feature", PRIORITY_FEATURES)
def test_priority_features_have_minimal_expected_backend_behavior(backend: str, feature: str):
    status = _contract_status(feature, backend)
    mapped_nodes = BACKEND_FEATURE_NODE_SUPPORT[backend][feature]

    if not mapped_nodes:
        assert status in {"none", "partial"}
        return

    generated = _generate(backend, _feature_nodes(feature))
    assert generated.strip(), f"{backend} no generó salida para {feature}"

    assert status in {"full", "partial", "none"}
