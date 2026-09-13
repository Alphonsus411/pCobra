"""Caracterización del bloqueo normativo de ``desde ... usar ...``."""

import ast
import shutil
import subprocess

import pytest

from pcobra.cobra.core import Lexer, Parser, ParserError, TipoToken
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.core.ast_nodes import NodoImportDesde


FUENTE_COBRA = 'desde "paquete" usar simbolo como alias'
RAMA_LEGADA_NO_PUBLICA = 'desde "paquete" import simbolo como alias'


def _parsear(codigo: str):
    return Parser(Lexer(codigo).analizar_token()).parsear()


def test_desde_usar_llega_al_parser_con_los_tokens_existentes():
    tokens = Lexer(FUENTE_COBRA).analizar_token()

    assert [token.tipo for token in tokens] == [
        TipoToken.DESDE,
        TipoToken.CADENA,
        TipoToken.USAR,
        TipoToken.IDENTIFICADOR,
        TipoToken.COMO,
        TipoToken.IDENTIFICADOR,
        TipoToken.EOF,
    ]


@pytest.mark.parametrize("target", ["python", "javascript", "rust"])
def test_desde_usar_esta_bloqueado_antes_de_los_backends(target):
    """Los tres targets quedan inaccesibles sin cambiar la gramática."""
    with pytest.raises(ParserError, match="Se esperaba 'import' después de 'desde'"):
        _parsear(FUENTE_COBRA)


def test_rama_legada_preserva_nodo_y_emite_los_tres_backends(tmp_path):
    """Traza la rama existente sin declararla sintaxis pública Cobra."""
    nodos = _parsear(RAMA_LEGADA_NO_PUBLICA)

    assert len(nodos) == 1
    nodo = nodos[0]
    assert isinstance(nodo, NodoImportDesde)
    assert (nodo.modulo, nodo.nombre, nodo.alias) == (
        "paquete",
        "simbolo",
        "alias",
    )

    python = TranspiladorPython().generate_code(nodos)
    javascript = TranspiladorJavaScript().generate_code(nodos)
    rust = TranspiladorRust().generate_code(nodos)

    assert "from paquete import simbolo as alias" in python
    assert "import { simbolo as alias } from 'paquete';" in javascript
    assert "use paquete::simbolo as alias;" in rust
    ast.parse(python)

    if node := shutil.which("node"):
        destino_js = tmp_path / "salida.mjs"
        destino_js.write_text(javascript, encoding="utf-8")
        subprocess.run([node, "--check", str(destino_js)], check=True)

    if rustc := shutil.which("rustc"):
        destino_rs = tmp_path / "salida.rs"
        destino_rs.write_text(
            "mod paquete { pub fn simbolo() {} }\n"
            "use paquete::simbolo as alias;\n"
            "fn main() { alias(); }\n",
            encoding="utf-8",
        )
        subprocess.run(
            [rustc, str(destino_rs), "-o", str(tmp_path / "salida")],
            check=True,
        )
