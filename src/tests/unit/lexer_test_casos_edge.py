import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest
from cobra.core import (
    Lexer,
    TipoToken,
    InvalidTokenError,
    UnclosedStringError,
)


def test_cadena_sin_cerrar():
    lexer = Lexer("'hola")
    with pytest.raises(UnclosedStringError):
        lexer.tokenizar()


def test_caracter_no_valido():
    codigo = 'var x = \u20AC'
    lexer = Lexer(codigo)
    with pytest.raises(InvalidTokenError):
        lexer.tokenizar()


def test_literal_extremo():
    codigo = '999999999999999999'
    tokens = Lexer(codigo).analizar_token()
    assert tokens[0].tipo == TipoToken.ENTERO
    assert tokens[0].valor == 999999999999999999
    assert tokens[-1].tipo == TipoToken.EOF


def test_cadena_con_escape():
    codigo = r"'hola\\nmundo'"
    tokens = Lexer(codigo).analizar_token()
    assert tokens[0].tipo == TipoToken.CADENA
    assert tokens[0].valor == "hola\\nmundo"
    assert tokens[-1].tipo == TipoToken.EOF


def test_cadena_con_comillas_escapadas():
    codigo = '"dijo \\"hola\\""'
    tokens = Lexer(codigo).analizar_token()
    assert tokens[0].tipo == TipoToken.CADENA
    assert tokens[0].valor == 'dijo "hola"'
    assert tokens[-1].tipo == TipoToken.EOF
