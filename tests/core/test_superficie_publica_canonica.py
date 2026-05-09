from __future__ import annotations

import ast
from pathlib import Path

import pytest

from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    REPL_COBRA_MODULE_INTERNAL_PATH_MAP,
    USAR_RUNTIME_EXPORT_OVERRIDES,
)

PROHIBIDOS = {"self", "append", "map", "filter", "unwrap", "expect"}
RAIZ_REPO = Path(__file__).resolve().parents[2]


def _nombres_publicos(path_modulo: Path) -> list[str]:
    arbol = ast.parse(path_modulo.read_text(encoding="utf-8"))
    simbolos: dict[str, list[str]] = {}

    for nodo in arbol.body:
        destinos = []
        valor = None
        if isinstance(nodo, ast.Assign):
            destinos = [d for d in nodo.targets if isinstance(d, ast.Name)]
            valor = nodo.value
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            destinos = [nodo.target]
            valor = nodo.value

        if not destinos or valor is None:
            continue

        for destino in destinos:
            nombre = destino.id
            if isinstance(valor, (ast.List, ast.Tuple)):
                simbolos[nombre] = [
                    x.value for x in valor.elts if isinstance(x, ast.Constant) and isinstance(x.value, str)
                ]
            elif isinstance(valor, ast.Call) and isinstance(valor.func, ast.Name) and valor.func.id == "list":
                arg = valor.args[0] if valor.args else None
                if isinstance(arg, ast.Name) and arg.id in simbolos:
                    simbolos[nombre] = list(simbolos[arg.id])

    if "__all__" not in simbolos:
        raise AssertionError(f"{path_modulo} no define __all__")
    return simbolos["__all__"]


def _simbolos_definidos_modulo(path_modulo: Path) -> set[str]:
    arbol = ast.parse(path_modulo.read_text(encoding="utf-8"))
    definidos = {nodo.name for nodo in arbol.body if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign):
            for destino in nodo.targets:
                if isinstance(destino, ast.Name):
                    definidos.add(destino.id)
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            definidos.add(nodo.target.id)
    return definidos


@pytest.mark.parametrize("modulo", tuple(CANONICAL_MODULE_SURFACE_CONTRACTS.keys()))
def test_superficie_publica_solo_espanol_y_sin_prohibidos(modulo: str):
    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[modulo]
    ruta_modulo = RAIZ_REPO / ruta_relativa
    publicos = _nombres_publicos(ruta_modulo)

    assert publicos, f"{modulo} debe exportar al menos un símbolo"
    assert all("__" not in nombre for nombre in publicos)
    assert PROHIBIDOS.isdisjoint(publicos)


@pytest.mark.parametrize("modulo, contrato", tuple(CANONICAL_MODULE_SURFACE_CONTRACTS.items()))
def test_superficie_canonia_requiere_funciones_minimas(modulo: str, contrato):
    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[modulo]
    ruta_modulo = RAIZ_REPO / ruta_relativa
    funciones = _simbolos_definidos_modulo(ruta_modulo)
    publicos = set(_nombres_publicos(ruta_modulo))

    for nombre in contrato.required_functions:
        assert nombre in funciones, f"{modulo} debe implementar {nombre}"
        assert nombre in publicos, f"{modulo} debe exportar {nombre} en __all__"


@pytest.mark.parametrize("modulo, aliases", tuple((m, c.allowed_aliases) for m, c in CANONICAL_MODULE_SURFACE_CONTRACTS.items()))
def test_aliases_controlados_por_contrato(modulo: str, aliases: dict[str, str]):
    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[modulo]
    ruta_modulo = RAIZ_REPO / ruta_relativa
    publicos = set(_nombres_publicos(ruta_modulo))

    for alias, destino in aliases.items():
        assert alias in publicos, f"{modulo} debe exportar alias permitido {alias}"
        assert destino in publicos, f"{modulo} debe exportar destino canónico {destino}"


@pytest.mark.parametrize("modulo, exportes", tuple(USAR_RUNTIME_EXPORT_OVERRIDES.items()))
def test_override_runtime_sin_simbolos_prohibidos(modulo: str, exportes: tuple[str, ...]):
    assert all("__" not in nombre for nombre in exportes)
    assert PROHIBIDOS.isdisjoint(exportes)
