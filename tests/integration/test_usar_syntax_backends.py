"""Caracterización de ``usar`` desde fuente Cobra hasta backends oficiales."""

from __future__ import annotations

import ast
import shutil
import subprocess

import pytest

from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.backends.rust_adapter import RustAdapter
from pcobra.cobra.core import Lexer, Parser, ParserError
from pcobra.core.ast_nodes import NodoUsar


def _parsear_fuente(codigo: str) -> list:
    return Parser(Lexer(codigo).tokenizar()).parsear()


@pytest.mark.parametrize(
    ("fuente", "modulo"),
    [
        ('usar "texto"', "texto"),
        ('usar "utilidades.fechas"', "utilidades.fechas"),
        ("usar utilidades.fechas", "utilidades.fechas"),
    ],
)
def test_usar_desde_fuente_caracteriza_formas_aceptadas(fuente, modulo):
    nodos = _parsear_fuente(fuente)

    assert nodos == [NodoUsar(modulo)]


def test_usar_identificador_simple_sin_comillas_es_rechazado():
    with pytest.raises(ParserError, match="Un solo identificador sin comillas"):
        _parsear_fuente("usar texto")


def test_usar_misma_fuente_transpila_por_adaptadores_oficiales(tmp_path):
    nodos = _parsear_fuente('usar "texto"')

    python = PythonAdapter().compile(nodos)
    javascript = JavaScriptAdapter().compile(nodos)
    rust = RustAdapter().compile(nodos)

    assert "usar_modulo('texto', safe_mode=True)" in python
    assert "// usar texto" in javascript
    assert "// usar texto" in rust

    ast.parse(python)

    node = shutil.which("node")
    if node is not None:
        salida_js = tmp_path / "usar.js"
        salida_js.write_text(javascript, encoding="utf-8")
        subprocess.run([node, "--check", str(salida_js)], check=True)

    rustc = shutil.which("rustc")
    if rustc is not None:
        salida_rs = tmp_path / "usar.rs"
        # El backend emite imports contractuales del runtime; stubs locales
        # permiten que rustc compruebe la unidad aislada sin enlazar ese runtime.
        salida_rs.write_text(
            "mod corelibs {}\nmod standard_library {}\n" + rust,
            encoding="utf-8",
        )
        subprocess.run(
            [rustc, "--crate-type", "lib", str(salida_rs)],
            check=True,
            cwd=tmp_path,
        )
