import pytest
from pygments import lex
from pygments.token import Keyword, Name

from pcobra.cobra.cli.repl.cobra_lexer import CobraLexer


@pytest.mark.parametrize("source", ["elseif", "sino si"])
def test_repl_lexer_follows_sino_si_keyword_contract(source):
    tokens = [(token, value) for token, value in lex(source, CobraLexer()) if value.strip()]

    assert tokens == [(Keyword, source)]


@pytest.mark.parametrize(
    ("source", "expected_token"),
    [
        ("con", Keyword),
        ("como", Keyword),
        ("with", Name),
        ("as", Name),
    ],
)
def test_repl_lexer_follows_con_como_keyword_contract(source, expected_token):
    tokens = [(token, value) for token, value in lex(source, CobraLexer()) if value.strip()]

    assert tokens == [(expected_token, source)]


@pytest.mark.parametrize(
    ("source", "expected_token"),
    [
        ("rasgo", Keyword),
        ("interface", Keyword),
        ("trait", Name),
        ("interfaz", Name),
    ],
)
def test_repl_lexer_follows_interface_keyword_contract(source, expected_token):
    tokens = [(token, value) for token, value in lex(source, CobraLexer()) if value.strip()]

    assert tokens == [(expected_token, source)]


@pytest.mark.parametrize("source", ["guard", "garantia"])
def test_repl_lexer_follows_garantia_keyword_contract(source):
    tokens = [(token, value) for token, value in lex(source, CobraLexer()) if value.strip()]

    assert tokens == [(Keyword, source)]


@pytest.mark.parametrize(
    ("source", "expected_token"),
    [
        ("enumeracion", Keyword),
        ("enum", Keyword),
        ("enumerador", Name),
    ],
)
def test_repl_lexer_follows_enum_keyword_contract(source, expected_token):
    tokens = [(token, value) for token, value in lex(source, CobraLexer()) if value.strip()]

    assert tokens == [(expected_token, source)]
