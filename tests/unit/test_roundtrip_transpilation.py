from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import pytest

from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.reverse.from_python import ReverseFromPython
from cobra.transpilers.reverse.from_js import ReverseFromJS
from cobra.transpilers.import_helper import get_standard_imports
from core.ast_nodes import (
    NodoAsignacion,
    NodoCase,
    NodoIdentificador,
    NodoOption,
    NodoPattern,
    NodoSwitch,
    NodoValor,
)

SNAPSHOT_DIR = Path("tests/data/roundtrip_snapshots")


def _normalize_ast(value: Any) -> Any:
    if is_dataclass(value):
        return _normalize_ast(asdict(value))
    if isinstance(value, dict):
        return {k: _normalize_ast(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_normalize_ast(v) for v in value]
    return value


def _strip_standard_imports(code: str, target: str) -> str:
    imports = get_standard_imports(target) or ""
    if imports and code.startswith(imports):
        code = code[len(imports):]
    return code.lstrip("\n")


def test_roundtrip_cobra_python_cobra_ast_equivalente_snapshot():
    ast_cobra = [
        NodoAsignacion("x", NodoValor(1)),
        NodoAsignacion("mensaje", NodoValor("hola")),
    ]

    codigo_python = TranspiladorPython().generate_code(ast_cobra)
    codigo_intermedio = _strip_standard_imports(codigo_python, "python")

    expected_snapshot = (SNAPSHOT_DIR / "python_intermediate.py.snap").read_text(encoding="utf-8")
    assert codigo_intermedio == expected_snapshot

    ast_reconstruido = ReverseFromPython().generate_ast(codigo_intermedio)
    assert _normalize_ast(ast_reconstruido) == _normalize_ast(ast_cobra)


@pytest.mark.skipif(not hasattr(ReverseFromJS, "generate_ast"), reason="Reverse JS no disponible")
def test_roundtrip_cobra_js_cobra_ast_equivalente_snapshot():
    try:
        reverse = ReverseFromJS()
    except NotImplementedError:
        pytest.skip("tree-sitter JS no disponible")

    ast_cobra = [
        NodoAsignacion("a", NodoOption(None)),
        NodoSwitch(
            NodoIdentificador("a"),
            [
                NodoCase(
                    NodoPattern(NodoValor(1)),
                    [NodoAsignacion("y_local", NodoValor(1))],
                )
            ],
            [NodoAsignacion("y_local", NodoValor(0))],
        ),
    ]

    codigo_js = TranspiladorJavaScript().generate_code(ast_cobra)
    codigo_intermedio = _strip_standard_imports(codigo_js, "javascript")

    expected_snapshot = (SNAPSHOT_DIR / "javascript_intermediate.js.snap").read_text(encoding="utf-8")
    assert codigo_intermedio == expected_snapshot

    ast_reconstruido = reverse.generate_ast(codigo_intermedio)
    assert _normalize_ast(ast_reconstruido) == _normalize_ast(ast_cobra)
