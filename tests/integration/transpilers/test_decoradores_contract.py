from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import AST_FEATURE_MINIMUM_CONTRACT
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.core.ast_nodes import NodoFuncion, NodoIdentificador, NodoRetorno, NodoValor
from tests.integration.transpilers.backend_contracts import TRANSPILERS

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "decoradores"
LANGUAGE_EQUIVALENCE = Path(__file__).resolve().parents[3] / "data" / "language_equivalence.yml"

EXPECTED_DECORATORS = {
    "memoizar",
    "orden_total",
    "despachar_por_tipo",
    "depreciado",
    "sincronizar",
    "reintentar",
    "reintentar_async",
    "dataclase",
    "temporizar",
}


def _generate(backend: str, decorator_name: str) -> str:
    module_name, class_name = TRANSPILERS[backend]
    transpiler = getattr(importlib.import_module(module_name), class_name)()
    nodes = [
        NodoFuncion(
            f"usar_{decorator_name}",
            ["valor"],
            [NodoRetorno(NodoValor("ok"))],
            decoradores=[NodoIdentificador(decorator_name)],
        )
    ]
    output = transpiler.generate_code(nodes)
    return "\n".join(output) if isinstance(output, list) else str(output)


def test_fixtures_decoradores_cubren_todo_el_inventario_decoradores():
    found = {path.stem for path in FIXTURES_DIR.glob("*.cobra")}
    assert found == EXPECTED_DECORATORS


@pytest.mark.parametrize("decorator_name", sorted(EXPECTED_DECORATORS))
def test_fixture_cada_decorador_tiene_sintaxis_basica_de_decorador(decorator_name: str):
    fixture = (FIXTURES_DIR / f"{decorator_name}.cobra").read_text(encoding="utf-8")
    assert fixture.lstrip().startswith("@")
    assert decorator_name in fixture


@pytest.mark.parametrize("decorator_name", sorted(EXPECTED_DECORATORS))
@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_matriz_decoradores_por_backend_esta_declarada_y_alineada_con_contrato_ast(
    decorator_name: str, backend: str
):
    expected = AST_FEATURE_MINIMUM_CONTRACT[backend]["decoradores"]
    raw_equivalence = LANGUAGE_EQUIVALENCE.read_text(encoding="utf-8")
    assert "decorator_support:" in raw_equivalence
    assert f"      {decorator_name}:" in raw_equivalence
    assert f"        {backend}: {expected}" in raw_equivalence


@pytest.mark.parametrize("decorator_name", sorted(EXPECTED_DECORATORS))
@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_fixture_decorador_genera_salida_para_todos_los_backends(backend: str, decorator_name: str):
    generated = _generate(backend, decorator_name)
    assert generated.strip(), f"{backend} no generó salida para {decorator_name}"
