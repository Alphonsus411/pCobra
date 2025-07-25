import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend" / "src"))
sys.path.insert(0, str(ROOT))
import core.visitor as _vis
sys.modules.setdefault("backend.src.core.visitor", _vis)
sys.modules.setdefault("backend.src.core", sys.modules.get("core"))

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import (
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoWith,
    NodoPasar,
    NodoIdentificador,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_parser_del():
    ast = Parser(Lexer("eliminar x").analizar_token()).parsear()
    assert isinstance(ast[0], NodoDel)
    assert isinstance(ast[0].objetivo, NodoIdentificador)
    assert ast[0].objetivo.nombre == "x"


def test_parser_global():
    ast = Parser(Lexer("global a, b").analizar_token()).parsear()
    assert isinstance(ast[0], NodoGlobal)
    assert ast[0].nombres == ["a", "b"]


def test_parser_nolocal():
    ast = Parser(Lexer("nolocal c").analizar_token()).parsear()
    assert isinstance(ast[0], NodoNoLocal)
    assert ast[0].nombres == ["c"]


def test_parser_with():
    code = "con recurso como r: pasar fin"
    ast = Parser(Lexer(code).analizar_token()).parsear()
    assert isinstance(ast[0], NodoWith)
    assert isinstance(ast[0].contexto, NodoIdentificador)
    assert ast[0].contexto.nombre == "recurso"
    assert ast[0].alias == "r"
    assert len(ast[0].cuerpo) == 1 and isinstance(ast[0].cuerpo[0], NodoPasar)


def test_transpilar_del():
    nodo = NodoDel(NodoIdentificador("x"))
    codigo = TranspiladorPython().generate_code([nodo])
    assert codigo == IMPORTS + "del x\n"


def test_transpilar_global():
    nodo = NodoGlobal(["a", "b"])
    codigo = TranspiladorPython().generate_code([nodo])
    assert codigo == IMPORTS + "global a, b\n"


def test_transpilar_nolocal():
    nodo = NodoNoLocal(["c"])
    codigo = TranspiladorPython().generate_code([nodo])
    assert codigo == IMPORTS + "nonlocal c\n"


def test_transpilar_with():
    nodo = NodoWith(NodoIdentificador("recurso"), "r", [NodoPasar()])
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = IMPORTS + "with recurso as r:\n    pass\n"
    assert codigo == esperado


def test_parser_del_sin_expresion():
    with pytest.raises(SyntaxError):
        Parser(Lexer("eliminar").analizar_token()).parsear()


def test_parser_global_sin_identificadores():
    with pytest.raises(SyntaxError):
        Parser(Lexer("global").analizar_token()).parsear()


def test_parser_con_sin_fin():
    with pytest.raises(SyntaxError):
        Parser(Lexer("con x:").analizar_token()).parsear()
